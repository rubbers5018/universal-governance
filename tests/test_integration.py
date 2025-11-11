#!/usr/bin/env python3
"""
Integration Test for Universal Governance

Tests the complete workflow:
1. Load The Nurse's registration
2. Verify signature
3. List members
4. Submit a proposal

This test must pass before any production deployment.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from governance_crypto import verify_openpgp_signature
from mainscript import PublicRegistrar


def test_the_nurse_registration():
    """Test 1: Verify The Nurse's registration"""
    print("\n[TEST 1] Verifying The Nurse's registration...")

    reg_file = Path(__file__).parent.parent / 'registrations' / 'examples' / 'reg_AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79.json'

    assert reg_file.exists(), f"Registration file not found: {reg_file}"

    with open(reg_file, 'r') as f:
        registration = json.load(f)

    # Verify signature
    is_valid = verify_openpgp_signature(registration)

    assert is_valid, "The Nurse's signature verification failed"
    print("✅ The Nurse's registration verified")


def test_list_members():
    """Test 2: List all registered members"""
    print("\n[TEST 2] Listing registered members...")

    reg_dir = Path(__file__).parent.parent / 'registrations' / 'examples'
    registrar = PublicRegistrar(reg_dir=str(reg_dir))

    members = registrar.list_members()

    assert len(members) > 0, "No members found"
    assert any(m['proof_name'] == 'the_nurse' for m in members), "The Nurse not in member list"
    assert all(m['verified'] for m in members), "Not all members verified"

    print(f"✅ Found {len(members)} verified member(s)")


def test_identity_verification():
    """Test 3: Verify identity by fingerprint"""
    print("\n[TEST 3] Testing identity verification...")

    reg_dir = Path(__file__).parent.parent / 'registrations' / 'examples'
    registrar = PublicRegistrar(reg_dir=str(reg_dir))

    fingerprint = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"

    # First verification
    is_valid = registrar.verify_identity(fingerprint)
    assert is_valid, "Identity verification failed"

    # Second verification (should use cache)
    is_valid_cached = registrar.verify_identity(fingerprint)
    assert is_valid_cached, "Cached identity verification failed"

    print("✅ Identity verification working (including cache)")


def test_proposal_submission():
    """Test 4: Submit a governance proposal"""
    print("\n[TEST 4] Testing proposal submission...")

    reg_dir = Path(__file__).parent.parent / 'registrations' / 'examples'
    registrar = PublicRegistrar(reg_dir=str(reg_dir))

    fingerprint = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"

    proposal = {
        "title": "Test Proposal",
        "description": "Integration test proposal",
        "test": True
    }

    result = registrar.submit_proposal(proposal, fingerprint)

    assert result is not None, "Proposal submission failed"
    assert 'proposal_id' in result, "Proposal ID not in result"
    assert result['submitted_by'] == fingerprint, "Incorrect submitter"

    # Verify proposal file was created
    proposal_file = Path('governance/proposals') / f"proposal_{result['proposal_id']}.json"
    assert proposal_file.exists(), f"Proposal file not created: {proposal_file}"

    # Clean up test proposal
    proposal_file.unlink()
    print(f"✅ Proposal submission working (ID: {result['proposal_id']})")


def main():
    """Run all integration tests"""
    print("=" * 70)
    print("INTEGRATION TESTS - Universal Governance")
    print("=" * 70)

    tests = [
        test_the_nurse_registration,
        test_list_members,
        test_identity_verification,
        test_proposal_submission
    ]

    failed = []

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed.append(test.__name__)

    # Summary
    print("\n" + "=" * 70)
    if failed:
        print(f"❌ FAILED: {len(failed)}/{len(tests)} tests")
        for name in failed:
            print(f"   - {name}")
        print("=" * 70)
        sys.exit(1)
    else:
        print(f"✅ SUCCESS: All {len(tests)} integration tests passed")
        print("=" * 70)
        print("\nRepository is production-ready!")
        sys.exit(0)


if __name__ == '__main__':
    main()
