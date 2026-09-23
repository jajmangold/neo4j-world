// Minimal seed world for validating the model.

MERGE (w:World {id: 'microdrama_world_001'})
SET w.name = 'Microdrama World 001',
    w.genre = 'luxury erotic social melodrama',
    w.tone = 'romantic, status-driven, suggestive, funny, cruel, emotionally serialized',
    w.created_at = datetime(),
    w.current_world_time = date('2026-01-01');

MERGE (camille:Character {id: 'char_camille_voss'})
SET camille.display_name = 'Camille Voss',
    camille.slug = 'camille-voss',
    camille.age = 27,
    camille.active = true,
    camille.logline = 'A status-obsessed founder with a perfect face and a dangerous need to be chosen.',
    camille.attachment_style = 'anxious',
    camille.baseline_emotion = 'controlled tension',
    camille.created_at = datetime();

MERGE (marco:Character {id: 'char_marco_vale'})
SET marco.display_name = 'Marco Vale',
    marco.slug = 'marco-vale',
    marco.age = 34,
    marco.active = true,
    marco.logline = 'A charming operator whose loyalty is usually real, but never free.',
    marco.attachment_style = 'avoidant',
    marco.baseline_emotion = 'dry skeptical calm',
    marco.created_at = datetime();

MERGE (voice1:Voice {id: 'voice_camille_canonical'})
SET voice1.description = 'American woman, early thirties, grounded, intimate microphone, controlled tension.',
    voice1.model = 'qwen3_tts_base',
    voice1.reference_transcript = 'I checked the schedule twice. Everything lines up, but I still do not trust him.',
    voice1.locked = true;

MERGE (voice2:Voice {id: 'voice_marco_canonical'})
SET voice2.description = 'American man, late thirties, dry humor, calm but skeptical, cinematic close microphone.',
    voice2.model = 'qwen3_tts_base',
    voice2.reference_transcript = 'That sounds like a terrible idea. But if you are going, I am going with you.',
    voice2.locked = true;

MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (voice1:Voice {id: 'voice_camille_canonical'})
MERGE (camille)-[:HAS_VOICE {role: 'canonical'}]->(voice1);

MATCH (marco:Character {id: 'char_marco_vale'})
MATCH (voice2:Voice {id: 'voice_marco_canonical'})
MERGE (marco)-[:HAS_VOICE {role: 'canonical'}]->(voice2);

MERGE (a1:Asset {id: 'asset_camille_voice_ref'})
SET a1.type = 'audio',
    a1.path = '/srv/nvme-data/containers/wan2gp/outputs/qwen3_tts_smoke/reference_voice.wav',
    a1.sample_rate = 24000,
    a1.channels = 1,
    a1.duration_seconds = 6.696875;

MERGE (a2:Asset {id: 'asset_marco_voice_ref'})
SET a2.type = 'audio',
    a2.path = '/srv/nvme-data/containers/wan2gp/outputs/qwen3_tts_smoke/reference_voice2.wav',
    a2.sample_rate = 24000,
    a2.channels = 1,
    a2.duration_seconds = 6.136875;

MATCH (voice1:Voice {id: 'voice_camille_canonical'})
MATCH (a1:Asset {id: 'asset_camille_voice_ref'})
MERGE (voice1)-[:HAS_ASSET {role: 'canonical_reference'}]->(a1);

MATCH (voice2:Voice {id: 'voice_marco_canonical'})
MATCH (a2:Asset {id: 'asset_marco_voice_ref'})
MERGE (voice2)-[:HAS_ASSET {role: 'canonical_reference'}]->(a2);

MERGE (t1:Trait {name: 'ambition'});
MERGE (t2:Trait {name: 'jealousy'});
MERGE (t3:Trait {name: 'risk_tolerance'});
MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (t1:Trait {name: 'ambition'})
MERGE (camille)-[:HAS_TRAIT {weight: 0.91}]->(t1);

MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (t2:Trait {name: 'jealousy'})
MERGE (camille)-[:HAS_TRAIT {weight: 0.88}]->(t2);

MATCH (marco:Character {id: 'char_marco_vale'})
MATCH (t3:Trait {name: 'risk_tolerance'})
MERGE (marco)-[:HAS_TRAIT {weight: 0.74}]->(t3);

MERGE (d_status:Desire {id: 'desire_status'})
SET d_status.name = 'status',
    d_status.description = 'Need to rise, be seen, and outrank rivals.';

