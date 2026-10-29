# Documentation release checklist

- [ ] Run `python scripts/check_docs.py --root . --json` without network access or real credentials.
- [ ] Run `pytest tests/documentation -q` and the complete automatic suite.
- [ ] Verify the README, configuration, deployment, privacy, dependencies, and troubleshooting docs.
- [ ] Verify local links, commands, paths, profiles, and dependencies in an isolated environment or equivalent tests.
- [ ] Verify public templates and profiles contain no API keys, Wi-Fi passwords, tokens, or audio.
- [ ] Verify timeout/retry behavior, the 600-second context, audio cleanup, and provider limits.
- [ ] Run the opt-in hardware tests separately before distributing images.
- [ ] Confirm MCP is documented as out of scope until a verified integration exists.
