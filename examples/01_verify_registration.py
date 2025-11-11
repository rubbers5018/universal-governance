#!/usr/bin/env python3
"""
Example 01: Verify The Nurse's Registration

Demonstrates cryptographic verification of a real-world identity attestation.
This example loads The Nurse's Oath and verifies the OpenPGP signature.
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from governance_crypto import verify_openpgp_signature


def main():
    print("=" * 70)
    print("Example 01: Verify The Nurse's Registration")
    print("=" * 70)
    print()

    # Path to The Nurse's registration
    reg_file = Path(__file__).parent.parent / 'registrations' / 'examples' / 'reg_AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79.json'

    if not reg_file.exists():
        print(f"❌ ERROR: Registration file not found: {reg_file}")
        print("   Please ensure the repository is complete.")
        sys.exit(1)

    # Load registration
    print(f"Loading registration: {reg_file.name}")
    with open(reg_file, 'r') as f:
        registration = json.load(f)

    # Display oath
    oath = registration.get('proof_data', {}).get('oath', 'Unknown')
    print(f"\n📜 The Nurse's Oath:")
    print(f'   "{oath}"')
    print()

    # Verify OpenPGP signature
    print("🔍 Verifying OpenPGP signature...")
    print()

    try:
        is_valid = verify_openpgp_signature(registration)

        if is_valid:
            print()
            print("=" * 70)
            print("✅ VERIFICATION SUCCESSFUL")
            print("=" * 70)
            print("The Nurse's Oath is cryptographically verified!")
            print(f"Fingerprint: {registration.get('openpgp_fingerprint', 'Unknown')}")
            print()
            print("This demonstrates a real-world commitment to patient advocacy,")
            print("verified without relying on institutional gatekeepers.")
            print("=" * 70)
            sys.exit(0)
        else:
            print()
            print("❌ VERIFICATION FAILED")
            print("The signature could not be verified.")
            print("This may indicate:")
            print("  - GPG key not imported")
            print("  - Signature corruption")
            print("  - Tampered registration file")
            print()
            print("Try importing the key first:")
            print("  gpg --keyserver keys.openpgp.org --recv-keys AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nEnsure GPG is installed and The Nurse's key is imported.")
        sys.exit(1)


if __name__ == '__main__':
    main()
