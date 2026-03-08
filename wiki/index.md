# wiki index

## audience and purpose

this wiki is the maintainer reference for ginji internals and operations. it is written for people who need to keep autonomous runs healthy, debug failures quickly, and make safe improvements without breaking the agent loop.

## read order by role

### maintainer

1. [overview](./overview.md)
2. [architecture](./architecture.md)
3. [runtime loop and message flow](./runtime-loop-and-message-flow.md)
4. [evolution pipeline](./evolution-pipeline.md)
5. [incident runbook](./incident-runbook.md)

### contributor

1. [overview](./overview.md)
2. [prompts and skills system](./prompts-and-skills-system.md)
3. [tools contracts and failure modes](./tools-contracts-and-failure-modes.md)
4. [testing and safety](./testing-and-safety.md)
5. [contribution guidelines for agent safe changes](./contribution-guidelines-for-agent-safe-changes.md)

### operator

1. [github actions and scheduling](./github-actions-and-scheduling.md)
2. [tagging versioning and day count](./tagging-versioning-and-day-count.md)
3. [issue ingestion triage and response](./issue-ingestion-triage-and-response.md)
4. [maintainer playbook local ops](./maintainer-playbook-local-ops.md)
5. [incident runbook](./incident-runbook.md)

## page map

- [overview](./overview.md): mission, operating model, and repo boundaries.
- [architecture](./architecture.md): runtime decomposition and control flow map.
- [runtime loop and message flow](./runtime-loop-and-message-flow.md): detailed repl and tool-call sequence.
- [tools contracts and failure modes](./tools-contracts-and-failure-modes.md): function contracts, constraints, and error behavior.
- [prompts and skills system](./prompts-and-skills-system.md): prompt composition, skill parsing, and precedence.
- [evolution pipeline](./evolution-pipeline.md): end-to-end `scripts/evolve.sh` behavior.
- [issue ingestion triage and response](./issue-ingestion-triage-and-response.md): issue pull, formatting, triage, and feedback loop.
- [state files](./state-files.md): persistent and ephemeral state file contracts.
- [testing and safety](./testing-and-safety.md): validation gates and safety controls.
- [github actions and scheduling](./github-actions-and-scheduling.md): workflow triggers, retries, and secret requirements.
- [tagging versioning and day count](./tagging-versioning-and-day-count.md): day progression and tag semantics.
- [incident runbook](./incident-runbook.md): failure diagnosis and recovery procedures.
- [maintainer playbook local ops](./maintainer-playbook-local-ops.md): local run, debug, and release workflow.
- [contribution guidelines for agent safe changes](./contribution-guidelines-for-agent-safe-changes.md): change policy and review checklist.

## how to verify this wiki is healthy

```bash
ls wiki/*.md | wc -l
rg -n "\]\(\./.*\.md\)" wiki
```

expected result: links resolve to existing files and no page is isolated.
