# getting started

## installation

```bash
pip install -r requirements.txt
```

## local run

```bash
OPENAI_API_KEY=sk-... python src/ginji.py
```

## single-shot prompt

```bash
OPENAI_API_KEY=sk-... python src/ginji.py -p "list the files in this repo"
```

## piped input

```bash
echo "read src/ginji.py" | OPENAI_API_KEY=sk-... python src/ginji.py
```

## local evolution

```bash
OPENAI_API_KEY=sk-... ./scripts/evolve.sh
```

## required tools

- python 3.11+
- git
- gh cli
- openai api key
