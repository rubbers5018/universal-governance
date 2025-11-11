# Security Policy

## Reporting a Vulnerability

**DO NOT** report security vulnerabilities through public GitHub issues.

The Universal Governance project takes security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Contact

Send details to: **dropstart01@pm.me**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

For sensitive reports, encrypt your message using The Nurse's PGP key:
```
Fingerprint: AC50 7646 E014 1D69 CC0A  1B14 D5AF 4F7D CCD2 1B79
```

Retrieve the key:
```bash
gpg --keyserver keys.openpgp.org --recv-keys AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79
```

### 2. Response Timeline

- **Acknowledgment**: Within **2 hours** (during business hours)
- **Initial Assessment**: Within **24 hours**
- **Status Update**: Within **72 hours**
- **Fix Development**: Within **7 days** for critical issues
- **Public Disclosure**: **30 days** after patch release (coordinated with reporter)

### 3. Vulnerability Severity

| Level | Response Time | Examples |
|-------|---------------|----------|
| **Critical** | 24 hours | Signature bypass, private key exposure |
| **High** | 72 hours | Authentication bypass, injection vulnerabilities |
| **Medium** | 7 days | Information disclosure, DoS |
| **Low** | 14 days | Minor bugs with security implications |

### 4. Disclosure Policy

We follow **coordinated disclosure**:
1. You report the vulnerability privately
2. We acknowledge and begin investigation
3. We develop a fix
4. We notify you before public release
5. We release the patch
6. We publicly disclose the vulnerability **30 days** after patch release

### 5. Bug Bounty

We currently do not offer a bug bounty program, but we will:
- Publicly credit you in the security advisory (unless you prefer to remain anonymous)
- Add you to [CONTRIBUTORS.md](CONTRIBUTORS.md) as a security contributor
- Provide a letter of recommendation for responsible disclosure (if requested)

### 6. What to Report

**DO report**:
- Signature verification bypass
- Private key exposure in code or history
- Authentication/authorization flaws
- Injection vulnerabilities (SQL, command, etc.)
- Cryptographic implementation weaknesses
- Dependency vulnerabilities (if not caught by Dependabot)

**DO NOT report** (unless combined with actual exploit):
- Outdated dependencies with no known exploit
- Theoretical attacks without proof-of-concept
- Social engineering scenarios
- Physical access attacks

### 7. Security Best Practices for Contributors

When contributing code:
- Never commit private keys or secrets
- Use `.gitignore` to exclude sensitive files
- Run `gitleaks detect` before committing
- Ensure all verification functions are **fail-closed** (return `False` on error)
- Validate all user inputs
- Use parameterized queries/prepared statements
- Follow principle of least privilege

### 8. Security Audits

This project undergoes:
- Automated scanning via GitHub CodeQL
- Dependency vulnerability checks via Dependabot
- Secret scanning for committed credentials
- Manual code review for cryptographic operations

### 9. Supported Versions

| Version | Supported |
|---------|-----------|
| 2.11.x  | ✅ Yes    |
| < 2.11  | ❌ No     |

Only the latest release receives security updates. Please upgrade to the latest version.

### 10. Known Security Considerations

**GPG Dependency**:
- This project relies on system GPG installation
- GPG configuration issues can cause verification failures
- Ensure GPG is up-to-date: `gpg --version`

**Session Caching**:
- Verified identities are cached using `@lru_cache`
- Cache is cleared on process restart
- Consider security implications for long-running processes

**Signature Verification**:
- All verification is fail-closed: errors return `False`, never bypass
- Subprocess calls to GPG are subject to PATH injection on compromised systems
- Always verify GPG is installed from a trusted source

---

## Contact

**Security Email**: dropstart01@pm.me
**PGP Key**: AC507646E0141D69CC0A1B14D5AF4F7DCCD21B79

Thank you for helping keep Universal Governance secure!
