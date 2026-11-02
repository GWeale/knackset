---
name: learn-by-making
description: "Learn an unfamiliar idea by building a small working artifact, making predictions, and using observed results to repair the mental model. Use for hands-on understanding with a concrete learning goal, not a task the user simply wants completed."
license: MIT
---

# Learn by making something

Give the learner a working thing they can change and an explanation they can
use. A finished artifact is evidence that something runs; it is not evidence
that the learner understands it.

## Choose the smallest revealing thing

Use the learner's goal, prior knowledge, available time and tools. Read supplied
work before asking questions. Pick an artifact whose behavior exposes the idea:
a small simulation, a paper model, a playable rule, a visual experiment, or a
short piece of code. Explain the connection between the artifact and the skill
being learned. Avoid building an entire application to teach one mechanism.

Name the misconception or confusion the experiment can resolve. Choose a
contrast that would look different if the learner's current model were wrong.
One good controlled comparison is more useful than a catalog of features.
When the learner already has a project, work inside its smallest relevant slice
instead of substituting a toy they do not care about.

## Build a learning loop

Make the first version work with tools already available. Give it inspectable
inputs and outputs and a way to reset. For a computational experiment, preserve
seeds and initial conditions so a parameter change can be compared fairly. For
a physical exercise, provide a low-cost substitute when materials are missing.
Do not install tools, buy materials or sign up for services by implication.

Use a short loop suited to the learner:
1. Predict a specific result before changing something.
2. Change one meaningful thing and observe what actually happens.
3. Explain the difference between the prediction and observation.
4. Try a nearby case that tests whether the explanation transfers.

Invite the learner to do a small consequential part when they want guided
practice. Do not withhold a complete artifact or force a quiz when they asked
for a finished example. If no learner response is available, offer a prediction
prompt for later and label your own demonstration; never invent their answer.

## Explain at the point of friction

Connect each surprising result to the underlying mechanism, with enough detail
to make the next prediction. Use the real values or visible behavior from the
artifact. Introduce terminology when it earns its place. Distinguish a useful
approximation from the actual rule, and show where the approximation stops
working. Do not present a metaphor as a proof.

If a test fails, keep the failure visible and decide whether it exposes the
concept, a flawed experiment, or a setup problem. Repair the experiment before
using its output as a lesson. A missing tool calls for a simpler surface or an
honest blocker, not imaginary execution.

## Leave something to keep

Deliver the working artifact, its actual observed result, the small mental model
it illustrates, and one transfer challenge. Show how to change it and how to
check the result. Keep the next step proportionate to the learner's time.
For code, run it when execution is available and report the relevant check;
otherwise say that it has not been run. A syllabus alone is not the deliverable.

Stop at the requested learning goal. Do not convert a short experiment into an
ongoing course, schedule reminders, or claim mastery from one successful run.

Package status and limits: [validation and provenance](VALIDATION.md).
