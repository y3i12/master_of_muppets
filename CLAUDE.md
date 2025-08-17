# CLAUDE.md - Minimal Bootstrap

## Quick Start
**Load cognitive state first**: `claude/cognitive_cache.cc` (lines 1-20)
**Then query as needed**: `python claude/cognitive_ops.py q [path]`

## Cognitive System Files
- `claude/cognitive_cache.cc` - Instant mental state (20 lines)
- `claude/cognitive_core.json` - Full knowledge index
- `claude/cognitive_ops.py` - Query/update API
- `claude/COGNITIVE_SYSTEM.md` - System documentation

## Critical Reminders
- **Project**: Master of Muppets - USB MIDI to 16ch CV (0-10V) on Teensy 4.1
- **Style**: snake_case always (see CODING_STYLE.md)
- **Security**: Defensive only, no malicious code
- **Memory**: Static allocation only, no dynamic
- **Git**: Never commit without explicit request

## Session Protocol
- Check git branch for season (branch name = season)
- Episodes in `claude/sessions/season_XX/episode_YY_name.md`
- Update episode with "update episode", create with "write episode"

## Tools Available
- `claude/tools/kicad_parser.py` - 900x faster schematic parsing
- `claude/hardware_graph/` - Component relationships
- `claude/codebase_graph/` - Code structure

**All other knowledge encoded in cognitive_core.json - query as needed**