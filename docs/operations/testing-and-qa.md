# Testing and QA

## Minimum checks before enabling or changing an agent
- config files parse successfully
- output schema passes validation
- required destination channels exist
- token caps are defined
- source integrations return expected fields
- sample output renders correctly in the portal structure

## Minimum checks before release
- `python scripts/validate_pack.py`
- manual review of architecture diff
- verify changelog update
- verify schedules and routing config remain aligned
