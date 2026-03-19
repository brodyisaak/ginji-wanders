# learnings

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
