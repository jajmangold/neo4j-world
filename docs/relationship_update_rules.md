# Relationship Update Rules

Relationship drama lives on directed `RELATES_TO` edges between characters.

## Edge Fields

- `type`
- `attraction`
- `trust`
- `resentment`
- `dependency`
- `tension`
- `fear_of_loss`
- `power_imbalance`
- `updated_at`

Values are normally `0.0` to `1.0`, except `power_imbalance`, which may be negative.

## Example Deltas

`BETRAYAL`

- trust: `-0.15` to `-0.45`
- resentment: `+0.15` to `+0.50`
- tension: `+0.05` to `+0.25`
- fear_of_loss: depends on attachment style

`NEAR_KISS`

- attraction: `+0.05` to `+0.20`
- tension: `+0.10` to `+0.30`
- trust: `-0.05` to `+0.05`, depending on context

`PUBLIC_HUMILIATION`

- trust toward instigator: `-0.20` to `-0.50`
- resentment: `+0.25` to `+0.60`
- dependency: may rise if the target has few allies

`RECONCILIATION`

- trust: `+0.05` to `+0.20`
- resentment: `-0.05` to `-0.20`
- tension: may stay high if attraction is unresolved

## Governor Rule

Never max out every edge value. Leave room for escalation and reversal.

