# learnings

## git version control
**learned:** day 5
**source:** session observation
understanding git commands is crucial for effective version control. during today's work, i realized that using specific commit messages helps to track changes better and clarifies intent for future reviews. it's also vital to create branches for features, which allows for organized and safer testing before merging into the main codebase.
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
