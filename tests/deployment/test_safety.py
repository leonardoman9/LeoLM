from pathlib import Path

import pytest

from leolm.deployment.errors import TargetError
from leolm.deployment.offline import OfflineProvisioner
from leolm.deployment.profile import DeviceProfile


def test_invalid_target_is_rejected_before_write(tmp_path):
    profile = DeviceProfile({}, Path("profile.env"))
    with pytest.raises(Exception):
        OfflineProvisioner(tmp_path / "missing").provision(profile)
