#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

EDGE_FIELDS = {
    "attraction",
    "trust",
    "resentment",
    "dependency",
    "tension",
    "fear_of_loss",
    "power_imbalance",
}


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).expanduser().open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clamp(field: str, value: float) -> float:
    if field == "power_imbalance":
        return max(-1.0, min(1.0, value))
    return max(0.0, min(1.0, value))


def event_id(event: dict[str, Any]) -> str:
    return event.get("id") or event["event_id"]


def relationship_props(tx, source_id: str, target_id: str) -> dict[str, Any]:
    result = tx.run(
        """
        MATCH (:Character {id: $source_id})-[r:RELATES_TO]->(:Character {id: $target_id})
        RETURN properties(r) AS props
        """,
        source_id=source_id,
        target_id=target_id,
    ).single()
    return dict(result["props"]) if result and result["props"] else {}


def apply_relationship_delta(tx, event: dict[str, Any], delta: dict[str, Any]) -> None:
    source_id = delta["source_character_id"]
    target_id = delta["target_character_id"]
    current = relationship_props(tx, source_id, target_id)
    edge_type = delta.get("type") or current.get("type") or "dramatic"
    fields = delta.get("deltas", {})
    next_props = {field: current.get(field, 0.0) for field in EDGE_FIELDS}

    for field, change in fields.items():
        if field not in EDGE_FIELDS:
            continue
        next_props[field] = clamp(field, float(next_props.get(field, 0.0)) + float(change))

    next_props["type"] = edge_type
    next_props["last_event_id"] = event_id(event)
    next_props["last_event_summary"] = event.get("summary", "")
    next_props["updated_at"] = event.get("world_time", "")

    tx.run(
        """
        MERGE (source:Character {id: $source_id})
        ON CREATE SET source.created_at = datetime(), source.active = true
        MERGE (target:Character {id: $target_id})
        ON CREATE SET target.created_at = datetime(), target.active = true
        MERGE (source)-[r:RELATES_TO]->(target)
        SET r += $props,
            r.updated_at = datetime()
        WITH source, target
        MATCH (e:Event {id: $event_id})
        MERGE (source)-[sr:RELATIONSHIP_CHANGED {event_id: $event_id, target_id: $target_id}]->(e)
        SET sr.deltas = $deltas, sr.updated_at = datetime()
        MERGE (e)-[er:AFFECTED_RELATIONSHIP {source_id: $source_id, target_id: $target_id}]->(target)
        SET er.deltas = $deltas, er.updated_at = datetime()
        """,
        source_id=source_id,
        target_id=target_id,
        event_id=event_id(event),
        props=next_props,
        deltas=json.dumps(fields, sort_keys=True),
    )


