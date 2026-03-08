---
name: self-assess
description: analyze your own source code and capabilities to find bugs, gaps, and opportunities
tools: [bash_exec, read_file, write_file]
---

# self-assessment

you are assessing yourself. your source code is your body. read it critically.

## process
1. read src/ginji.py completely
2. try a small real task to test yourself
3. note what went wrong — crashes, bad errors, missing features, slow/clunky ux
4. check JOURNAL.md — have you tried this before and failed?

## what to look for
- unhandled exceptions — potential crashes
- missing error messages — silent failures
- hardcoded values — paths, model names, magic strings
- missing edge cases — empty input, unicode, very long strings
- ux gaps — anything confusing or annoying

## output
write findings as a prioritized list. most impactful first.
format: self-assessment day n: 1. [critical/high/medium/low] description

then decide what to tackle this session. one improvement only.
