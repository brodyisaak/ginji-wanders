# architecture

## repl execution flow

1. determine input path: stdin pipe, `--prompt`, or interactive prompt
2. build system prompt from built-in text plus optional system and skills
3. call openai api with function tools
4. execute returned tool calls and append outputs
5. loop until no tool calls remain, then print final response

## input paths

- stdin piped content is used first when present
- `--prompt` is used for single-shot tasks when no piped input exists
- interactive mode starts when neither source is provided

## tool execution loop

ginji dispatches tool calls by name, parses json args, executes local functions, returns string outputs, and handles malformed arguments safely.

## skills loading

`--skills` enables recursive discovery of `SKILL.md` files. frontmatter metadata and body text are concatenated and prepended into the system prompt.

## design intent

ginji is intentionally small and functional to keep behavior inspectable and easy to evolve. `src/ginji.py` remains the core runtime.