def ingest_event(tx, event: dict[str, Any]) -> None:
    eid = event_id(event)
    tx.run(
        """
        MERGE (e:Event {id: $event_id})
        ON CREATE SET e.created_at = datetime()
        SET e.type = $type,
            e.summary = $summary,
            e.world_time = $world_time,
            e.severity = $severity,
            e.visibility = $visibility,
            e.source = $source,
            e.updated_at = datetime()
        """,
        event_id=eid,
        type=event["type"],
        summary=event["summary"],
        world_time=event["world_time"],
        severity=float(event.get("severity", 0.0)),
        visibility=float(event.get("visibility", 0.0)),
        source=event.get("source", "manual"),
    )

    if event.get("episode_id"):
        tx.run(
            """
            MERGE (ep:Episode {id: $episode_id})
            ON CREATE SET ep.created_at = datetime()
            WITH ep
            MATCH (e:Event {id: $event_id})
            MERGE (e)-[:PART_OF]->(ep)
            """,
            event_id=eid,
            episode_id=event["episode_id"],
        )

    if event.get("scene_id"):
        tx.run(
            """
            MERGE (s:Scene {id: $scene_id})
            ON CREATE SET s.created_at = datetime()
            WITH s
            MATCH (e:Event {id: $event_id})
            MERGE (e)-[:OCCURS_IN]->(s)
            """,
            event_id=eid,
            scene_id=event["scene_id"],
        )

    for participant in event.get("participants", []):
        tx.run(
            """
            MERGE (c:Character {id: $character_id})
            ON CREATE SET c.created_at = datetime(), c.active = true
            WITH c
            MATCH (e:Event {id: $event_id})
            MERGE (c)-[r:PARTICIPATED_IN {role: $role}]->(e)
            SET r.updated_at = datetime()
            """,
            event_id=eid,
            character_id=participant["character_id"],
            role=participant.get("role", "participant"),
        )

    for delta in event.get("relationship_deltas", []):
        apply_relationship_delta(tx, event, delta)

    for delta in event.get("reputation_deltas", []):
        tx.run(
            """
            MERGE (c:Character {id: $character_id})
            ON CREATE SET c.created_at = datetime(), c.active = true
            WITH c
            MATCH (e:Event {id: $event_id})
            MERGE (e)-[r:AFFECTS {dimension: $dimension}]->(c)
            SET r.delta = $delta,
                r.updated_at = datetime()
            """,
            event_id=eid,
            character_id=delta["character_id"],
            dimension=delta.get("dimension", "reputation"),
            delta=float(delta.get("delta", 0.0)),
        )

    for arc_update in event.get("arc_updates", event.get("arc_ids", [])):
        if isinstance(arc_update, str):
            arc_update = {"arc_id": arc_update, "amount": 0.0}
        tx.run(
            """
            MERGE (a:Arc {id: $arc_id})
            ON CREATE SET a.created_at = datetime(), a.status = 'active'
            WITH a
            MATCH (e:Event {id: $event_id})
            MERGE (e)-[r:ADVANCES]->(a)
            SET r.amount = $amount,
                r.updated_at = datetime()
            """,
            event_id=eid,
            arc_id=arc_update["arc_id"],
            amount=float(arc_update.get("amount", 0.0)),
        )

    for secret in event.get("secret_updates", []):
        tx.run(
            """
            MERGE (s:Secret {id: $secret_id})
            ON CREATE SET s.created_at = datetime()
            SET s += $props,
                s.updated_at = datetime()
            WITH s
            MATCH (e:Event {id: $event_id})
            MERGE (e)-[:REVEALS]->(s)
            """,
            event_id=eid,
            secret_id=secret["secret_id"],
            props={k: v for k, v in secret.items() if k != "secret_id"},
        )

    memories = event.get("memories") or [
        {
            "character_id": participant["character_id"],
            "summary": event["summary"],
            "salience": event.get("severity", 0.5),
            "valence": 0.0,
        }
        for participant in event.get("participants", [])
    ]
    for memory in memories:
        memory_id = memory.get("memory_id") or f"memory_{eid}_{memory['character_id']}"
        tx.run(
            """
            MERGE (m:Memory {id: $memory_id})
            ON CREATE SET m.created_at = datetime()
            SET m.summary = $summary,
                m.world_time = $world_time,
                m.event_id = $event_id,
                m.updated_at = datetime()
            WITH m
            MATCH (c:Character {id: $character_id})
            MERGE (c)-[r:REMEMBERS]->(m)
            SET r.salience = $salience,
                r.valence = $valence,
                r.updated_at = datetime()
            """,
            memory_id=memory_id,
            event_id=eid,
            character_id=memory["character_id"],
            summary=memory.get("summary", event["summary"]),
            world_time=event["world_time"],
            salience=float(memory.get("salience", event.get("severity", 0.5))),
            valence=float(memory.get("valence", 0.0)),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a durable story event and apply graph state deltas.")
    parser.add_argument("--uri", default=os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.environ.get("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.environ.get("NEO4J_PASSWORD", "microdrama-local"))
    parser.add_argument("--event-json", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    event = read_json(args.event_json)
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    with driver:
        with driver.session() as session:
            session.execute_write(ingest_event, event)
    print(json.dumps({"event_id": event_id(event), "type": event["type"], "summary": event["summary"]}, indent=2))


if __name__ == "__main__":
    main()
