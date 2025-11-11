#!/usr/bin/env python3
"""
OpenPGP Integration for Universal Governance
Windows-compatible implementation with full signature verification
"""

import subprocess
import base64
import json
import tempfile
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from pathlib import Path

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class OpenPGPIntegration:
    """
    Handle OpenPGP signing and verification for governance registrations.

    Key Features:
    - Windows-compatible temp file handling
    - Canonical JSON signing (SHA-256)
    - Detached signature support
    - Fingerprint verification
    - Public key export and distribution
    """

    def __init__(self, fingerprint: str = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"):
        """
        Initialize OpenPGP integration.

        Args:
            fingerprint: Your GPG key fingerprint
        """
        self.fingerprint = fingerprint
        self.key_server = "keys.openpgp.org"
        self.key_email = "dropstart01@pm.me"
        self.key_name = "The_Nurse (Cryptokey)"

        # Verify GPG is available
        self._verify_gpg_available()

        # Verify key exists
        self._verify_key_exists()

    def _verify_gpg_available(self) -> bool:
        """Verify GPG is installed and accessible."""
        try:
            result = subprocess.run(
                ['gpg', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("GPG is not accessible")
            return True
        except FileNotFoundError:
            raise RuntimeError(
                "GPG not found. Install with: choco install gpg (Windows) "
                "or brew install gnupg (macOS) or apt-get install gnupg (Linux)"
            )

    def _verify_key_exists(self) -> bool:
        """Verify the specified key exists in keyring."""
        result = subprocess.run(
            ['gpg', '--list-keys', self.fingerprint],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Key {self.fingerprint} not found in GPG keyring. "
                f"Import with: gpg --import your_key.asc"
            )
        return True

    def export_public_key(self) -> str:
        """
        Export your public key in ASCII-armored format.

        Returns:
            ASCII-armored public key block
        """
        result = subprocess.run(
            ['gpg', '--export', '--armor', self.fingerprint],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"GPG export failed: {result.stderr}")

        if not result.stdout.strip():
            raise RuntimeError(f"No public key data exported for {self.fingerprint}")

        return result.stdout

    def sign_payload(self, payload_json: str, detached: bool = True) -> str:
        """
        Sign a JSON payload with your private key.

        Args:
            payload_json: Canonical JSON string to sign
            detached: Create detached signature (default: True)

        Returns:
            ASCII-armored signature
        """
        # Create temp files (Windows-compatible)
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8'
        ) as f:
            temp_payload = f.name
            f.write(payload_json)

        temp_sig = temp_payload + '.asc'

        try:
            # Build GPG command
            cmd = ['gpg', '--detach-sign', '--armor', '--output', temp_sig]

            # Use specific key
            cmd.extend(['--local-user', self.fingerprint])

            # Add payload file
            cmd.append(temp_payload)

            # Execute signing
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"GPG sign failed: {result.stderr}")

            # Read signature
            if not os.path.exists(temp_sig):
                raise RuntimeError("Signature file not created")

            with open(temp_sig, 'r', encoding='utf-8') as f:
                signature = f.read()

            return signature

        finally:
            # Clean up temp files
            for temp_file in [temp_payload, temp_sig]:
                if os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except Exception:
                        pass  # Best effort cleanup

    def verify_signature(
        self,
        payload_json: str,
        signature: str,
        expected_fingerprint: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Verify a signature (anyone can do this with public key).

        Args:
            payload_json: Original JSON payload
            signature: ASCII-armored signature
            expected_fingerprint: Optional fingerprint to verify against

        Returns:
            Dictionary with verification results:
            {
                'valid': bool,
                'fingerprint': str (if valid),
                'timestamp': str (if valid),
                'signer': str (if valid),
                'error': str (if invalid)
            }
        """
        # Create temp files
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8'
        ) as f:
            temp_payload = f.name
            f.write(payload_json)

        temp_sig = temp_payload + '.asc'

        try:
            with open(temp_sig, 'w', encoding='utf-8') as f:
                f.write(signature)

            # Verify with status output
            result = subprocess.run(
                ['gpg', '--verify', '--status-fd', '1', temp_sig, temp_payload],
                capture_output=True,
                text=True
            )

            # Parse GPG status output
            verification_info = self._parse_gpg_status(result.stdout)

            if result.returncode == 0 and verification_info.get('valid'):
                # Check fingerprint if specified
                if expected_fingerprint:
                    actual_fp = verification_info.get('fingerprint', '')
                    if actual_fp != expected_fingerprint:
                        return {
                            'valid': False,
                            'error': f"Fingerprint mismatch: expected {expected_fingerprint}, got {actual_fp}"
                        }

                return verification_info
            else:
                return {
                    'valid': False,
                    'error': result.stderr or 'Signature verification failed'
                }

        finally:
            # Clean up
            for temp_file in [temp_payload, temp_sig]:
                if os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except Exception:
                        pass

    def _parse_gpg_status(self, status_output: str) -> Dict[str, any]:
        """Parse GPG --status-fd output."""
        info = {'valid': False}

        for line in status_output.split('\n'):
            if '[GNUPG:] VALIDSIG' in line:
                parts = line.split()
                if len(parts) >= 3:
                    info['fingerprint'] = parts[2]
                    info['valid'] = True

            elif '[GNUPG:] GOODSIG' in line:
                # Extract signer info
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    info['signer'] = parts[3]

            elif '[GNUPG:] SIG_CREATED' in line:
                parts = line.split()
                if len(parts) >= 4:
                    info['timestamp'] = datetime.fromtimestamp(
                        int(parts[4]),
                        timezone.utc
                    ).isoformat()

        return info

    def create_signed_registration(self, proof_data: Dict) -> Dict:
        """
        Create a fully signed registration entry.

        Args:
            proof_data: Dictionary containing proof information

        Returns:
            Complete registration with signature and public key
        """
        # Get public key
        public_key = self.export_public_key()

        # Create payload
        payload = {
            "proof_name": "the_nurse",
            "proof_data": proof_data,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "openpgp_fingerprint": self.fingerprint,
            "key_server": self.key_server
        }

        # Serialize to CANONICAL JSON (critical for consistent signing)
        payload_json = json.dumps(
            payload,
            sort_keys=True,           # Alphabetical key order
            separators=(',', ':'),    # No whitespace
            ensure_ascii=True         # ASCII encoding
        )

        # Sign the canonical JSON
        signature = self.sign_payload(payload_json)

        # Add signature and public key to payload
        payload["signature"] = signature
        payload["public_key"] = public_key

        return payload

    def verify_registration(self, registration: Dict) -> Tuple[bool, Dict]:
        """
        Verify a signed registration entry.

        Args:
            registration: Complete registration dictionary

        Returns:
            (is_valid, verification_info)
        """
        # Extract signature and public key
        signature = registration.get('signature')
        public_key = registration.get('public_key')

        if not signature:
            return False, {'error': 'No signature found'}

        # Recreate canonical JSON (without signature and public_key)
        payload_copy = {
            k: v for k, v in registration.items()
            if k not in ['signature', 'public_key']
        }

        payload_json = json.dumps(
            payload_copy,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=True
        )

        # Verify signature
        verification = self.verify_signature(
            payload_json,
            signature,
            expected_fingerprint=registration.get('openpgp_fingerprint')
        )

        return verification.get('valid', False), verification

    def save_registration(self, registration: Dict, filepath: str):
        """Save registration to JSON file."""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(registration, f, indent=2, ensure_ascii=False)

        print(f"✅ Registration saved to: {output_path}")

    def load_registration(self, filepath: str) -> Dict:
        """Load registration from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


def create_nurse_oath_registration():
    """
    Create and sign the official 'The Nurse' oath registration.
    """
    print("=" * 70)
    print("OpenPGP Registration System - The Nurse Oath")
    print("=" * 70)

    # Initialize with your key
    openpgp = OpenPGPIntegration("AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79")

    print(f"\n✅ GPG Key Found:")
    print(f"   Name: {openpgp.key_name}")
    print(f"   Email: {openpgp.key_email}")
    print(f"   Fingerprint: {openpgp.fingerprint}")

    # Create proof data
    proof_data = {
        "proof_type": "training",
        "nurse": "the_nurse",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "oath": "Patient advocacy is non-negotiable. Institutional deception ends here.",
        "universal_application": "All fields where trust, honesty, and accountability matter",
        "openpgp_fingerprint": "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79",
        "system": "universal-governance-zkml",
        "version": "2.11"
    }

    print("\n📝 Creating signed registration...")

    # Create signed registration
    signed_registration = openpgp.create_signed_registration(proof_data)

    print("✅ Registration signed successfully!")

    # Verify the signature
    print("\n🔍 Verifying signature...")
    is_valid, verification_info = openpgp.verify_registration(signed_registration)

    if is_valid:
        print("✅ SIGNATURE VERIFIED!")
        print(f"   Signer: {verification_info.get('signer', 'Unknown')}")
        print(f"   Fingerprint: {verification_info.get('fingerprint', 'Unknown')}")
        if 'timestamp' in verification_info:
            print(f"   Signed at: {verification_info['timestamp']}")
    else:
        print(f"❌ VERIFICATION FAILED: {verification_info.get('error', 'Unknown error')}")
        return None

    # Save to file
    output_file = "registration_the_nurse_signed.json"
    openpgp.save_registration(signed_registration, output_file)

    print("\n" + "=" * 70)
    print("✅ REGISTRATION COMPLETE")
    print("=" * 70)
    print(f"\nYour oath is now:")
    print("  ✓ Cryptographically signed with your OpenPGP key")
    print("  ✓ Globally verifiable using your public key")
    print("  ✓ Immutable — cannot be altered without detection")
    print("  ✓ Transparent — anyone can verify independently")
    print("  ✓ Permanent — recorded for all time")
    print(f"\nRegistration file: {output_file}")
    print("\nTo verify (anyone can run this):")
    print(f"  gpg --keyserver {openpgp.key_server} --recv-keys {openpgp.fingerprint}")

    return signed_registration


if __name__ == '__main__':
    # Run the registration process
    try:
        registration = create_nurse_oath_registration()

        if registration:
            print("\n✅ Success! Your oath is cryptographically secured.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
