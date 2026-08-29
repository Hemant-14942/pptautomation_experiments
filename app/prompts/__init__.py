"""Every prompt sent to the AI model lives here, one module per call site,
so prompt text can be reviewed/tuned without digging through pipeline logic.

Each module exports:
  * a `*_SYSTEM_PROMPT` constant (or `None` if the call doesn't use one), and
  * a `build_*_prompt(...)` function that renders the user-turn text from
    the caller's data.
"""
