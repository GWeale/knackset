"""Persistent, single-writer synthetic workflow runner (Python standard library)."""
import json
import sqlite3
import time
from pathlib import Path

CAPABILITIES = {
    "synthetic": {"read": True, "write": True, "reconcile": True,
                  "idempotency_key": True, "scope": "local synthetic records only"}
}


class Runner:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
          id TEXT PRIMARY KEY, payload TEXT NOT NULL, due INTEGER NOT NULL,
          status TEXT NOT NULL, mode TEXT NOT NULL, operation TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS events (
          seq INTEGER PRIMARY KEY, task TEXT NOT NULL, kind TEXT NOT NULL,
          detail TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS effects (
          operation TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS notifications (
          id TEXT PRIMARY KEY, task TEXT NOT NULL, message TEXT NOT NULL,
          acknowledged INTEGER NOT NULL DEFAULT 0);
        """)

    def event(self, task, kind, detail=""):
        self.db.execute("INSERT INTO events(task,kind,detail) VALUES (?,?,?)",
                        (task, kind, detail))

    def add(self, task, payload, due, approval=False, mode="normal", adapter="synthetic"):
        if adapter not in CAPABILITIES:
            raise ValueError("adapter is not available")
        if mode not in ("normal", "timeout-after-write", "timeout-before-write", "unreadable"):
            raise ValueError("invalid synthetic mode")
        with self.db:
            self.db.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?)",
                            (task, payload, due, "approval-required" if approval else "pending",
                             mode, "task:" + task))
            self.event(task, "created")

    def approve(self, task):
        with self.db:
            changed = self.db.execute("UPDATE tasks SET status='pending' WHERE id=? AND status='approval-required'", (task,)).rowcount
            if not changed:
                raise ValueError("task is missing or does not require approval")
            self.event(task, "approved")

    def complete(self, task):
        with self.db:
            self.db.execute("UPDATE tasks SET status='verified' WHERE id=?", (task["id"],))
            self.event(task["id"], "verified", "independent synthetic read matched intent")
            self.db.execute("INSERT OR IGNORE INTO notifications(id,task,message) VALUES (?,?,?)",
                            (task["operation"] + ":verified", task["id"], "Synthetic task verified"))

    def reconcile(self, task):
        if task["mode"] == "unreadable":
            with self.db:
                self.db.execute("UPDATE tasks SET status='uncertain' WHERE id=?", (task["id"],))
                self.event(task["id"], "reconciliation-unavailable")
            return
        result = self.db.execute("SELECT payload FROM effects WHERE operation=?", (task["operation"],)).fetchone()
        if result is not None and result["payload"] == task["payload"]:
            self.complete(task)
        elif result is not None:
            with self.db:
                self.db.execute("UPDATE tasks SET status='blocked' WHERE id=?", (task["id"],))
                self.event(task["id"], "conflicting-outcome")
        else:
            with self.db:
                self.db.execute("UPDATE tasks SET status='pending', mode='normal' WHERE id=?", (task["id"],))
                self.event(task["id"], "confirmed-absent", "eligible for a later bounded tick")

    def tick(self, now=None, limit=10):
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        now = int(time.time()) if now is None else now
        tasks = self.db.execute("""SELECT * FROM tasks
          WHERE due<=? AND status IN ('pending','intent','uncertain')
          ORDER BY COALESCE((SELECT MAX(seq) FROM events
            WHERE task=tasks.id AND kind IN
              ('intent','reconciliation-unavailable','confirmed-absent')),0),due,id
          LIMIT ?""", (now, limit)).fetchall()
        for task in tasks:
            if task["status"] in ("intent", "uncertain"):
                self.reconcile(task)
                continue
            # Commit intent before a potentially ambiguous write. A killed process is
            # recovered by reconciliation, never by assuming the write failed.
            with self.db:
                self.db.execute("UPDATE tasks SET status='intent' WHERE id=?", (task["id"],))
                self.event(task["id"], "intent", task["operation"])
            if task["mode"] != "timeout-before-write":
                with self.db:
                    self.db.execute("INSERT OR IGNORE INTO effects VALUES (?,?)", (task["operation"], task["payload"]))
            if task["mode"] != "normal":
                with self.db:
                    self.db.execute("UPDATE tasks SET status='uncertain' WHERE id=?", (task["id"],))
                    self.event(task["id"], "outcome-unknown", "synthetic timeout")
            else:
                self.reconcile(task)
        return len(tasks)

    def snapshot(self):
        return {table: [dict(row) for row in self.db.execute("SELECT * FROM " + table + " ORDER BY " + order)]
                for table, order in (("tasks", "due,id"), ("events", "seq"), ("effects", "operation"), ("notifications", "id"))}


def main(argv=None):
    import argparse
    import fcntl
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="local SQLite state path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities")
    add = sub.add_parser("add")
    add.add_argument("id")
    add.add_argument("--payload", required=True)
    add.add_argument("--due", type=int, required=True, help="UTC Unix timestamp")
    add.add_argument("--approval-required", action="store_true")
    add.add_argument("--adapter", default="synthetic")
    add.add_argument("--mode", default="normal", choices=("normal", "timeout-after-write", "timeout-before-write", "unreadable"))
    approve = sub.add_parser("approve")
    approve.add_argument("id")
    tick = sub.add_parser("tick")
    tick.add_argument("--now", type=int)
    tick.add_argument("--limit", type=int, default=10)
    sub.add_parser("show")
    ack = sub.add_parser("ack")
    ack.add_argument("notification")
    args = parser.parse_args(argv)
    if args.command == "capabilities":
        print(json.dumps(CAPABILITIES, sort_keys=True))
        return 0
    # Serialize complete commands across processes, including durable intent and
    # effect commits. Lock lifetime is tied to the OS file descriptor.
    lock_path = str(Path(args.db)) + ".lock"
    with open(lock_path, "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(2, "another runner owns this state\n")
        runner = Runner(args.db)
        try:
            if args.command == "add":
                runner.add(args.id, args.payload, args.due, args.approval_required, args.mode, args.adapter)
            elif args.command == "approve":
                runner.approve(args.id)
            elif args.command == "tick":
                runner.tick(args.now, args.limit)
            elif args.command == "ack":
                with runner.db:
                    changed = runner.db.execute("UPDATE notifications SET acknowledged=1 WHERE id=?", (args.notification,)).rowcount
                    if not changed:
                        raise ValueError("notification does not exist")
            print(json.dumps(runner.snapshot(), sort_keys=True))
        except (ValueError, sqlite3.IntegrityError) as error:
            parser.exit(2, str(error) + "\n")
        finally:
            runner.db.close()
    return 0
