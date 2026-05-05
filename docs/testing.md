# MD INDUSTRIES

Developer: `M.DHANESVARAN`

## Testing Plan

The repository includes both compile-success and compile-failure validation.

## Included Test Inputs

- `test/sample.py`
- `test/semantic_error.py`

## Functional Test Flow

1. build the local launcher
2. compile `test/sample.py` into `output/sample.c`
3. verify expected snippets in the generated C
4. compile `test/semantic_error.py` and confirm failure
5. if a host C compiler exists, build and run the generated C
6. compare runtime output with `output/expected_output.txt`
