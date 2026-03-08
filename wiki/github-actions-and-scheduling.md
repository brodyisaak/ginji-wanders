# github actions and scheduling

## purpose

document workflow behavior, cadence, retries, and secrets needed for reliable automation.

## system boundaries

workflows:
- `.github/workflows/ci.yml`
- `.github/workflows/evolve.yml`

external dependencies:
- github actions runner
- gh cli auth via token
- openai api key

## workflow behavior

### ci workflow

1. trigger on push and pull request to `main`.
2. install dependencies from `requirements.txt`.
3. run `py_compile` and full pytest suite.

### evolution workflow

1. trigger every 6 hours by cron and on manual dispatch.
2. configure git bot identity.
3. run `scripts/evolve.sh` with retries after 15 and 45 minutes.

current cron:
- `0 */6 * * *` (every 6 hours, utc)

## required secrets

- `OPENAI_API_KEY`
- `GITHUB_TOKEN`
- `GH_PAT` (optional fallback)

## what can go wrong

- secrets missing or expired.
- workflow retries duplicate session behavior.
- cron interpretation confusion across timezones.
- frequent schedule can produce duplicate day increments unless guarded.

## diagnostics

```bash
gh run list --workflow evolve --limit 5
gh run view <run-id> --log
rg -n "cron|retry|OPENAI_API_KEY|GH_TOKEN" .github/workflows/evolve.yml
```

## recovery actions

- rotate secrets and rerun with `workflow_dispatch`.
- keep once-per-day pacific guard in script even if retries fire.
- keep one journal publish per pacific day even with four runs per day.
- verify runner logs for exact failure step before changing workflow yaml.

## how to verify

- ci and evolution workflows both succeed on latest main.
- evolution retries do not create multiple day increments in same pacific date.

## related pages

- [evolution pipeline](./evolution-pipeline.md)
- [tagging versioning and day count](./tagging-versioning-and-day-count.md)
- [incident runbook](./incident-runbook.md)
