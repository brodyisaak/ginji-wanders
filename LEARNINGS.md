# learnings

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