MERGE (d_intimacy:Desire {id: 'desire_intimacy'})
SET d_intimacy.name = 'intimacy',
    d_intimacy.description = 'Need to be wanted, chosen, protected, or understood.';

MERGE (d_control:Desire {id: 'desire_control'})
SET d_control.name = 'control',
    d_control.description = 'Need to steer outcomes and avoid vulnerability.';

MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (d_status:Desire {id: 'desire_status'})
MERGE (camille)-[:HAS_DESIRE {weight: 0.94, conflict: 0.72}]->(d_status);

MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (d_intimacy:Desire {id: 'desire_intimacy'})
MERGE (camille)-[:HAS_DESIRE {weight: 0.82, conflict: 0.88}]->(d_intimacy);

MATCH (marco:Character {id: 'char_marco_vale'})
MATCH (d_control:Desire {id: 'desire_control'})
MERGE (marco)-[:HAS_DESIRE {weight: 0.76, conflict: 0.62}]->(d_control);

MATCH (marco:Character {id: 'char_marco_vale'})
MATCH (d_intimacy:Desire {id: 'desire_intimacy'})
MERGE (marco)-[:HAS_DESIRE {weight: 0.67, conflict: 0.71}]->(d_intimacy);

MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (marco:Character {id: 'char_marco_vale'})
MERGE (camille)-[r1:RELATES_TO]->(marco)
SET r1.type = 'romantic_tension',
    r1.attraction = 0.91,
    r1.trust = 0.22,
    r1.resentment = 0.63,
    r1.dependency = 0.50,
    r1.tension = 0.95,
    r1.fear_of_loss = 0.84,
    r1.power_imbalance = 0.31,
    r1.updated_at = datetime();

MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (marco:Character {id: 'char_marco_vale'})
MERGE (marco)-[r2:RELATES_TO]->(camille)
SET r2.type = 'romantic_tension',
    r2.attraction = 0.86,
    r2.trust = 0.41,
    r2.resentment = 0.27,
    r2.dependency = 0.32,
    r2.tension = 0.79,
    r2.fear_of_loss = 0.55,
    r2.power_imbalance = -0.31,
    r2.updated_at = datetime();

MERGE (arc:Arc {id: 'arc_first_betrayal'})
SET arc.title = 'The First Betrayal',
    arc.status = 'active',
    arc.tension = 0.64,
    arc.escalation_budget = 0.35,
    arc.cooldown_until = date('2026-01-03');

MERGE (secret:Secret {id: 'secret_marco_debt'})
SET secret.summary = 'Marco owes money to Camille’s quietest rival.',
    secret.visibility = 'hidden',
    secret.severity = 0.74,
    secret.created_at = datetime();

MATCH (marco:Character {id: 'char_marco_vale'})
MATCH (secret:Secret {id: 'secret_marco_debt'})
MERGE (marco)-[:OWNS_SECRET]->(secret);

MERGE (event:Event {id: 'event_0001_private_warning'})
SET event.type = 'PRIVATE_WARNING',
    event.summary = 'Camille warns Marco that she knows he is hiding something.',
    event.severity = 0.42,
    event.visibility = 0.10,
    event.world_time = datetime('2026-01-01T22:14:00'),
    event.created_at = datetime();

MATCH (camille:Character {id: 'char_camille_voss'})
MATCH (event:Event {id: 'event_0001_private_warning'})
MERGE (camille)-[:PARTICIPATED_IN {role: 'instigator'}]->(event);

MATCH (marco:Character {id: 'char_marco_vale'})
MATCH (event:Event {id: 'event_0001_private_warning'})
MERGE (marco)-[:PARTICIPATED_IN {role: 'target'}]->(event);

MATCH (event:Event {id: 'event_0001_private_warning'})
MATCH (arc:Arc {id: 'arc_first_betrayal'})
MERGE (event)-[:ADVANCES {amount: 0.12}]->(arc);

MATCH (event:Event {id: 'event_0001_private_warning'})
MATCH (camille:Character {id: 'char_camille_voss'})
MERGE (event)-[:AFFECTS {dimension: 'trust', delta: -0.08}]->(camille);

MATCH (event:Event {id: 'event_0001_private_warning'})
MATCH (marco:Character {id: 'char_marco_vale'})
MERGE (event)-[:AFFECTS {dimension: 'fear_of_exposure', delta: 0.18}]->(marco);
