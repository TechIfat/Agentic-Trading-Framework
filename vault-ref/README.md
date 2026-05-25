# vault-ref/README.md
# External secret references. NO SECRETS ARE STORED IN THIS FOLDER.
# This folder tells the agent WHERE to retrieve secrets, not what they are.

## How secrets work in this workspace

All secrets live in an external vault (HashiCorp Vault, Azure Key Vault,
or 1Password Secrets Automation) or a local `.env` file for development. 
This folder contains only reference metadata: paths, key names, and checksums.

---

## checksums.txt (CRITICAL — read by Stage 03)

This file maps each sensitive workspace file to its expected SHA-256 hash.
Stage 03 reads this to verify risk-limits.md has not been tampered with.

Format:
```text
[sha256-hex]  [relative-file-path]
```

Example (replace with real values after setup):
```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  03_risk/risk-limits.md
```

**After editing risk-limits.md**, regenerate this entry to overwrite the old hash:
```bash
# On Mac/Linux:
shasum -a 256 03_risk/risk-limits.md > vault-ref/checksums.txt
```
Note: `vault-ref/checksums.txt` is included in the `.gitignore` by default to prevent accidental commits of your risk profile to version history.

---

## mcp-allowlist.txt (read at session start)

Permitted MCP server URLs. Any MCP call to a URL not on this list is rejected.

```text
[Add broker MCP URL or local MCP server command]
```

---

## Secret key names (vault paths — not values)

```text
VAULT_PATH_BROKER_READ_TOKEN:   secret/trading/broker/read-token
VAULT_PATH_BROKER_WRITE_TOKEN:  secret/trading/broker/write-token
VAULT_PATH_ANTHROPIC_API_KEY:   secret/trading/anthropic/api-key
VAULT_PATH_ENCRYPTION_KEY:      secret/trading/storage/aes256-key
```

---

## Encryption note

`knowledge/wiki/`, `knowledge/graph/`, and `audit/` should be encrypted at rest
using AES-256 with the key at VAULT_PATH_ENCRYPTION_KEY in production environments.
Decryption happens at session start; re-encryption at session end (Stage 07 teardown).

## Setup instructions for first use

1. Set up your chosen vault (or local `.env` file).
2. Generate AES-256 key, store at VAULT_PATH_ENCRYPTION_KEY (if using encryption).
3. Add broker API credentials to your vault/env.
4. Compute SHA-256 of `03_risk/risk-limits.md`, store in `vault-ref/checksums.txt`.
5. Add broker MCP URL/command to `mcp-allowlist.txt`.
6. Run first session with `SESSION_TYPE: AUDIT_ONLY` to verify the stack.
