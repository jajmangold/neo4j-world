// Micro-drama persistent world graph schema.
// Apply with:
//   docker compose exec -T neo4j-world cypher-shell -u neo4j -p microdrama-local -f /var/lib/neo4j/import/world_schema.cypher

CREATE CONSTRAINT character_id IF NOT EXISTS
FOR (n:Character) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT voice_id IF NOT EXISTS
FOR (n:Voice) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT visual_identity_id IF NOT EXISTS
FOR (n:VisualIdentity) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT body_identity_id IF NOT EXISTS
FOR (n:BodyIdentity) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT asset_id IF NOT EXISTS
FOR (n:Asset) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT location_id IF NOT EXISTS
FOR (n:Location) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT organization_id IF NOT EXISTS
FOR (n:Organization) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT episode_id IF NOT EXISTS
FOR (n:Episode) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT scene_id IF NOT EXISTS
FOR (n:Scene) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT event_id IF NOT EXISTS
FOR (n:Event) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT arc_id IF NOT EXISTS
FOR (n:Arc) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT secret_id IF NOT EXISTS
FOR (n:Secret) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT desire_id IF NOT EXISTS
FOR (n:Desire) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT memory_id IF NOT EXISTS
FOR (n:Memory) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reputation_id IF NOT EXISTS
FOR (n:ReputationSnapshot) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT style_tag_name IF NOT EXISTS
FOR (n:StyleTag) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT trait_name IF NOT EXISTS
FOR (n:Trait) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT world_id IF NOT EXISTS
FOR (n:World) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT render_run_id IF NOT EXISTS
FOR (n:RenderRun) REQUIRE n.id IS UNIQUE;

CREATE INDEX character_display_name IF NOT EXISTS
FOR (n:Character) ON (n.display_name);

CREATE INDEX character_slug IF NOT EXISTS
FOR (n:Character) ON (n.slug);

CREATE INDEX character_active IF NOT EXISTS
FOR (n:Character) ON (n.active);

CREATE INDEX event_type IF NOT EXISTS
FOR (n:Event) ON (n.type);

CREATE INDEX event_world_time IF NOT EXISTS
FOR (n:Event) ON (n.world_time);

CREATE INDEX scene_world_time IF NOT EXISTS
FOR (n:Scene) ON (n.world_time);

CREATE INDEX asset_path IF NOT EXISTS
FOR (n:Asset) ON (n.path);

CREATE INDEX arc_status IF NOT EXISTS
FOR (n:Arc) ON (n.status);

CREATE INDEX secret_visibility IF NOT EXISTS
FOR (n:Secret) ON (n.visibility);

// Relationship conventions:
// (:Character)-[:HAS_VOICE {role:'canonical'|'neutral'|'angry'|...}]->(:Voice)
// (:Character)-[:HAS_VISUAL_IDENTITY]->(:VisualIdentity)
// (:Character)-[:HAS_BODY_IDENTITY]->(:BodyIdentity)
// (:Character)-[:HAS_TRAIT {weight:0.0..1.0}]->(:Trait)
// (:Character)-[:HAS_DESIRE {weight:0.0..1.0, conflict:0.0..1.0}]->(:Desire)
// (:Character)-[:REMEMBERS {salience:0.0..1.0, valence:-1.0..1.0}]->(:Memory)
// (:Character)-[:KNOWS_SECRET {certainty:0.0..1.0, leverage:0.0..1.0}]->(:Secret)
// (:Character)-[:OWNS_SECRET]->(:Secret)
// (:Character)-[:APPEARS_IN {role:'lead'|'supporting'|'background'}]->(:Scene)
// (:Character)-[:PARTICIPATED_IN {role:'actor'|'victim'|'witness'|'instigator'}]->(:Event)
// (:Character)-[:MEMBER_OF {role, start_time, end_time}]->(:Organization)
// (:Character)-[:LOCATED_AT {start_time, end_time}]->(:Location)
// (:Character)-[:RELATES_TO {type, attraction, trust, resentment, dependency, tension, fear_of_loss, power_imbalance, updated_at}]->(:Character)
// (:Event)-[:AFFECTS {delta, dimension}]->(:Character)
// (:Event)-[:DAMAGES|:STRENGTHENS]->(:RELATIONSHIP EVENT NODE) is intentionally avoided; keep relationship edge state on RELATES_TO.
// (:Event)-[:REVEALS]->(:Secret)
// (:Event)-[:ADVANCES {amount:0.0..1.0}]->(:Arc)
// (:Scene)-[:PART_OF]->(:Episode)
// (:Scene)-[:USES_ASSET {role:'start_frame'|'end_frame'|'audio_guide'|'render'}]->(:Asset)
// (:RenderRun)-[:RENDERS]->(:Scene)
// (:RenderRun)-[:PRODUCED_ASSET {role:'video'|'contact_sheet'|'final_mix'|'final_muxed'}]->(:Asset)
// (:Voice)-[:HAS_ASSET {role:'canonical_reference'|'emotion_variant'}]->(:Asset)
// (:VisualIdentity)-[:HAS_ASSET {role:'neutral'|'smiling'|'profile'|'full_body'|'keyframe'}]->(:Asset)
