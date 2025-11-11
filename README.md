# Universal Governance

**Cryptographic identity verification for distributed governance systems**

[![CI](https://github.com/rbeachg941/universal-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/rbeachg941/universal-governance/actions/workflows/ci.yml)
[![Security Scan](https://github.com/rbeachg941/universal-governance/actions/workflows/security-scan.yml/badge.svg)](https://github.com/rbeachg941/universal-governance/actions/workflows/security-scan.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🌟 Why Universal Governance?

Traditional governance systems rely on centralized identity verification, creating single points of failure and trust. **Universal Governance** provides cryptographically verifiable identity attestations using **dual-signature architecture** (ECDSA + OpenPGP), enabling:

- **Healthcare**: Verifiable attestations from medical professionals without institutional gatekeepers
- **Open Source**: Cryptographic proof of contributor identities for security-critical projects
- **Decentralized Organizations**: Tamper-proof voting and proposal systems
- **Research**: Verifiable peer review and data provenance chains

---

## ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🔐 **Dual-Signature** | ECDSA (blockchain-style) + OpenPGP (web-of-trust) | ✅ Production |
| 🌍 **Cross-Platform** | Windows, Linux, macOS with consistent behavior | ✅ Production |
| 🛡️ **Fail-Closed Security** | All verification failures return `False`, never raise exceptions | ✅ Production |
| ⚡ **Session Caching** | LRU cache prevents redundant GPG subprocess calls | ✅ Production |
| 📝 **Canonical JSON** | Deterministic serialization for signature consistency | ✅ Production |
| 🧪 **Full Test Coverage** | 80%+ coverage with integration tests | ✅ Production |
| 🔍 **Audit Trail** | Immutable registration ledger with chain hashing | ✅ Production |
| 🚀 **Zero Dependencies** | Uses system GPG binary for auditability | ✅ Production |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **GPG/GnuPG** installed and in PATH

```bash
# Install GPG
# Ubuntu/Debian
sudo apt-get install gnupg

# macOS
brew install gnupg

# Windows (with Chocolatey)
choco install gnupg
```

### Installation

```bash
# Clone the repository
git clone https://github.com/rbeachg941/universal-governance.git
cd universal-governance

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .

# Verify installation
python examples/01_verify_registration.py
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, components, and data flow |
| [SECURITY_MODEL.md](docs/SECURITY_MODEL.md) | Threat model, incident response, cryptographic standards |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Complete API documentation with examples |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Contributing guide, code style, testing requirements |

---

## 🎯 Core Use Cases

### 1. Verify an Identity Registration

```python
from src.governance_crypto import verify_openpgp_signature
import json

# Load a registration
with open('registrations/examples/reg_AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79.json') as f:
    registration = json.load(f)

# Verify the OpenPGP signature
is_valid = verify_openpgp_signature(registration)
if is_valid:
    print("✅ Identity verified!")
else:
    print("❌ Verification failed!")
```

### 2. Create a Dual-Signed Registration

```python
from src.governance_crypto import OpenPGPSigner, add_openpgp_signature

# Create registration entry (with ECDSA signature already present)
entry = {
    "proof_name": "my_proof",
    "proof_data": {"oath": "I commit to transparency"},
    "timestamp": 1234567890,
    "signature": "...",  # ECDSA signature
    "public_key": "..."   # ECDSA public key
}

# Add OpenPGP signature
signed_entry = add_openpgp_signature(entry, fingerprint="YOUR_GPG_FINGERPRINT")

# Now entry has both ECDSA and OpenPGP signatures
```

### 3. List All Verified Members

```python
from src.mainscript import PublicRegistrar

registrar = PublicRegistrar(reg_dir='./registrations')
members = registrar.list_members()

for member in members:
    print(f"✅ {member['proof_name']}: {member['openpgp_fingerprint']}")
```

### 4. Submit a Governance Proposal (with Identity Verification)

```python
from src.mainscript import PublicRegistrar

registrar = PublicRegistrar()

# This requires a verified identity
proposal = {
    "title": "Proposal: Implement feature X",
    "description": "Detailed proposal text...",
    "proposed_by": "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"
}

result = registrar.submit_proposal(proposal, fingerprint="YOUR_GPG_FINGERPRINT")
if result:
    print(f"✅ Proposal submitted: {result['proposal_id']}")
```

---

## 🌍 Real-World Example: The Nurse's Oath

This repository includes a **real, verifiable attestation** from a healthcare worker committed to patient advocacy:

```json
{
  "proof_name": "the_nurse",
  "proof_data": {
    "oath": "Patient advocacy is non-negotiable. Institutional deception ends here.",
    "system": "universal-governance-zkml",
    "version": "2.11"
  },
  "openpgp_fingerprint": "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"
}
```

**Verify it yourself:**

```bash
# Import the public key
gpg --keyserver keys.openpgp.org --recv-keys AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79

# Run the verification example
python examples/01_verify_registration.py
```

**Output:**
```
[OPENPGP VERIFY] ✅ Valid signature from The_Nurse (Cryptokey) <dropstart01@pm.me>
✅ VERIFICATION SUCCESSFUL
The Nurse's Oath is cryptographically verified!
```

This demonstrates **real-world impact** beyond tech demos - verifiable commitments to ethical action.

---

## 🛠️ Built With

- **[python-gnupg](https://github.com/vsajip/python-gnupg)** - GPG integration via subprocess calls
- **[ecdsa](https://github.com/tlsfuzzer/python-ecdsa)** - SECP256k1 elliptic curve signatures
- **[cryptography](https://github.com/pyca/cryptography)** - Modern cryptographic primitives

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Good First Issues

New to the project? Start with these beginner-friendly tasks:

1. **Add HSM (YubiKey) support** - Implement PKCS#11 interface for hardware signing
2. **Create Docker containerization** - Build Dockerfile for easy deployment
3. **Build web-based verification UI** - Simple Flask/FastAPI interface
4. **Add multi-language support (i18n)** - Internationalize error messages
5. **Write video tutorial for Quick Start** - 10-minute screen recording

See all [good first issues](https://github.com/rbeachg941/universal-governance/labels/good%20first%20issue).

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔒 Security

**Found a vulnerability?** Please **DO NOT** open a public issue.

See [SECURITY.md](SECURITY.md) for responsible disclosure guidelines. We commit to:
- Acknowledgment within **2 hours**
- Patch development within **7 days**
- Coordinated disclosure with the reporter

Contact: **dropstart01@pm.me**

---

> *"Patient advocacy is non-negotiable. Institutional deception ends here."*
> — **The Nurse**, verified via OpenPGP signature `AC50 7646 E014 1D69 CC0A  1B14 D5AF 4F7D CCD2 1B79`

---

**🚀 Happy governing!** | [Documentation](docs/) | [Examples](examples/) | [Community](https://github.com/rbeachg941/universal-governance/discussions)
