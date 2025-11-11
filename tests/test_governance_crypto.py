import json
import pytest
from unittest.mock import patch

from src.governance_crypto import verify_openpgp_signature, OpenPGPSigner


@patch("subprocess.run")
def test_verify_signature_valid(mock_run):
    mock_run.return_value.stdout = "Good signature"
    mock_run.return_value.returncode = 0
    assert verify_openpgp_signature("message", "signature") is True


@patch("subprocess.run")
def test_verify_signature_invalid(mock_run):
    mock_run.return_value.stdout = "Bad signature"
    mock_run.return_value.returncode = 1
    assert verify_openpgp_signature("message", "signature") is False


@patch("subprocess.run", side_effect=FileNotFoundError)
def test_verify_signature_gpg_missing(_):
    with pytest.raises(FileNotFoundError):
        verify_openpgp_signature("msg", "sig")


@patch("subprocess.run")
def test_signer_sign(mock_run):
    mock_run.return_value.stdout = "fake_signature"
    signer = OpenPGPSigner("FAKE_KEY", verify=False)  # ✅ prevents real GPG lookup
    sig = signer.sign("hello world")                  # ✅ wrapper added in class
    assert sig == "fake_signature"


def test_canonical_json():
    data = {"b": 2, "a": 1}
    json_output = OpenPGPSigner.canonical_json(data)
    assert json_output == json.dumps({"a": 1, "b": 2}, separators=(",", ":"), sort_keys=True)
