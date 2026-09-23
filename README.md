# Neo4j World Graph

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://hub.docker.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-red.svg)](https://neo4j.com/)

A persistent graph database for narrative world simulation where **relationships carry numerical emotions**. Trust, resentment, attraction, tension, fear of loss, power imbalance -- all stored as edge properties that update when events happen.

---

## The Idea

Most story engines track "who knows whom." This tracks *how they feel about each other*, numerically, and updates those feelings when things happen.

A betrayal doesn't just create a plot point. It applies `trust: -0.30, resentment: +0.40, tension: +0.15` to the relationship edge. A near-kiss applies `attraction: +0.15, tension: +0.25`. The numbers persist across scenes and episodes, so the AI (or a human writer) can query the current emotional state of any relationship and write accordingly.

## Schema

```mermaid
erDiagram
    Character ||--o{ RELATES_TO : has
    Character ||--o{ APPEARS_IN : in
    Character ||--o{ HAS_TRAIT : with
    Character ||--o{ HAS_DESIRE : wants
    Character ||--o{ REMEMBERS : remembers
    Character ||--o{ KNOWS_SECRET : knows
    Scene ||--o{ PART_OF : episode
    Scene ||--o{ USES_ASSET : uses
    Event ||--o{ AFFECTS : impacts
    Event ||--o{ ADVANCES : arc
    Event ||--o{ REVEALS : secret
```

### Relationship Edge Fields

| Field | Range | Description |
|-------|-------|-------------|
| `attraction` | 0.0 - 1.0 | Romantic/physical pull |
| `trust` | 0.0 - 1.0 | Reliability and honesty |
| `resentment` | 0.0 - 1.0 | Grudge accumulation |
| `dependency` | 0.0 - 1.0 | Need for the other character |
| `tension` | 0.0 - 1.0 | Unresolved friction |
| `fear_of_loss` | 0.0 - 1.0 | Attachment anxiety |
| `power_imbalance` | -1.0 - 1.0 | Dominance (negative = one-sided) |

### Event Types

Events are the *consequence layer*. Each event type applies known deltas to relationship edges:

| Event | trust | resentment | tension | attraction |
|-------|-------|------------|---------|------------|
| `BETRAYAL` | -0.30 | +0.40 | +0.15 | varies |
| `NEAR_KISS` | +/-0.05 | -- | +0.25 | +0.15 |
| `PUBLIC_HUMILIATION` | -0.35 | +0.45 | +0.10 | -- |
| `RECONCILIATION` | +0.15 | -0.15 | stays high | -- |
| `SECRET_REVEALED` | varies | +0.20 | +0.20 | -- |

Full taxonomy in [`docs/event_taxonomy.md`](docs/event_taxonomy.md).

## Narrative Governors

The world sim enforces continuity rules to prevent chaos:

| Governor | Purpose |
|----------|---------|
| **Scandal cooldowns** | Major reveals need downtime before the next one |
| **Escalation budget** | Every arc has limited escalation per episode |
| **Emotional rhythm** | Contrast high-tension beats with humor, tenderness, or embarrassment |
| **Arc spacing** | Don't resolve every active arc in the same episode |
| **Consequence persistence** | Large events alter future prompts, wardrobe, posture, and relationships |

Rules in [`docs/narrative_governors.md`](docs/narrative_governors.md).

## Quick Start

```bash
docker compose up -d

# Apply schema
cp schema/*.cypher import/
docker compose exec -T neo4j-world cypher-shell -u neo4j -p microdrama-local \
  -f /var/lib/neo4j/import/world_schema.cypher
docker compose exec -T neo4j-world cypher-shell -u neo4j -p microdrama-local \
  -f /var/lib/neo4j/import/seed_world.cypher
```

### Ingest a Story Event

```bash
python3 scripts/ingest_story_event.py \
  --event-json examples/events/private_warning_escalation.json
```

### Export Character Memory Context

```bash
python3 scripts/export_memory_context.py \
  --scene-manifest /path/to/scene_manifest.json \
  --output-md /tmp/memory_context.md \
  --output-json /tmp/memory_context.json
```

## Features

| Capability | Description |
|-----------|-------------|
| Drama-state relationships | Numerical emotion fields on every character edge |
| Event taxonomy | Typed events with deterministic delta application |
| Narrative governors | Continuity enforcement and pacing rules |
| Memory export | Compressed context for LLM planner prompts |
| Cypher-native schema | Full graph model in Cypher, no ORM layer |
| Seed data | Sample world with characters, traits, and desires |

## Who This Is For

- **Narrative AI researchers** building story generation systems that need persistent emotional state
- **Game developers** prototyping NPC relationship systems with structured drama
- **Interactive fiction** authors who want mechanical consequences for player choices
- **AI video pipelines** that need to track character continuity across generated scenes

## Documentation

| Document | Purpose |
|----------|---------|
| [`docs/relationship_update_rules.md`](docs/relationship_update_rules.md) | Edge field ranges, delta examples, governor rules |
| [`docs/event_taxonomy.md`](docs/event_taxonomy.md) | Event types, required fields, quality rules |
| [`docs/narrative_governors.md`](docs/narrative_governors.md) | Continuity enforcement, episode shape, anti-patterns |
| [`docs/memory_compression.md`](docs/memory_compression.md) | Exporting compressed context for LLM prompts |

## Contributing

This is part of the [Microdrama](https://github.com/jajmangold/microdrama-orchestrator) ecosystem. Issues and PRs welcome.

## License

[MIT](LICENSE)
