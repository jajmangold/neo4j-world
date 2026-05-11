#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import subprocess
import wave
from pathlib import Path

from neo4j import GraphDatabase


def run_ffprobe(path: Path) -> dict:
    if not path.exists():
        return {}
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_name,width,height,sample_rate,channels,avg_frame_rate",
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def infer_asset_type(path: Path, explicit_type: str | None) -> str:
    if explicit_type:
        return explicit_type
    mime, _ = mimetypes.guess_type(path.name)
    if mime:
        if mime.startswith("audio/"):
            return "audio"
        if mime.startswith("video/"):
            return "video"
        if mime.startswith("image/"):
            return "image"
    return "file"


def media_props(path: Path, asset_type: str) -> dict:
    props = {
        "size_bytes": path.stat().st_size if path.exists() else None,
    }
    probe = run_ffprobe(path)
    streams = probe.get("streams") or []
    fmt = probe.get("format") or {}
    if "duration" in fmt:
        try:
            props["duration_seconds"] = float(fmt["duration"])
        except ValueError:
            pass
    if streams:
        stream = streams[0]
        for key in ("codec_name", "width", "height", "sample_rate", "channels", "avg_frame_rate"):
            if key in stream:
                value = stream[key]
                if key in {"width", "height", "channels"}:
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        pass
                if key == "sample_rate":
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        pass
                props[key] = value
    if asset_type == "audio" and path.suffix.lower() == ".wav" and "duration_seconds" not in props:
        try:
            with wave.open(str(path), "rb") as wav:
                frames = wav.getnframes()
                sample_rate = wav.getframerate()
                props["sample_rate"] = sample_rate
                props["channels"] = wav.getnchannels()
                props["duration_seconds"] = float(frames) / float(sample_rate) if sample_rate else None
                props["codec_name"] = "pcm_wav"
        except wave.Error:
            pass
    props["type"] = asset_type
    return {k: v for k, v in props.items() if v is not None}


def upsert_asset(tx, args, props):
    tx.run(
        """
        MERGE (a:Asset {id: $asset_id})
        ON CREATE SET a.created_at = datetime()
        SET a += $props,
            a.path = $path,
            a.role = $role,
            a.updated_at = datetime()
        """,
        asset_id=args.asset_id,
        props=props,
        path=str(Path(args.path).resolve()),
        role=args.role,
    )

    if args.character_id:
        tx.run(
            """
            MATCH (c:Character {id: $character_id})
            MATCH (a:Asset {id: $asset_id})
            MERGE (c)-[r:HAS_ASSET {role: $role}]->(a)
            SET r.updated_at = datetime()
            """,
            character_id=args.character_id,
            asset_id=args.asset_id,
            role=args.role,
        )

    if args.voice_id:
        tx.run(
            """
            MERGE (v:Voice {id: $voice_id})
            ON CREATE SET v.created_at = datetime()
            SET v.updated_at = datetime()
            WITH v
            MATCH (a:Asset {id: $asset_id})
            MERGE (v)-[r:HAS_ASSET {role: $role}]->(a)
            SET r.updated_at = datetime()
            """,
            voice_id=args.voice_id,
            asset_id=args.asset_id,
            role=args.role,
        )
        if args.character_id:
            tx.run(
                """
                MATCH (c:Character {id: $character_id})
                MATCH (v:Voice {id: $voice_id})
                MERGE (c)-[r:HAS_VOICE {role: $voice_role}]->(v)
                SET r.updated_at = datetime()
                """,
                character_id=args.character_id,
                voice_id=args.voice_id,
                voice_role=args.voice_role,
            )

    if args.visual_identity_id:
        tx.run(
            """
            MERGE (vi:VisualIdentity {id: $visual_identity_id})
            ON CREATE SET vi.created_at = datetime()
            SET vi.updated_at = datetime()
            WITH vi
            MATCH (a:Asset {id: $asset_id})
            MERGE (vi)-[r:HAS_ASSET {role: $role}]->(a)
            SET r.updated_at = datetime()
            """,
            visual_identity_id=args.visual_identity_id,
            asset_id=args.asset_id,
            role=args.role,
        )
        if args.character_id:
            tx.run(
                """
                MATCH (c:Character {id: $character_id})
                MATCH (vi:VisualIdentity {id: $visual_identity_id})
                MERGE (c)-[:HAS_VISUAL_IDENTITY]->(vi)
                """,
                character_id=args.character_id,
                visual_identity_id=args.visual_identity_id,
            )

    if args.scene_id:
        tx.run(
            """
            MERGE (s:Scene {id: $scene_id})
            ON CREATE SET s.created_at = datetime()
            SET s.updated_at = datetime()
            WITH s
            MATCH (a:Asset {id: $asset_id})
            MERGE (s)-[r:USES_ASSET {role: $role}]->(a)
            SET r.updated_at = datetime()
            """,
            scene_id=args.scene_id,
            asset_id=args.asset_id,
            role=args.role,
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Register a generated asset in the Neo4j micro-drama world graph.")
    parser.add_argument("--uri", default=os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.environ.get("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.environ.get("NEO4J_PASSWORD", "microdrama-local"))
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--type", choices=["audio", "image", "video", "file"], default=None)
    parser.add_argument("--role", required=True)
    parser.add_argument("--character-id", default="")
    parser.add_argument("--voice-id", default="")
    parser.add_argument("--voice-role", default="canonical")
    parser.add_argument("--visual-identity-id", default="")
    parser.add_argument("--scene-id", default="")
    parser.add_argument("--metadata-json", default="")
    return parser.parse_args()


def main():
    args = parse_args()
    path = Path(args.path).expanduser()
    asset_type = infer_asset_type(path, args.type)
    props = media_props(path, asset_type)
    if args.metadata_json:
        props.update(json.loads(args.metadata_json))

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    with driver:
        with driver.session() as session:
            session.execute_write(upsert_asset, args, props)
    print(json.dumps({"asset_id": args.asset_id, "path": str(path.resolve()), "type": asset_type, "role": args.role}, indent=2))


if __name__ == "__main__":
    main()
