# Execution deviations

- Unstick Project baseline: initial native turn returned “Selected model is at capacity. Please try a different model.” before a completed artifact result. The same lane was retried with unchanged provider/model/settings, task, input snapshot and output directory. No model switch occurred. This is a retained setup failure, not a scored task completion.
- The seeded plan randomizes variant order within each pair. Different cases overlap, and second variants start when their own preceding variant finishes rather than waiting for a global wave boundary. No elapsed-time comparison is made.
- One pair per case is an exploratory artifact pilot, not the repository's five-repeat sandbox comparison protocol. No general efficacy, statistical, speed or cost claim is made.
- All agents share an owner checkout but are instructed to read only assigned inputs and skill treatment and write only their separate output directory. This is instructed isolation, not enforced filesystem isolation.
