# Examples

This directory contains runnable examples demonstrating Universal Governance functionality.

## Prerequisites

Before running examples, ensure:
1. Python 3.8+ is installed
2. GPG is installed and in PATH
3. Dependencies are installed: `pip install -r requirements.txt`
4. The Nurse's GPG key is imported:
   ```bash
   gpg --keyserver keys.openpgp.org --recv-keys AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79
   ```

## Examples

### 01_verify_registration.py
**Purpose**: Verify The Nurse's cryptographic attestation

Demonstrates loading a registration file and verifying the OpenPGP signature.
This is the core proof-of-concept showing real-world identity verification.

```bash
python examples/01_verify_registration.py
```

**Expected Output**:
```
📜 The Nurse's Oath:
   "Patient advocacy is non-negotiable. Institutional deception ends here."

🔍 Verifying OpenPGP signature...
[OPENPGP VERIFY] ✅ Valid signature from The_Nurse (Cryptokey) <dropstart01@pm.me>

✅ VERIFICATION SUCCESSFUL
The Nurse's Oath is cryptographically verified!
```

---

### 02_list_members.py
**Purpose**: List all registered members with verification status

Scans the registration directory and batch-verifies all signatures.
Shows how to build a verified member roster.

```bash
python examples/02_list_members.py
```

**Expected Output**:
```
Found 1 registration(s):

✅ VERIFIED: the_nurse
  Fingerprint: AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79
  Timestamp:   1762823435
  File:        reg_AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79.json
```

---

### 03_submit_proposal.py
**Purpose**: Submit a governance proposal with identity verification

Demonstrates the `@require_verified_identity` decorator and how governance
operations require cryptographic proof of identity.

```bash
python examples/03_submit_proposal.py
```

**Expected Output**:
```
📋 Proposal Details:
   Title: Proposal: Implement Patient Advocacy Framework
   Proposed by: AC507646E0141D6...

🔍 Verifying identity before submission...
[OPENPGP VERIFY] ✅ Valid signature from The_Nurse (Cryptokey) <dropstart01@pm.me>

✅ PROPOSAL SUBMITTED SUCCESSFULLY
Proposal ID: a3f2c9e1b8d4
```

---

## Troubleshooting

### "GPG not found"
**Solution**: Install GPG:
- Ubuntu/Debian: `sudo apt-get install gnupg`
- macOS: `brew install gnupg`
- Windows: `choco install gnupg`

### "Key not found"
**Solution**: Import The Nurse's public key:
```bash
gpg --keyserver keys.openpgp.org --recv-keys AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79
```

### "Signature verification failed"
**Possible causes**:
1. Key not imported (see above)
2. Registration file corrupted
3. GPG configuration issue

**Debug steps**:
```bash
# Verify GPG works
gpg --version

# List imported keys
gpg --list-keys

# Manually verify signature
gpg --verify registrations/examples/reg_AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79.json
```

---

## Next Steps

After running the examples:
1. Read [DEVELOPMENT.md](../docs/DEVELOPMENT.md) to learn how to contribute
2. Explore [API_REFERENCE.md](../docs/API_REFERENCE.md) for integration details
3. Check [ARCHITECTURE.md](../docs/ARCHITECTURE.md) to understand the design

## Creating Your Own Registration

To create your own registration:
1. Generate a GPG key: `gpg --full-generate-key`
2. Export your public key: `gpg --export --armor YOUR_FINGERPRINT`
3. Use `src/governance_crypto.py` to sign your attestation
4. Submit a pull request to add your registration

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.
