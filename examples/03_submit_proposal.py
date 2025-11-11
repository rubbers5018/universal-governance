#!/usr/bin/env python3
"""
Example 03: Submit a Governance Proposal

Demonstrates the @require_verified_identity decorator and proposal submission.
This shows how governance operations require cryptographic identity verification.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mainscript import PublicRegistrar, require_verified_identity


# Example function protected by identity verification
@require_verified_identity("AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79")
def perform_governance_action():
    """
    This function requires a verified identity to execute.
    Without valid signature verification, it will raise PermissionError.
    """
    return "Governance action authorized!"


def main():
    print("=" * 70)
    print("Example 03: Submit a Governance Proposal")
    print("=" * 70)
    print()

    # Initialize registrar
    reg_dir = Path(__file__).parent.parent / 'registrations' / 'examples'
    registrar = PublicRegistrar(reg_dir=str(reg_dir))

    # The Nurse's fingerprint
    fingerprint = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"

    # Create a sample proposal
    proposal = {
        "title": "Proposal: Implement Patient Advocacy Framework",
        "description": "Establish guidelines for patient advocacy in healthcare settings.",
        "rationale": "Current systems lack transparent accountability mechanisms.",
        "proposed_by": fingerprint
    }

    print("📋 Proposal Details:")
    print(f"   Title: {proposal['title']}")
    print(f"   Proposed by: {fingerprint[:16]}...")
    print()

    # Submit proposal (requires verified identity)
    print("🔍 Verifying identity before submission...")
    result = registrar.submit_proposal(proposal, fingerprint)

    if result:
        print()
        print("=" * 70)
        print("✅ PROPOSAL SUBMITTED SUCCESSFULLY")
        print("=" * 70)
        print(f"Proposal ID: {result['proposal_id']}")
        print(f"Timestamp:   {result['timestamp']}")
        print()
        print("The proposal has been cryptographically signed and recorded.")
        print("This demonstrates governance with verifiable accountability.")
        print("=" * 70)
        print()

        # Demonstrate decorator usage
        print("🔐 Testing @require_verified_identity decorator...")
        try:
            message = perform_governance_action()
            print(f"✅ {message}")
        except PermissionError as e:
            print(f"❌ {e}")

        sys.exit(0)
    else:
        print("\n❌ PROPOSAL SUBMISSION FAILED")
        print("Identity verification failed or other error occurred.")
        sys.exit(1)


if __name__ == '__main__':
    main()
