# Neo4j World Graph

Persistent graph database for the micro-drama world simulation.

## Service

- Browser: `http://127.0.0.1:7474`
- Bolt: `bolt://127.0.0.1:7687`
- User: `neo4j`
- Default local password: `microdrama-local`

Override the password by setting `NEO4J_PASSWORD` before starting Compose.

## Start

```bash
docker compose up -d
```

## Apply Schema

The compose file mounts `./import` to `/var/lib/neo4j/import`. Copy schema files there or run them from `/schema` through the host.

```bash
cp schema/*.cypher import/
docker compose exec -T neo4j-world cypher-shell -u neo4j -p microdrama-local -f /var/lib/neo4j/import/world_schema.cypher
docker compose exec -T neo4j-world cypher-shell -u neo4j -p microdrama-local -f /var/lib/neo4j/import/seed_world.cypher
```

## Ingest Assets

Register one file directly:

```bash
python3 scripts/ingest_asset.py \
  --asset-id asset_char001_voice_neutral \
  --path /srv/nvme-data/containers/projects/microdramas/characters/char001/voice/neutral.wav \
  --type audio \
  --role canonical_reference \
  --character-id char001 \
  --voice-id voice_char001
```

Register a production render and its linked assets from a render manifest:

```bash
python3 scripts/ingest_render_manifest.py \
  --render-manifest /srv/nvme-data/containers/projects/microdramas/orchestrator_runs/episode_smoke_001/scene_smoke_001/render_manifest.dry_run.json
```

The render manifest importer creates or updates `Episode`, `Scene`, `RenderRun`, `Asset`, `Character`, `Voice`, and `VisualIdentity` nodes, then links them with `PART_OF`, `RENDERS`, `USES_ASSET`, `PRODUCED_ASSET`, `APPEARS_IN`, `HAS_VOICE`, and `HAS_VISUAL_IDENTITY`.

## Model Shape

Core node labels:

- `World`
- `Character`
- `Voice`
- `VisualIdentity`
- `BodyIdentity`
- `Asset`
- `Location`
- `Organization`
- `Episode`
- `Scene`
- `Event`
- `Arc`
- `Secret`
- `Desire`
- `Memory`
- `ReputationSnapshot`
- `RenderRun`
- `Trait`
- `StyleTag`

Important relationship:

- `(:Character)-[:RELATES_TO]->(:Character)`

Relationship edges carry drama state:

- `attraction`
- `trust`
- `resentment`
- `dependency`
- `tension`
- `fear_of_loss`
- `power_imbalance`

That edge state is where most of the drama lives.
