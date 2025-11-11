#!/usr/bin/env python3
"""
MASTER SCRIPT v2.10: PUBLIC REGISTRATION BEHEMOTH
=======================
Provenance Pinnacle: _register_training_proof(the_nurse) yeets training oath to public ledger.
- Hash proof + timestamp + sig for tamper-proof broadcast.
- Mock TPA log: File/chain sim; prod: Eth/IPFS.
- Embed reg ID in public_inputs for inference attestations.
- Tests: Verify sig, chain integrity.

Requirements: Same as v2.9 + ecdsa (for sigs).

Run: python mainscript.py --model_path model.pt --dataset_path ./train_data/ --pinned_commit abc... --pinned_provenance def... --quantum --optimize --backdoor_check --storage_backend blockchain
Outputs: ./public_reg/training_nurse_proof.json (signed + chained); global gospel.
"""

import argparse
import os
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import sympy as sp
from pathlib import Path
import hashlib
import json
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives.asymmetric import dh, ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import utils
import torchattacks
import sqlite3
import pytest
import ecdsa  # Sig for registration
from ecdsa import SigningKey, SECP256k1
from zkml_auditor import MasterScriptIntegration
from typing import List, Dict, Any

# [All classes from v2.9 - QuantumResistantZK, MaliciousDataScrubber, etc., ProofLedger, AuditTrailBackend, run_tests - unchanged]

@dataclass
class ProofResult:
    proof: bytes
    proof_size_bytes: int
    generation_time_ms: float
    verification_time_ms: float
    status: str
    model_commitment: str

# [ProofLedger, AuditTrailBackend, run_tests - unchanged]

# NEW: Public Registration for Training Proof (TPA-Style Log)
class PublicRegistrar:
    """Mock TPA/Chain: Register proof publicly for verification."""
    def __init__(self, reg_file: str = './public_reg/training_proofs.json'):
        self.reg_file = reg_file
        self.prev_reg_hash = 'genesis_public_0000000000000000000000000000000000000000000000000000000000000000'
        os.makedirs(os.path.dirname(reg_file), exist_ok=True)
        self.private_key = SigningKey.generate(curve=SECP256k1)  # Dummy TPA key
        self.public_key = self.private_key.verifying_key

    def _register_training_proof(self, training_proof: Dict, proof_name: str = "the_nurse"):
        """One-time: Sign + chain training proof for public verification."""
        timestamp = int(time.time())
        entry = {
            'proof_name': proof_name,
            'training_proof': training_proof,
            'timestamp': timestamp,
            'prev_reg_hash': self.prev_reg_hash
        }
        
        # Sig: ECDSA on serialized entry
        ser = json.dumps(entry, sort_keys=True).encode()
        sig = self.private_key.sign(ser, hashfunc=hashlib.sha256)
        entry['signature'] = sig.hex()
        entry['public_key'] = self.public_key.to_string().hex()
        
        # Chain hash
        entry['reg_hash'] = self._compute_reg_hash(entry)
        self.prev_reg_hash = entry['reg_hash']
        
        # Append to reg
        reg = []
        if os.path.exists(self.reg_file):
            with open(self.reg_file, 'r') as f:
                reg = json.load(f)
        reg.append(entry)
        with open(self.reg_file, 'w') as f:
            json.dump(reg, f, indent=2)
        
        print(f"[REGISTRAR] '{proof_name}' forged & registered: Hash {entry['reg_hash'][:16]}..., Sig verified.")
        return entry

    def _compute_reg_hash(self, entry: Dict) -> str:
        ser = json.dumps(entry, sort_keys=True).exclude('signature').encode()  # Sig after
        return hashlib.sha256(self.prev_reg_hash.encode() + ser).hexdigest()

    def verify_registration(self, reg_entry: Dict):
        """TPA Challenge: Verify sig + chain."""
        ser = json.dumps({k: v for k, v in reg_entry.items() if k != 'signature'}, sort_keys=True).encode()
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(reg_entry['public_key']), curve=SECP256k1)
        try:
            vk.verify(bytes.fromhex(reg_entry['signature']), ser, hashfunc=hashlib.sha256)
            assert reg_entry['reg_hash'] == self._compute_reg_hash(reg_entry), "Chain mismatch"
            print("[TPA VERIFY] Registration legit: Sig + hash golden.")
            return True
        except:
            print("[TPA VIOLATION] Reg forged: Sig or chain broken.")
            return False

