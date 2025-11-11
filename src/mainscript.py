#!/usr/bin/env python3
"""
Universal Governance - Main Governance Engine
Provides PublicRegistrar for cryptographic identity verification and governance operations
"""

import argparse
import json
import os
import sys
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import wraps, lru_cache

# Import governance crypto module
from governance_crypto import verify_openpgp_signature, OpenPGPSigner


class PublicRegistrar:
    """
    Public Registration system for governance identities
    Manages cryptographic identity verification and governance operations
    """

    def __init__(self, reg_dir: str = './registrations/examples'):
        """
        Initialize PublicRegistrar

        Args:
            reg_dir: Directory containing registration files
        """
        self.reg_dir = Path(reg_dir)
        self.reg_dir.mkdir(parents=True, exist_ok=True)
        self._verified_cache: Dict[str, Dict[str, Any]] = {}

    @lru_cache(maxsize=128)
    def _load_registration(self, fingerprint: str) -> Optional[Dict]:
        """
        Load a registration file by fingerprint (cached)

        Args:
            fingerprint: OpenPGP fingerprint

        Returns:
            Registration dict or None if not found
        """
        reg_file = self.reg_dir / f"reg_{fingerprint}.json"
        if not reg_file.exists():
            return None

        try:
            with open(reg_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load registration: {e}")
            return None

    def verify_identity(self, fingerprint: str) -> bool:
        """
        Verify an identity by OpenPGP fingerprint

        Args:
            fingerprint: OpenPGP fingerprint to verify

        Returns:
            True if identity is cryptographically verified
        """
        # Check cache first
        if fingerprint in self._verified_cache:
            print(f"[CACHE HIT] Identity {fingerprint[:16]}... already verified")
            return True

        # Load registration
        registration = self._load_registration(fingerprint)
        if not registration:
            print(f"[VERIFY FAIL] No registration found for {fingerprint}")
            return False

        # Verify OpenPGP signature
        is_valid = verify_openpgp_signature(registration)

        if is_valid:
            # Cache the verified identity
            self._verified_cache[fingerprint] = registration
            print(f"[VERIFY SUCCESS] Identity {fingerprint[:16]}... verified and cached")
            return True
        else:
            print(f"[VERIFY FAIL] Signature verification failed for {fingerprint}")
            return False

    def list_members(self) -> List[Dict[str, str]]:
        """
        List all registered members with verified identities

        Returns:
            List of member info dicts
        """
        members = []

        # Scan registration directory
        for reg_file in self.reg_dir.glob("reg_*.json"):
            try:
                with open(reg_file, 'r') as f:
                    registration = json.load(f)

                # Extract member info
                member_info = {
                    'proof_name': registration.get('proof_name', 'Unknown'),
                    'openpgp_fingerprint': registration.get('openpgp_fingerprint', ''),
                    'timestamp': registration.get('timestamp', 0),
                    'file': str(reg_file.name)
                }

                # Verify signature
                if verify_openpgp_signature(registration):
                    member_info['verified'] = True
                    members.append(member_info)
                else:
                    member_info['verified'] = False
                    print(f"[WARNING] Member {member_info['proof_name']} has invalid signature")

            except Exception as e:
                print(f"[ERROR] Failed to process {reg_file}: {e}")

        return members

    def register_member(self, registration_data: Dict, fingerprint: str) -> bool:
        """
        Register a new member (must have valid OpenPGP signature)

        Args:
            registration_data: Registration entry with signature
            fingerprint: OpenPGP fingerprint

        Returns:
            True if registration successful
        """
        # Verify signature first
        if not verify_openpgp_signature(registration_data):
            print("[REGISTER FAIL] Invalid signature - cannot register")
            return False

        # Save registration file
        reg_file = self.reg_dir / f"reg_{fingerprint}.json"

        try:
            with open(reg_file, 'w') as f:
                json.dump(registration_data, f, indent=2)

            print(f"[REGISTER SUCCESS] Member registered: {reg_file}")
            return True

        except Exception as e:
            print(f"[REGISTER FAIL] Failed to save registration: {e}")
            return False

    def submit_proposal(self, proposal: Dict, fingerprint: str) -> Optional[Dict]:
        """
        Submit a governance proposal (requires verified identity)

        Args:
            proposal: Proposal data dict
            fingerprint: Submitter's fingerprint

        Returns:
            Proposal metadata if successful, None otherwise
        """
        # Verify identity first
        if not self.verify_identity(fingerprint):
            print("[PROPOSAL FAIL] Identity not verified - cannot submit proposal")
            return None

        # Create proposal file
        proposals_dir = Path('./governance/proposals')
        proposals_dir.mkdir(parents=True, exist_ok=True)

        proposal_id = hashlib.sha256(
            json.dumps(proposal, sort_keys=True).encode()
        ).hexdigest()[:16]

        proposal_data = {
            'proposal_id': proposal_id,
            'submitted_by': fingerprint,
            'timestamp': int(time.time()),
            'proposal': proposal
        }

        proposal_file = proposals_dir / f"proposal_{proposal_id}.json"

        try:
            with open(proposal_file, 'w') as f:
                json.dump(proposal_data, f, indent=2)

            print(f"[PROPOSAL SUCCESS] Proposal {proposal_id} submitted")
            return proposal_data

        except Exception as e:
            print(f"[PROPOSAL FAIL] Failed to save proposal: {e}")
            return None


def require_verified_identity(fingerprint: str):
    """
    Decorator to require verified identity for governance operations

    Args:
        fingerprint: Required fingerprint

    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            registrar = PublicRegistrar()
            if not registrar.verify_identity(fingerprint):
                raise PermissionError(
                    f"Identity {fingerprint} not verified - operation denied"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def main(args):
    """Main CLI interface"""
    registrar = PublicRegistrar(reg_dir=args.reg_dir)

    if args.list_members:
        print("=" * 70)
        print("REGISTERED MEMBERS")
        print("=" * 70)
        members = registrar.list_members()

        for member in members:
            status = "✅" if member['verified'] else "❌"
            print(f"{status} {member['proof_name']}")
            print(f"   Fingerprint: {member['openpgp_fingerprint']}")
            print(f"   File: {member['file']}")
            print()

        print(f"Total verified members: {sum(1 for m in members if m['verified'])}")

    elif args.verify_identity:
        print(f"Verifying identity: {args.verify_identity}")
        is_valid = registrar.verify_identity(args.verify_identity)
        sys.exit(0 if is_valid else 1)

    elif args.register_member:
        print(f"Registering member from file: {args.register_member}")
        try:
            with open(args.register_member, 'r') as f:
                registration = json.load(f)

            fingerprint = registration.get('openpgp_fingerprint')
            if not fingerprint:
                print("[ERROR] No fingerprint in registration file")
                sys.exit(1)

            success = registrar.register_member(registration, fingerprint)
            sys.exit(0 if success else 1)

        except Exception as e:
            print(f"[ERROR] Failed to register member: {e}")
            sys.exit(1)

    elif args.submit_proposal:
        print(f"Submitting proposal from file: {args.submit_proposal}")
        try:
            with open(args.submit_proposal, 'r') as f:
                proposal = json.load(f)

            if not args.fingerprint:
                print("[ERROR] --fingerprint required for proposal submission")
                sys.exit(1)

            result = registrar.submit_proposal(proposal, args.fingerprint)
            sys.exit(0 if result else 1)

        except Exception as e:
            print(f"[ERROR] Failed to submit proposal: {e}")
            sys.exit(1)

    else:
        print("No action specified. Use --help for options.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Universal Governance - Cryptographic Identity Verification"
    )

    parser.add_argument(
        '--reg-dir',
        type=str,
        default='./registrations/examples',
        help='Directory containing registration files'
    )

    parser.add_argument(
        '--list-members',
        action='store_true',
        help='List all registered members'
    )

    parser.add_argument(
        '--verify-identity',
        type=str,
        metavar='FINGERPRINT',
        help='Verify an identity by fingerprint'
    )

    parser.add_argument(
        '--register-member',
        type=str,
        metavar='FILE',
        help='Register a new member from JSON file'
    )

    parser.add_argument(
        '--submit-proposal',
        type=str,
        metavar='FILE',
        help='Submit a governance proposal from JSON file'
    )

    parser.add_argument(
        '--fingerprint',
        type=str,
        help='Your OpenPGP fingerprint (for proposal submission)'
    )

    args = parser.parse_args()
    main(args)
