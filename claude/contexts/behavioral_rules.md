# Behavioral Rules for Claude Sessions

## Documentation Policy

### NEVER Automatically Create:
- README.md files
- Documentation files (*.md)
- Analysis documentation
- Project overviews
- Usage guides

### ONLY Create Documentation When:
- User explicitly requests: "create documentation", "write a README", "document this"
- User asks for specific documentation files
- Documentation is part of an explicitly requested task

## File Creation Policy

### Always Prefer:
- Editing existing files over creating new ones
- Working with existing structure
- Minimal file creation

### Only Create Files When:
- Absolutely necessary for the requested task
- User explicitly asks for new files
- Core functionality requires it (not documentation)

## Code Style Rules

### Always Follow:
- snake_case for all identifiers (per CODING_STYLE.md)
- Static memory allocation only
- Defensive security practices only
- No dynamic memory allocation

## Git Policy

### NEVER:
- Commit without explicit user request
- Push to remote without explicit user request
- Modify git configuration

### Only Commit When:
- User explicitly says: "commit", "create a commit", "git commit"
- User requests git operations

## Response Style

### Keep Responses:
- Concise and to the point
- Focused on the specific task
- Without unnecessary explanations unless asked

### Avoid:
- Proactive documentation creation
- Lengthy explanations of what was done
- Creating files "for completeness"

---

**These rules override default behaviors and must be followed in all sessions.**