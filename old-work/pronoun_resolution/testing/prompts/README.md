# Pronoun Resolution Prompt Set

This folder contains the planned batch-labeling prompts for the pronoun-resolution prompt-engineering study.

## Prompt files
- `P0_base_zero_shot.md`
- `P1_two_shot.md`
- `P2_four_shot.md`
- `P3_decomposed_candidate_tracking.md`
- `P4_expanded_definition.md`
- `claude_code_repo_restructure_instruction.md`

## Notes
- All prompts preserve the same CSV-in / CSV-out scaffold.
- All prompts preserve the same output schema: `item_id,answer`.
- All prompts preserve the same anti-external-resource instruction.
- `P2_four_shot.md` is included; no 6-shot condition is included.
