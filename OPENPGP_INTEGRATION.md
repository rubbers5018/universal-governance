# OpenPGP Integration Guide for Universal Governance

**Your OpenPGP Key Details:**
- **Fingerprint:** `AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79`
- **Key Server:** `keys.openpgp.org`
- **Status:** Public, available for verification

---

## Step 1: Export Your Public Key

```bash
# Export to ASCII-armored format
gpg --export --armor AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79 > your_public_key.asc

# Verify export
cat your_public_key.asc
```

**Output will look like:**
```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mI0EZ...AQAB...
...
-----END PGP PUBLIC KEY BLOCK-----
```

---

## Step 2: Create Your Registration Entry

Create a file `registration_payload.json`:

```json
{
  "proof_name": "the_nurse",
  "proof_data": {
    "proof_type": "training",
    "nurse": "the_nurse",
    "timestamp": "2025-11-10T19:45:00Z",
    "oath": "Patient advocacy is non-negotiable. Institutional deception ends here.",
    "universal_application": "All fields where trust, honesty, and accountability matter",
    "openpgp_fingerprint": "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79",
    "system": "universal-governance-zkml",
    "version": "2.11"
  }
}
```

---

## Step 3: Sign Your Registration Entry

```bash
# Create detached signature (recommended)
gpg --detach-sign --armor registration_payload.json

# This creates: registration_payload.json.asc
cat registration_payload.json.asc
```

**Output will look like:**
```
-----BEGIN PGP SIGNATURE-----

iQEzBAEBCAAdFiEEpQfGRuAUHWnMChuU1a9PfczSG7kFAmdeK...
...
-----END PGP SIGNATURE-----
```

---

## Step 4: Verify the Signature

```bash
# Verify the signature (anyone can do this)
gpg --verify registration_payload.json.asc registration_payload.json

# Expected output:
# gpg: Signature made Mon 10 Nov 2025 07:45:00 PM EST
# gpg: Good signature from "Your Name <email>" [ultimate]
```

---

## Step 5: Integrate Into mainscript_v2_11.py

Add this function to `mainscript_v2_11.py`:

```python
import subprocess
import base64

class OpenPGPIntegration:
    """Handle OpenPGP signing and verification."""
    
    def __init__(self, fingerprint: str = "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79"):
        self.fingerprint = fingerprint
        self.key_server = "keys.openpgp.org"
    
    def export_public_key(self) -> str:
        """Export your public key in ASCII-armored format."""
        result = subprocess.run(
            ['gpg', '--export', '--armor', self.fingerprint],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"GPG export failed: {result.stderr}")
        return result.stdout
    
    def sign_payload(self, payload_json: str, detached: bool = True) -> str:
        """Sign a JSON payload with your private key."""
        # Write payload to temp file
        with open('/tmp/payload_to_sign.json', 'w') as f:
            f.write(payload_json)
        
        # Sign (detached by default)
        cmd = ['gpg', '--detach-sign', '--armor']
        if detached:
            cmd.append('--output')
            cmd.append('/tmp/payload.sig')
        cmd.append('/tmp/payload_to_sign.json')
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"GPG sign failed: {result.stderr}")
        
        # Read signature
        with open('/tmp/payload.sig', 'r') as f:
            signature = f.read()
        
        return signature
    
    def verify_signature(self, payload_json: str, signature: str) -> bool:
        """Verify a signature (anyone can do this)."""
        # Write payload and signature to temp files
        with open('/tmp/payload_verify.json', 'w') as f:
            f.write(payload_json)
        
        with open('/tmp/payload_verify.sig', 'w') as f:
            f.write(signature)
        
        # Verify
        result = subprocess.run(
            ['gpg', '--verify', '/tmp/payload_verify.sig', '/tmp/payload_verify.json'],
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    
    def create_signed_registration(self, proof_data: dict) -> dict:
        """Create a fully signed registration entry."""
        import json
        from datetime import datetime, timezone
        
        # Get your public key
        public_key = self.export_public_key()
        
        # Create payload
        payload = {
            "proof_name": "the_nurse",
            "proof_data": proof_data,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "openpgp_fingerprint": self.fingerprint,
            "key_server": self.key_server
        }
        
        # Serialize to canonical JSON
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        # Sign it
        signature = self.sign_payload(payload_json)
        
        # Add signature and key to entry
        payload["signature"] = signature
        payload["public_key"] = public_key
        
        return payload


# Usage in mainscript_v2_11.py:
def create_signed_oath():
    openpgp = OpenPGPIntegration("AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79")
    
    proof_data = {
        "proof_type": "training",
        "nurse": "the_nurse",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "oath": "Patient advocacy is non-negotiable.",
        "universal_application": "All fields where trust matters",
        "system": "universal-governance-zkml",
        "version": "2.11"
    }
    
    signed_entry = openpgp.create_signed_registration(proof_data)
    
    # Verify it
    payload_json = json.dumps(
        {k: v for k, v in signed_entry.items() 
         if k not in ['signature', 'public_key']},
        sort_keys=True,
        separators=(',', ':')
    )
    
    is_valid = openpgp.verify_signature(payload_json, signed_entry['signature'])
    
    logger.info(f"Signed registration created and verified: {is_valid}")
    
    return signed_entry
```

