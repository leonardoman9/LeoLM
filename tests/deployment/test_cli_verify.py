import importlib.util
from pathlib import Path
import sys


def load_cli():
    path = Path("scripts/leolm-deploy.py")
    spec = importlib.util.spec_from_file_location("leolm_deploy", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_verify_accepts_the_target_ssh_user():
    args = load_cli().parser().parse_args([
        "verify", "--profile", "profile.env", "--target", "raspberry-bo", "--user", "leonardo",
    ])
    assert args.user == "leonardo"


def test_deploy_ssh_accepts_verbose_progress():
    args = load_cli().parser().parse_args([
        "deploy-ssh", "--profile", "profile.env", "--host", "raspberry-bo", "--verbose",
    ])
    assert args.verbose is True
