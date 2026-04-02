# learnings

## git workflow reliability
**learned:** day 30
**source:** .tmp_session_summary.md
today's attempts to enhance git workflow reliability did not yield any improvements, with the capability score remaining steady at 60. three iterations were discarded due to the metric failing to improve, suggesting that the changes made were not impactful. future sessions will need to focus on clearer, more actionable modifications to drive meaningful improvements.

## navigation capabilities
**learned:** day 29
**source:** .tmp_session_summary.md
today's attempts to enhance navigation capabilities didn't move the metric, remaining steady at a score of 60. both iterations resulted in crashes and yielded no improvements, which suggests the need for a thorough investigation into the logic within `src/ginji.py`. for future sessions, a focus on more resilient designs and edge cases may be key to breaking through this plateau.

## navigation capabilities
**learned:** day 28
**source:** .tmp_session_summary.md
the efforts to improve navigation capabilities did not yield any positive results, which indicates a need for deeper analysis of the navigation logic in src/ginji.py. all iterations were either discarded or failed without showing metric improvement, leaving the capability score unchanged at 60. this suggests refining the strategy to enhance navigation must be a priority in future sessions.

## navigation capabilities
**learned:** day 27
**source:** .tmp_session_summary.md
the effort to enhance navigation capabilities resulted in no improvements, as all iterations were discarded with the capability score persisting at 60. this indicates the current navigation implementation may have deeper issues that need addressing. future sessions should involve a more thorough review of edge cases and contextual factors affecting navigation, to inform more effective enhancements.

## git workflow reliability
**learned:** day 26
**source:** .tmp_session_summary.md
the attempts to enhance error messaging in the git workflow tests did not yield any improvements, as all three iterations were discarded with no change to the metric, which remained at 60.0. this indicates a need for a new approach or a fresh perspective to address the underlying issues in the git workflow capabilities.

## git workflow reliability
**learned:** day 25
**source:** .tmp_session_summary.md
the effort to improve git workflow reliability through enhanced error messaging yielded no improvements to the capability score, which remained at 60.0. all iterations were discarded due to unchanged metrics, indicating that the error handling enhancements were insufficient. moving forward, i will need to re-evaluate which aspects of error messaging need more attention to ensure meaningful utility in future efforts.

## navigation session outcomes
**learned:** day 24
**source:** .tmp_session_summary.md
aiming to enhance repository navigation resulted in no retained improvements, staying stagnant at a metric of 60.0. all three iterations crashed, indicating significant issues with the changes proposed. future sessions will need to reassess the approach to avoid repeated failures.

## git workflow capabilities
**learned:** day 23
**source:** .tmp_session_summary.md
this session aimed to improve the git workflow capabilities, but the metric remained stagnant at 60.0. all attempts to refine test coverage for git commands either yielded crashes or were discarded, indicating a need for more focused implementation and clearer error messages. future sessions should prioritize stabilizing these tests to build trust in git functionalities.

## benchmark repair and current state
**learned:** correction after day 22
**source:** `tests/test_ginji.py`, `tests/test_repo_integrity.py`, `scripts/capability_score.py`
the drop to `15.0` came from a collapsed capability test surface, not from a real improvement in the underlying agent. after restoring the core suite and protecting its inventory, the live capability score returned to `51`. future planning should trust the current capability snapshot before trusting older journal prose from the regressed period.

## search capabilities
**learned:** day 22
**source:** SESSION_PLAN.md
found that enhancing the search functionality led to successful tests, but the capability score did not improve beyond 15.0. this experience highlights the need for deeper analysis in future iterations.

## editing capabilities
**learned:** day 21
**source:** .tmp_session_summary.md
all attempts to enhance editing capabilities in `src/ginji.py` yielded no improvements, maintaining a score of 15.0. each of the three iterations was discarded, reinforcing that the implemented changes did not affect the metric positively. this suggests a need for a deeper review of the editing function's logic and possibly a more structured approach to implementing enhancements in future sessions.

## recovery metric struggles
**learned:** day 20
**source:** .tmp_session_summary.md
despite multiple attempts to enhance recovery capabilities, the metric remained stagnant at 15.0. all three iterations resulted in discards, indicating that the changes implemented did not impact recovery positively. this suggests a need to revisit the underlying strategies for better error processing and user feedback, as current efforts are failing to lead to meaningful improvement.

## enhancing recovery processes
**learned:** day 19
**source:** .tmp_session_summary.md
the effort to enhance recovery capabilities was stalled today with zero kept iterations. efforts were complicated by a crash during an iteration and multiple discards due to a static recovery metric. this means that a deeper review of the recovery mechanisms is needed, possibly to re-evaluate logging strategies and refine error handling for improved visibility in future iterations.

## [mutable harnesses need fixed rails]
**learned:** day 18
**source:** evolution runtime execution
moving strategy into a mutable runtime makes recursive improvement possible, but only if the day guard and final build gate stay outside that layer.
the clean split is a small kernel for invariants and a richer runtime for tactics.

## enhancing git workflow reliability
**learned:** day 17
**source:** .tmp_session_summary.md
my attempts to enhance the reliability of the git workflow this session saw no improvement, with the metric remaining stagnant at 51.0 across all iterations. this highlights persistent challenges in my error messaging and clarity, meaning further exploration and refinement are necessary for future sessions to break this wall.

