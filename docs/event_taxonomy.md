# Event Taxonomy

Events are the durable consequence layer. They should be typed, dated in world time, linked to participants, and converted into relationship/state deltas.

## Core Event Types

- `AFFAIR_DISCOVERED`
- `SECRET_REVEALED`
- `PUBLIC_HUMILIATION`
- `BETRAYAL`
- `RECONCILIATION`
- `STATUS_GAIN`
- `STATUS_LOSS`
- `FINANCIAL_SHOCK`
- `FAMILY_RUPTURE`
- `NEAR_KISS`
- `PRIVATE_WARNING`
- `BLACKMAIL_ATTEMPT`
- `CAREER_OPPORTUNITY`
- `SOCIAL_EXCLUSION`
- `LOYALTY_TEST`

## Required Fields

- `id`
- `type`
- `summary`
- `world_time`
- `severity`: `0.0` to `1.0`
- `visibility`: `0.0` private to `1.0` public
- `participants`
- `arc_ids`
- `relationship_deltas`
- `reputation_deltas`
- `secret_updates`

## Event Quality Rule

An event is only worth recording if it changes at least one durable state:

- relationship edge values
- reputation
- secret visibility
- arc progress
- character memory
- visual/voice state

