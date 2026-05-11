#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as handle:
        return json.load(handle)


def character_ids_from_scene(path: str) -> list[str]:
    scene = read_json(path)
    return [item["character_id"] for item in scene.get("characters", [])]


def query_character_context(tx, character_id: str, recent_limit: int) -> dict[str, Any]:
    character = tx.run(
        """
        MATCH (c:Character {id: $character_id})
        RETURN c {
          .id, .display_name, .slug, .age, .logline, .attachment_style,
          .baseline_emotion, .active
        } AS c
        """,
        character_id=character_id,
    ).single()

    traits = tx.run(
        """
        MATCH (:Character {id: $character_id})-[r:HAS_TRAIT]->(t:Trait)
        RETURN t.name AS name, r.weight AS weight
        ORDER BY weight DESC
        LIMIT 8
        """,
        character_id=character_id,
    ).data()

    desires = tx.run(
        """
        MATCH (:Character {id: $character_id})-[r:HAS_DESIRE]->(d:Desire)
        RETURN d.id AS id, d.name AS name, d.description AS description,
               r.weight AS weight, r.conflict AS conflict
        ORDER BY weight DESC
        LIMIT 8
        """,
        character_id=character_id,
    ).data()

    memories = tx.run(
        """
        MATCH (:Character {id: $character_id})-[r:REMEMBERS]->(m:Memory)
        RETURN m.id AS id, m.summary AS summary, m.world_time AS world_time,
               m.event_id AS event_id, r.salience AS salience, r.valence AS valence
        ORDER BY coalesce(m.world_time, '') DESC, r.salience DESC
        LIMIT $recent_limit
        """,
        character_id=character_id,
        recent_limit=recent_limit,
    ).data()

    relationships = tx.run(
        """
        MATCH (:Character {id: $character_id})-[r:RELATES_TO]->(other:Character)
        RETURN other.id AS target_id,
               coalesce(other.display_name, other.id) AS target_name,
               r.type AS type,
               r.attraction AS attraction,
               r.trust AS trust,
               r.resentment AS resentment,
               r.dependency AS dependency,
               r.tension AS tension,
               r.fear_of_loss AS fear_of_loss,
               r.power_imbalance AS power_imbalance,
               r.last_event_id AS last_event_id,
               r.last_event_summary AS last_event_summary
        ORDER BY coalesce(r.tension, 0) DESC, coalesce(r.attraction, 0) DESC
        LIMIT 12
        """,
        character_id=character_id,
    ).data()

    events = tx.run(
        """
        MATCH (:Character {id: $character_id})-[p:PARTICIPATED_IN]->(e:Event)
        RETURN e.id AS id, e.type AS type, e.summary AS summary, e.world_time AS world_time,
               e.severity AS severity, e.visibility AS visibility, p.role AS role
        ORDER BY coalesce(e.world_time, '') DESC
        LIMIT $recent_limit
        """,
        character_id=character_id,
        recent_limit=recent_limit,
    ).data()

    return {
        "character": character["c"] if character else {"id": character_id},
        "traits": traits,
        "desires": desires,
        "recent_memories": memories,
        "relationships": relationships,
        "recent_events": events,
    }


def build_markdown(context: dict[str, Any]) -> str:
    lines = ["# Memory Context", ""]
    for item in context["characters"]:
        char = item["character"]
        name = char.get("display_name") or char["id"]
        lines.extend([f"## {name}", ""])
        if char.get("logline"):
            lines.append(f"- Identity: {char['logline']}")
        if char.get("attachment_style") or char.get("baseline_emotion"):
            lines.append(
                "- Baseline: "
                + ", ".join(
                    value
                    for value in [char.get("attachment_style"), char.get("baseline_emotion")]
                    if value
                )
            )
        if item["traits"]:
            lines.append(
                "- Traits: "
                + ", ".join(f"{trait['name']} {trait.get('weight', 0):.2f}" for trait in item["traits"])
            )
        if item["desires"]:
            lines.append(
                "- Desires: "
                + ", ".join(f"{desire['name']} {desire.get('weight', 0):.2f}" for desire in item["desires"])
            )
        for rel in item["relationships"][:5]:
            lines.append(
                f"- Relationship to {rel['target_name']}: {rel.get('type') or 'dramatic'}, "
                f"attraction {rel.get('attraction', 0):.2f}, trust {rel.get('trust', 0):.2f}, "
                f"resentment {rel.get('resentment', 0):.2f}, tension {rel.get('tension', 0):.2f}."
            )
            if rel.get("last_event_summary"):
                lines.append(f"  Last pressure: {rel['last_event_summary']}")
        for memory in item["recent_memories"][:5]:
            lines.append(f"- Memory: {memory['summary']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export compressed character memory context for prompts.")
    parser.add_argument("--uri", default=os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.environ.get("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.environ.get("NEO4J_PASSWORD", "microdrama-local"))
    parser.add_argument("--character-id", action="append", default=[])
    parser.add_argument("--scene-manifest", default="")
    parser.add_argument("--recent-limit", type=int, default=6)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    character_ids = list(args.character_id)
    if args.scene_manifest:
        character_ids.extend(character_ids_from_scene(args.scene_manifest))
    character_ids = list(dict.fromkeys(character_ids))
    if not character_ids:
        raise SystemExit("Provide --character-id or --scene-manifest")

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    with driver:
        with driver.session() as session:
            context = {
                "character_ids": character_ids,
                "characters": [
                    session.execute_read(query_character_context, character_id, args.recent_limit)
                    for character_id in character_ids
                ],
            }

    if args.output_json:
        Path(args.output_json).expanduser().write_text(json.dumps(context, indent=2), encoding="utf-8")
    if args.output_md:
        Path(args.output_md).expanduser().write_text(build_markdown(context), encoding="utf-8")
    if not args.output_json and not args.output_md:
        print(json.dumps(context, indent=2))


if __name__ == "__main__":
    main()