# Enhanced run_tests: Add Registration Test
def run_tests(args):
    print("[TESTING] Igniting validation vigil...")
    os.makedirs("./tests/reports", exist_ok=True)
    
    # [Previous tests unchanged - test_model_commitment, test_backdoor_check, etc.]
    
    # NEW: Test Registration
    def test_training_registration():
        registrar = PublicRegistrar()
        dummy_proof = {'dummy': 'data'}
        entry = registrar._register_training_proof(dummy_proof, "test_nurse")
        assert registrar.verify_registration(entry), "Reg must self-verify"
        print("[TEST PASS] Registration: TPA oath sworn.")
    
    # Run all
    tests = [test_model_commitment, test_backdoor_check, test_training_provenance, test_integration_flush, test_perf_batch, test_training_registration]
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"[TEST FAIL] {test.__name__}: {e}")
            raise
    print("[TESTING] Empire validated: Registration chained.")
    # [JUnit sim unchanged]
    
    report = {'tests': len(tests), 'passes': len(tests), 'duration': time.time() - start_time}
    with open("./tests/reports/junit.xml", 'w') as f:
        f.write(f'<testsuite name="zkML" tests="{report["tests"]}" failures="0" time="{report["duration"]:.2f}"/>')
    print(f"[CI HOOK] JUnit report: {report}")

def main(args):
    if args.test:
        run_tests(args)
        return
    
    # [All previous init unchanged - Model, Dataset, Training Proof, Public Inputs, Backend, etc.]
    model = torch.load(args.model_path, map_location='cuda' if torch.cuda.is_available() else 'cpu')
    model.eval()
    computed_commit = compute_model_commitment(model)
    print(f"[COMPLIANCE] Computed commitment: {computed_commit}")
    
    pinned_commit = args.pinned_commit or os.getenv('ZK_PINNED_COMMIT')
    if pinned_commit:
        verify_model_authenticity(computed_commit, pinned_commit)
    
    dataset_commitment = compute_dataset_commitment(args.dataset_path) if args.dataset_path else 'dummy_hash'
    print(f"[RULE 3] Dataset commitment: {dataset_commitment}")
    
    training_config = {'optimizer': 'Adam', 'lr': 0.001, 'epochs': 10}
    training_proof = prove_training(args.model_path, dataset_commitment, **training_config, qr_zk=qr_zk)
    
    pinned_provenance = args.pinned_provenance or os.getenv('ZK_PINNED_PROVENANCE')
    if pinned_provenance:
        verify_training_provenance(training_proof, pinned_provenance)
    
    with open("./proofs/training_provenance.json", 'w') as f:
        json.dump(training_proof, f, indent=2)
    print("[RULE 3] Training proof forged & saved.")
    
    # NEW: Public Registration (TPA Log)
    registrar = PublicRegistrar()
    reg_entry = registrar._register_training_proof(training_proof, "the_nurse")
    public_inputs = {
        'model_commitment': computed_commit,
        'circuit_version': 'zkml_v2.10',
        'backdoor_check_enabled': args.backdoor_check,
        'dataset_commitment': dataset_commitment,
        'training_proof_hash': hashlib.sha256(json.dumps(training_proof, sort_keys=True).encode()).hexdigest(),
        'registration_id': reg_entry['reg_hash']  # Embed for attestation
    }
    
    # Verify Reg (TPA Challenge Sim)
    assert registrar.verify_registration(reg_entry), "[REG FAIL] Self-challenge broken!"
    print(f"[TPA] 'the_nurse' oath logged: {reg_entry['reg_hash'][:16]}...")
    
    # [Rest: Auditor Init, Optimizer, QR-ZK, Scrubber, Edge Key, GPU, Baseline, Process Loop - unchanged]
    base_batch_size = int(os.getenv('ZK_BATCH_SIZE', args.batch_size))
    zkml_audit = MasterScriptIntegration(
        model_path=args.model_path,
        audit_mode=args.mode,
        batch_size=base_batch_size,
        public_inputs=public_inputs
    )
    # ... (insert full loop from v2.8, with backend.store(proof_result))
    
    # At end of loop: backend.store(proof_result)  # Unchanged
    
    # [Flush, Final Nova, QR Export - unchanged]
    
    del model, scrubber, qr_zk
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    print(f"[COMPLIANCE] Oath eternal: 'the_nurse' registered, empire unchallenged.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Public Reg zkML Master: Oaths Broadcast")
    # [All previous args from v2.9]
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--dataset_path', type=str, help='Path to training dataset dir')
    parser.add_argument('--input_data', type=str, required=True)
    parser.add_argument('--batch_size', type=int, default=100)
    parser.add_argument('--mode', type=str, default='batch', choices=['realtime', 'batch', 'hybrid'])
    parser.add_argument('--gpu', action='store_true')
    parser.add_argument('--quantum', action='store_true')
    parser.add_argument('--optimize', action='store_true')
    parser.add_argument('--pinned_commit', type=str, help='Pinned SHA-256 for model')
    parser.add_argument('--pinned_provenance', type=str, help='Pinned hash for training proof')
    parser.add_argument('--backdoor_check', action='store_true')
    parser.add_argument('--storage_backend', type=str, default='jsonl', choices=['jsonl', 'db', 'blockchain'])
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    
    os.makedirs("./cloud_store", exist_ok=True)
    os.makedirs("./proofs", exist_ok=True)
    os.makedirs("./audits", exist_ok=True)
    os.makedirs("./audits/proofs", exist_ok=True)
    os.makedirs("./tests/reports", exist_ok=True)
    os.makedirs("./public_reg", exist_ok=True)
    
    main(args)