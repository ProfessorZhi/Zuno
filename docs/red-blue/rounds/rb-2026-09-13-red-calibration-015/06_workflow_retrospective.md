# Workflow Retrospective — rb-2026-09-13-red-calibration-015

status: SUPERSEDED_BEFORE_BLUE

## User verdict

The first Red output was rejected during `USER_RED_REVIEW`. The user's reason was structural: the questions had technical content, but still felt like an engineering / architecture checklist rewritten into long interview questions. The user explicitly requested studying real interview experiences and improving the Red thinking framework before any Blue execution.

## What failed

The Round separated a 30-question Primary Path from 70 reserve questions and added ownership Kill Switches, but it still treated the live interview as a pre-generated question sequence. Several Primary questions bundled multiple intents such as mechanism, inputs, ranking rule, exception, test assertion, metric or trade-off into one turn.

That produces high coverage but weak conversational realism. The interviewer does not truly need to listen to the previous answer because most of the attack tree has already been materialized.

## Corrective action

A separate workflow PR changed the Red model to:

```text
100-question PRESSURE_SUITE for offline coverage
+
6–10 SPOKEN_SEEDS for opening threads
+
DYNAMIC answer-driven follow-up
+
ONE_QUESTION_ONE_INTENT
```

The new model treats Ownership / Build-Buy / failure / evidence / fundamentals as an interviewer mental map rather than text that must be packed into each spoken question. Kill Switches stay in Controller state. Actual Red Evaluation should score the conversation threads that occurred, not completion of the pressure bank.

The change was merged to main as `7e8e15cebceed52cabd45a3fc3bf1464176be95b` after Architecture/documentation and Current-code selected verification both passed.

## Round decision

No Blue answers, Red Evaluation or Blue Architecture Reflection were run. This round is preserved as a failed Red-calibration sample and marked `SUPERSEDED`. A new Round must be created from the updated main to test the new skill.
