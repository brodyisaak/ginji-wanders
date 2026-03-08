# how it works

## two modes

1. interactive repl
2. autonomous evolution

ginji reads prompts, calls the openai api, executes tool calls, returns tool results into the conversation, and loops until the task is complete.

in the evolution loop, ginji reads its own source, reviews issues, plans one small improvement, writes and tests code, journals the result, then commits and pushes when healthy.
