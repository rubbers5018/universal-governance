#!/usr/bin/env python3
"""
Governance Crypto Module - OpenPGP Integration for Mainscript.py
Adds OpenPGP signing to complement ECDSA for enhanced verification
"""

import subprocess
import json
import hashlib
import tempfile
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class OpenPGPSigner:
    """
    OpenPGP signing integration for PublicRegistrar
    Complements existing ECDSA signatures with GPG verification
    """

    def __init__(self, fingerprint: str = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"):
        """
        Initialize OpenPGP signer

        Args:
            fingerprint: Your GPG key fingerprint
        """
        self.fingerprint = fingerprint
        self.key_server = "keys.openpgp.org"
        self._verify_gpg_available()
        self._verify_key_exists()

    def _verify_gpg_available(self):
        """Verify GPG is installed"""
        try:
            result = subprocess.run(
                ['gpg', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("GPG not accessible")
        except FileNotFoundError:
            raise RuntimeError(
                "GPG not found. Install with: choco install gpg (Windows)"
            )

    def _verify_key_exists(self):
        """Verify the specified key exists"""
        result = subprocess.run(
            ['gpg', '--list-keys', self.fingerprint],
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Key {self.fingerprint} not found. "
                f"Import with: gpg --import your_key.asc"
            )

    def export_public_key(self) -> str:
        """Export public key in ASCII-armored format"""
        result = subprocess.run(
            ['gpg', '--export', '--armor', self.fingerprint],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Key export failed: {result.stderr}")
        return result.stdout

    def sign_data(self, data: str) -> str:
        """
        Create detached GPG signature for data

        Args:
            data: String data to sign (canonical JSON)

        Returns:
            ASCII-armored signature
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write data to temp file
            data_file = tmp_path / "data.json"
            data_file.write_text(data, encoding='utf-8')

            sig_file = tmp_path / "data.asc"

            # Sign with GPG
            result = subprocess.run(
                ['gpg', '--detach-sign', '--armor', '--output', str(sig_file),
                 '--local-user', self.fingerprint, str(data_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"Signing failed: {result.stderr}")

            return sig_file.read_text(encoding='utf-8')

    def verify_signature(self, data: str, signature: str) -> Tuple[bool, Dict]:
        """
        Verify a GPG signature

        Args:
            data: Original data
            signature: ASCII-armored signature

        Returns:
            (is_valid, verification_info)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            data_file = tmp_path / "data.json"
            data_file.write_text(data, encoding='utf-8')

            sig_file = tmp_path / "data.asc"
            sig_file.write_text(signature, encoding='utf-8')

            # Verify
            result = subprocess.run(
                ['gpg', '--verify', '--status-fd', '1', str(sig_file), str(data_file)],
                capture_output=True,
                text=True
            )

            # Parse output
            info = {'valid': False}
            for line in result.stdout.split('\n'):
                if '[GNUPG:] VALIDSIG' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        info['fingerprint'] = parts[2]
                        info['valid'] = True
                elif '[GNUPG:] GOODSIG' in line:
                    parts = line.split(' ', 3)
                    if len(parts) >= 4:
                        info['signer'] = parts[3]

            return result.returncode == 0, info


def add_openpgp_signature(entry: Dict, fingerprint: str = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79") -> Dict:
    """
    Add OpenPGP signature to a registration entry (in addition to ECDSA)

    Args:
        entry: Registration entry dict (must already have ECDSA signature)
        fingerprint: OpenPGP key fingerprint

    Returns:
        Entry with added openpgp_signature field
    """
    signer = OpenPGPSigner(fingerprint)

    # Create canonical JSON (excluding both signatures)
    entry_copy = {k: v for k, v in entry.items()
                  if k not in ['signature', 'openpgp_signature', 'openpgp_public_key']}
    canonical_data = json.dumps(entry_copy, sort_keys=True, separators=(',', ':'))

    # Sign with OpenPGP
    openpgp_sig = signer.sign_data(canonical_data)

    # Add to entry
    entry['openpgp_signature'] = openpgp_sig
    entry['openpgp_public_key'] = signer.export_public_key()
    entry['openpgp_fingerprint'] = fingerprint

    print(f"[OPENPGP] Signature added: {fingerprint[:16]}...")

    return entry


def verify_openpgp_signature(entry: Dict) -> bool:
    """
    Verify OpenPGP signature on a registration entry

    Args:
        entry: Registration entry with openpgp_signature

    Returns:
        True if signature is valid
    """
    if 'openpgp_signature' not in entry:
        print("[OPENPGP] No OpenPGP signature found")
        return False

    # Import public key if provided
    if 'openpgp_public_key' in entry:
        result = subprocess.run(
            ['gpg', '--import'],
            input=entry['openpgp_public_key'],
            capture_output=True,
            text=True
        )
        # Ignore warnings about already imported keys

    # Reconstruct canonical data (must match signing order exactly)
    entry_copy = {k: v for k, v in entry.items()
                  if k not in ['signature', 'openpgp_signature', 'openpgp_public_key', 'openpgp_fingerprint']}
    canonical_data = json.dumps(entry_copy, sort_keys=True, separators=(',', ':'))

    # Direct GPG verification without creating OpenPGPSigner
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        data_file = tmp_path / "data.json"
        data_file.write_text(canonical_data, encoding='utf-8')

        sig_file = tmp_path / "data.asc"
        sig_file.write_text(entry['openpgp_signature'], encoding='utf-8')

        # Verify
        result = subprocess.run(
            ['gpg', '--verify', '--status-fd', '1', str(sig_file), str(data_file)],
            capture_output=True,
            text=True
        )

        # Parse output
        info = {'valid': False}
        for line in result.stdout.split('\n'):
            if '[GNUPG:] VALIDSIG' in line:
                parts = line.split()
                if len(parts) >= 3:
                    info['fingerprint'] = parts[2]
                    info['valid'] = True
            elif '[GNUPG:] GOODSIG' in line:
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    info['signer'] = parts[3]

        is_valid = result.returncode == 0

        if is_valid:
            print(f"[OPENPGP VERIFY] ✅ Valid signature from {info.get('signer', 'Unknown')}")
        else:
            print(f"[OPENPGP VERIFY] ❌ Invalid signature")

        return is_valid


# Convenience function for mainscript integration
def create_dual_signed_entry(entry: Dict, fingerprint: str = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79") -> Dict:
    """
    Create entry with both ECDSA and OpenPGP signatures

    Args:
        entry: Entry that already has ECDSA signature
        fingerprint: OpenPGP key fingerprint

    Returns:
        Entry with dual signatures
    """
    return add_openpgp_signature(entry, fingerprint)


def verify_dual_signatures(entry: Dict) -> Tuple[bool, bool]:
    """
    Verify both ECDSA and OpenPGP signatures

    Args:
        entry: Registration entry with dual signatures

    Returns:
        (ecdsa_valid, openpgp_valid)
    """
    # ECDSA verification (from mainscript's verify_registration method)
    ecdsa_valid = False
    try:
        import ecdsa
        from ecdsa import SECP256k1
        ser = json.dumps({k: v for k, v in entry.items()
                         if k not in ['signature', 'openpgp_signature', 'openpgp_public_key']},
                        sort_keys=True).encode()
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(entry['public_key']), curve=SECP256k1)
        vk.verify(bytes.fromhex(entry['signature']), ser, hashfunc=hashlib.sha256)
        ecdsa_valid = True
        print("[ECDSA VERIFY] ✅ Valid")
    except Exception as e:
        print(f"[ECDSA VERIFY] ❌ Invalid: {e}")

    # OpenPGP verification
    openpgp_valid = verify_openpgp_signature(entry)

    return ecdsa_valid, openpgp_valid


if __name__ == '__main__':
    print("=" * 70)
    print("Governance Crypto - OpenPGP Integration Test")
    print("=" * 70)

    # Test with a sample entry
    sample_entry = {
        'proof_name': 'test_proof',
        'timestamp': 1234567890,
        'data': {'test': 'data'}
    }

    print("\n1. Testing OpenPGP signing...")
    try:
        signed_entry = add_openpgp_signature(sample_entry)
        print("✅ Signing successful")

        print("\n2. Testing OpenPGP verification...")
        is_valid = verify_openpgp_signature(signed_entry)
        if is_valid:
            print("✅ Verification successful")
        else:
            print("❌ Verification failed")

    except Exception as e:
        print(f"❌ Test failed: {e}")
