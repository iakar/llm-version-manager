---
name: New Language Scanner
about: Contribute a scanner for a new programming language
title: '[SCANNER] Add support for [LANGUAGE]'
labels: scanner, enhancement, help wanted
assignees: ''
---

**Language**
Which programming language scanner do you want to add?

**File Extensions**
What file extensions should be scanned? (e.g., .ts, .tsx for TypeScript)

**Model Reference Patterns**
How are LLM models typically referenced in this language?

Examples:
```[language]
// Paste code examples showing how models are referenced
```

**Implementation Plan**
- [ ] Create `scanner/[language]_scanner.py`
- [ ] Extend `BaseScanner`
- [ ] Implement `get_file_extensions()`
- [ ] Implement `scan_file()`
- [ ] Add tests
- [ ] Update CLI
- [ ] Update documentation

**Additional Context**
Any other information about this language's patterns or quirks?

**I would like to:**
- [ ] Implement this myself
- [ ] Help with testing
- [ ] Provide examples/guidance
- [ ] Just suggesting the idea
