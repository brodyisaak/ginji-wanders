# incident runbook

## purpose

provide fast triage and recovery for broken autonomous sessions.

## system boundaries

incident classes:
- build failures
- workflow failures
- journal/learnings integrity failures
- issue processing failures
- site generation or publication failures

## triage flow

1. classify incident by first failed stage in logs.
2. capture exact command output and failing file.
3. determine whether failure is code, environment, or credential related.
4. apply minimal recovery action.
5. re-run validations.
6. publish postmortem note in journal/learnings when appropriate.

## common incidents and response

### build fails in step 0

diagnostics:
```bash
python -m py_compile src/ginji.py
python -m pytest tests/ -q
```
recovery:
- restore last known-good `src/` and `tests/`.
- apply smallest fix and rerun checks.

### evolution posts more than once in a day

diagnostics:
```bash
cat LAST_POST_DATE_PST
rg -n "LAST_POST_DATE_PST|TZ=America/Los_Angeles" scripts/evolve.sh
```
recovery:
- restore pacific-date guard logic.
- set `LAST_POST_DATE_PST` correctly and rerun next day.

### journal history missing

diagnostics:
```bash
git log -- JOURNAL.md --oneline
```
recovery:
- restore missing entries from prior commits.
- ensure prepend logic is used, not overwrite logic.

### issue response failures

diagnostics:
```bash
gh auth status
cat ISSUE_RESPONSE.md
```
recovery:
- skip issue posting when auth is invalid.
- keep core build and publish path healthy.

## how to verify

- ci and evolution workflows return green.
- site reflects latest journal and stable day count.
- state files satisfy invariants in [state files](./state-files.md).

## related pages

- [evolution pipeline](./evolution-pipeline.md)
- [github actions and scheduling](./github-actions-and-scheduling.md)
- [maintainer playbook local ops](./maintainer-playbook-local-ops.md)
