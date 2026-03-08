# Installation

## Requirements

- **Rust toolchain** — install from [rustup.rs](https://rustup.rs)
- **Anthropic API key** — get one from [console.anthropic.com](https://console.anthropic.com)

## Install from source

```bash
git clone https://github.com/yologdev/yoyo-evolve.git
cd yoyo-evolve
cargo build --release
```

The binary will be at `target/release/yoyo`.

## Run directly with Cargo

If you just want to try it:

```bash
cd yoyo-evolve
ANTHROPIC_API_KEY=sk-ant-... cargo run
```

## Set your API key

yoyo looks for your API key in this order:

1. `--api-key` CLI flag (highest priority)
2. `ANTHROPIC_API_KEY` environment variable
3. `API_KEY` environment variable

Set one of them:

```bash
# Via environment variable (recommended)
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Or pass directly
cargo run -- --api-key sk-ant-api03-...
```

If no key is found via any method, yoyo will exit with an error message explaining what to do.
