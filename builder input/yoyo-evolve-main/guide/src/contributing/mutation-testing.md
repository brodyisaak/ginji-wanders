# Mutation Testing

yoyo uses [cargo-mutants](https://github.com/sourcefrog/cargo-mutants) to assess test quality. Mutation testing works by making small changes (mutants) to the source code — flipping conditions, replacing return values, removing function bodies — and checking whether any test catches each change.

**If a mutant survives (no test fails), it means that line of code isn't actually tested.**

## Install cargo-mutants

```bash
cargo install cargo-mutants
```

## Run mutation testing

From the project root:

```bash
# Run all mutants (this takes a while — several minutes)
cargo mutants

# Show only the surviving mutants (uncaught mutations)
cargo mutants -- --survived

# Run mutants for a specific file
cargo mutants -f src/format.rs

# Run mutants for a specific function
cargo mutants -F "format_cost"
```

## Read the results

After a run, cargo-mutants creates a `mutants.out/` directory with detailed results:

```bash
# Summary
cat mutants.out/caught.txt     # mutants killed by tests ✓
cat mutants.out/survived.txt   # mutants NOT caught — test gaps!
cat mutants.out/timeout.txt    # mutants that caused infinite loops
cat mutants.out/unviable.txt   # mutants that didn't compile
```

Focus on `survived.txt` — each line is a mutation that no test catches. These are the weak spots.

## Configuration

The `mutants.toml` file in the project root excludes known-acceptable mutants:

- **Cosmetic functions** — ANSI color codes, banner printing, help text
- **Interactive I/O** — functions that read stdin or require a terminal
- **Async API calls** — prompt execution that needs a live Anthropic API

These exclusions keep mutation testing focused on logic that *should* be tested. If you add a new feature with testable logic, make sure it's not excluded.

## Writing targeted tests

When you find a surviving mutant:

1. Read what the mutation does (e.g., "replace `<` with `<=` in format_cost")
2. Write a test that specifically catches that boundary condition
3. Re-run `cargo mutants -F "function_name"` to verify the mutant is now caught

Example workflow:

```bash
# Find surviving mutants
cargo mutants 2>&1 | grep "SURVIVED"

# Write a test to kill the mutant, then verify
cargo mutants -F "format_cost"
```

## When to run

Mutation testing is slow — it builds and tests your code once per mutant. Don't add it to CI yet. Run it manually:

- After adding a new feature, to verify test coverage
- Before a release, as a quality check
- When you suspect the test suite has gaps
