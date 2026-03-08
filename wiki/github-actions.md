# github actions

## ci workflow

`.github/workflows/ci.yml` runs on pushes and pull requests to `main`. it installs dependencies, compiles `src/ginji.py`, and runs pytest.

## evolution workflow

`.github/workflows/evolve.yml` runs on a 6-hour cron and via `workflow_dispatch`. it installs dependencies, configures git bot identity, and runs `scripts/evolve.sh`.

## retry behavior

evolution retries after 15 minutes, then after 45 minutes if earlier attempts fail.

## required secrets

- `OPENAI_API_KEY`
- `GITHUB_TOKEN`
- `GH_PAT`

## git bot identity

workflow config sets:
- `ginji-wanders[bot]`
- `ginji-wanders[bot]@users.noreply.github.com`

## why workflow_dispatch exists

manual dispatch allows maintainers to run evolution on demand for debugging, validation, or urgent fixes outside cron cadence.
