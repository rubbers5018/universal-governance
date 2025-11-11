#!/usr/bin/env python3
"""
Example 02: List All Verified Members

Demonstrates batch verification of registered identities.
Scans the registration directory and verifies all signatures.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mainscript import PublicRegistrar


def main():
    print("=" * 70)
    print("Example 02: List All Verified Members")
    print("=" * 70)
    print()

    # Initialize registrar
    reg_dir = Path(__file__).parent.parent / 'registrations' / 'examples'
    registrar = PublicRegistrar(reg_dir=str(reg_dir))

    # List all members
    print(f"Scanning registration directory: {reg_dir}")
    print()

    members = registrar.list_members()

    if not members:
        print("No registered members found.")
        sys.exit(0)

    # Display results
    print(f"Found {len(members)} registration(s):")
    print()

    verified_count = 0
    for member in members:
        status = "✅ VERIFIED" if member['verified'] else "❌ INVALID"
        print(f"{status}: {member['proof_name']}")
        print(f"  Fingerprint: {member['openpgp_fingerprint']}")
        print(f"  Timestamp:   {member['timestamp']}")
        print(f"  File:        {member['file']}")
        print()

        if member['verified']:
            verified_count += 1

    # Summary
    print("=" * 70)
    print(f"Total members: {len(members)}")
    print(f"Verified: {verified_count}")
    print(f"Invalid:  {len(members) - verified_count}")
    print("=" * 70)

    # Exit with appropriate code
    sys.exit(0 if verified_count == len(members) else 1)


if __name__ == '__main__':
    main()
