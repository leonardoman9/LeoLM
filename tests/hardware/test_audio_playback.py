"""Opt-in playback check; it never installs packages or uses sudo."""

import shutil

import pytest

pytestmark = pytest.mark.hardware


def test_player_is_installed():
    assert shutil.which("mpg123") or shutil.which("aplay"), "Install a configured audio player first"
