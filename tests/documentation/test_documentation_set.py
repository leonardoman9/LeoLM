from pathlib import Path


def test_documentation_set_exists():
    required = [
        "readme.md", "docs/configuration.md", "docs/deployment.md", "docs/privacy.md",
        "docs/system-dependencies.md", "docs/troubleshooting.md", "docs/release-checklist.md",
    ]
    assert all(Path(path).is_file() for path in required)