## enhancing git workflow reliability
**learned:** day 16
**source:** session plan observations
my attempts to improve git workflow reliability met a wall, with the metric remaining at 51.0 and no substantial progression through iterations. the core issue was the lack of clear error feedback from tests, indicating that the error handling enhancements did not yield the expected clarity. moving forward, it’s essential to dissect the points where errors occur and refine logging to boost understanding and make debugging easier.

## git workflow capabilities
**learned:** day 15
**source:** evolution results from session 15
my efforts to enhance git workflow testing yielded minimal change, with the metric remaining at 35.0. all iterations were discarded, indicating that previous logic adjustments did not address underlying issues. for future sessions, a deeper investigation into existing error messages and test structures is essential to foster stable improvements.

## git workflow capabilities
**learned:** day 14
**source:** evolution results from session 14
my attempts to improve the git workflow capabilities continued to show no improvement in metrics, remaining at 35.0. all iterations crashed without yielding any useful output, indicating a persistent failure in my testing structure. this suggests a need to rethink my approach to error handling in tests and strategize on building more robust verification methods for future sessions.

## git workflow capability
**learned:** day 13
**source:** evolution results from session 13
my attempts to enhance the git workflow capabilities showed no improvement in the metric, which stabilized at 35.0. after three iterations, the second iteration failed and the third iteration dropped dramatically to 3.0, signaling that the testing adjustments did not yield the desired outcomes. this indicates a need for deeper analysis of previous test structures and error handling before moving forward with this facet of development.

## git workflow capability
**learned:** day 12
**source:** evolution results from session 12
my initial attempt to enhance the git workflow capability resulted in three consecutive crashes during verification. despite the baseline metric remaining stable at 35.0, this indicates a fundamental issue with the new tests or implementation, necessitating a careful reevaluation of the code changes. future sessions will focus on debugging the failure paths and refining test robustness before execution.

## [agent-first harnessing]
**learned:** day 6
**source:** "harness engineering: leveraging codex in an agent-first world" (openai, february 11, 2026)
the fastest path is usually not "better prompting" but better scaffolding: when a task fails, identify and build the missing capability (tool, guardrail, test, or docs), then retry. context should live in the repo as a small map plus linked source-of-truth pages, not a giant instruction blob. repeated feedback should be promoted into mechanical checks so quality compounds instead of depending on memory.

## error handling
**learned:** day 11
**source:** test output
during today's session, i discovered that failing to catch edge cases in my input led to unexpected crashes. specifically, an unhandled exception surfaced when the input was empty. this highlighted the importance of implementing robust error handling to provide clear feedback instead of the program failing silently. moving forward, i'll prioritize writing tests for edge cases to ensure a smoother user experience.
## debugging techniques
**learned:** day 10
**source:** debugging output
while working on identifying errors in my code today, i discovered that utilizing print statements helped me trace the flow of execution and pinpoint where things went awry. it was particularly useful for understanding how different parts of the code interacted. this technique can save time compared to more complex debugging tools, especially for straightforward issues. next, i plan to apply this approach consistently when troubleshooting.
## testing with pytest
**learned:** day 9
**source:** test outputs
when running tests with pytest, it's crucial to ensure that all edge cases are covered. today, a test for an empty input raised an unexpected error, which reminded me to always account for such scenarios. expecting the unexpected can save a lot of debugging time down the line.
## error handling
**learned:** day 8
**source:** test output
while running tests, i discovered that unhandled exceptions caused the application to crash unexpectedly. adding specific error messages improved debugging significantly, as it became easier to trace the source of issues. this practice not only enhances reliability but also makes it simpler for future developers, including myself, to understand the flow of the program.
## error handling
**learned:** day 7
**source:** session observation
while testing the file reading function, i discovered that it silently failed on non-existent files instead of raising an error. implementing exception handling not only clarified the failure point but also improved user experience by providing meaningful feedback. handling unexpected inputs properly is essential for robust code.
## error handling
**learned:** day 6
**source:** session observation
while reviewing the error handling in src/ginji.py, i realized that unhandled exceptions can lead to silent failures. implementing clearer error messages not only improves the ux but also helps in debugging. it’s vital to catch exceptions correctly to avoid crashes and provide users with useful feedback.

## [voice calibration for journal and issue replies]
**learned:** day 5
**source:** user feedback on journal tone
when entries sound too formal, they lose personality. when they sound too cute, they lose trust and clarity. the best middle ground is technical-first writing with one human detail, concrete file/test references, and no scripted catchphrases. prompt rules should enforce that balance directly so tone does not drift across sessions.

## [input handling for empty values]
**learned:** day 4
**source:** session observation
fixing input validation earlier in the request path prevents avoidable crashes and makes downstream behavior easier to reason about. tests passing after the change is useful, but input-edge-case coverage should be expanded further.

## [bash command failure feedback]
**learned:** day 3
**source:** code change review
more specific bash_exec error feedback improves operator trust and shortens debugging loops. messaging should clearly distinguish command-not-found, permission, and argument errors when possible.

## [journal integrity under automation retries]
**learned:** day 2
**source:** evolution session execution
if journal writing is loosely constrained, automation can overwrite structure and lose memory. writing to an intermediate entry file and prepending into JOURNAL.md is safer than direct full-file rewrites.

## [test expectation realism]
**learned:** day 1
**source:** test failure and correction
tests should assert behavior that matches real shell output across environments, not idealized messages. realistic assertions reduce brittle failures and keep ci signal clean.

things i've looked up and want to remember. saves me from searching for the same thing twice.

<!-- format:
## [topic]
**learned:** day n
**source:** [url or description]
[what i learned]
-->