---

## Step 6: Complete Registration Entry (Template)

```json
{
  "proof_name": "the_nurse",
  "proof_data": {
    "proof_type": "training",
    "nurse": "the_nurse",
    "timestamp": "2025-11-10T19:45:00Z",
    "oath": "Patient advocacy is non-negotiable. Institutional deception ends here.",
    "universal_application": "All fields where trust, honesty, and accountability matter",
    "openpgp_fingerprint": "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79",
    "system": "universal-governance-zkml",
    "version": "2.11"
  },
  "timestamp": 1731264300,
  "openpgp_fingerprint": "AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79",
  "key_server": "keys.openpgp.org",
  "signature": "-----BEGIN PGP SIGNATURE-----\n\niQEzBAEBCAAdFiEEpQfGRuAUHWnMChuU1a9PfczSG7kFAmdeK5wACgkQ1a9P\nfczSG7nJ3Qf+AbCdEfGhI...\n=FINAL\n-----END PGP SIGNATURE-----",
  "public_key": "-----BEGIN PGP PUBLIC KEY BLOCK-----\n\nmI0EZ5eK4BEEAPZvX...\n-----END PGP PUBLIC KEY BLOCK-----"
}
```

---

## Step 7: Deployment Command

Update `mainscript_v2_11.py` to accept your OpenPGP key:

```bash
# Register with OpenPGP signature
python mainscript_v2_11.py \
  --mode register_only \
  --openpgp-key AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79 \
  --sign

# Output:
# [2025-11-10 19:45:00] INFO: [REGISTRAR] Proof 'the_nurse' registered. Hash: abc123def456...
# [2025-11-10 19:45:00] INFO: [OPENPGP] Signature verified: AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79
# [2025-11-10 19:45:00] INFO: [SUCCESS] Oath registered, signed, and publicly attestable
```

---

## Step 8: Verification (Anyone Can Do This)

Anyone can verify your signature using your public key:

```bash
# Download your public key from the key server
gpg --keyserver keys.openpgp.org --recv-keys AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79

# Verify the registration entry
gpg --verify registration_payload.json.asc registration_payload.json

# Output will show:
# gpg: Good signature from [your key]
# gpg: Signature made [date/time]
```

---

## Step 9: Your Public Ledger

Once registered, your oath is publicly available at:

```
./public_reg/registration_ledger.json
```

**Anyone can:**
1. Download the ledger
2. Extract your registration entry
3. Verify your signature using your public key
4. Prove you attest to the oath

---

## Security Best Practices

1. **Never commit your private key** to GitHub
2. **Keep your passphrase secure**
3. **Backup your key** in a secure location
4. **Use a hardware security key** for production (YubiKey, etc.)
5. **Rotate keys** if compromised

---

## Troubleshooting

### GPG not found
```bash
# Install GPG
# macOS:
brew install gnupg

# Ubuntu/Debian:
sudo apt-get install gnupg

# Windows:
choco install gpg
```

### Signature verification fails
```bash
# Make sure public key is imported
gpg --keyserver keys.openpgp.org --recv-keys AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79

# Try verification again
gpg --verify registration_payload.json.asc registration_payload.json
```

### Passphrase issues
```bash
# Use gpg-agent for caching
eval $(gpg-agent --daemon)
```

---

## Final Result

Your registration entry is now:
- ✅ **Cryptographically signed** with your OpenPGP key
- ✅ **Globally verifiable** using your public key
- ✅ **Immutable** — cannot be altered without invalidating the signature
- ✅ **Transparent** — anyone can verify it independently
- ✅ **Permanent** — your oath is recorded for all time

**Your commitment is now unbreakable and eternally verifiable.**
