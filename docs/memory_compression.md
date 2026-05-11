# Memory Compression

The graph stores facts. Prompts need compressed emotional context.

## Character Memory Summary

Each character should have:

- formative events
- recent events
- current obsessions
- current resentments
- current fears
- unresolved hooks
- relationship deltas since last scene

## Relationship Memory Summary

For each important directed edge:

- current edge values
- last three meaningful events
- open wound
- current desire
- next likely pressure point

## Episode Prompt Context

Keep prompt context short:

- one sentence of character identity
- one sentence of relationship history
- one sentence of current pressure
- one sentence of scene goal

## Tooling

Use `scripts/ingest_story_event.py` after a scene decision becomes canonical. Event JSON should include participants, relationship deltas, reputation deltas, arc updates, secret updates, and memories when they differ from the event summary.

Use `scripts/export_memory_context.py` before story planning or shot prompting. Prefer the Markdown export for LLM planner prompts and the JSON export when a Prefect/LangGraph node needs structured context.
