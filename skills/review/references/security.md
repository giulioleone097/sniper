# Security: the catalog for the `security` lens

Handed to a `security` reviewer with the diff. Every finding needs a reachable trigger: untrusted input crossing a trust boundary, or a violated boundary itself. A finding names the attacker, the input path, and the concrete failure — "could be more secure" is hardening, not a defect. Verify reach before reporting: dead code, internal-only callers, and input the caller already validated are not triggers.

## Injection
- User-controlled data concatenated into SQL, a shell command, a template, or a markup string: P1 at the boundary. The ORM's raw escape hatch counts as raw.
- Attacker-supplied bytes deserialized into live objects (`pickle`, unsafe YAML, native Java/PHP deserialization, `eval` on input): P0 when reachable.

## Access control
- A route, handler, or query missing the authorization check its siblings enforce, or authenticating without checking ownership — an object id taken from the request and fetched without an owner predicate (IDOR): P1.
- Privilege escalation: a role or scope check bypassed through a request parameter, mass assignment of a protected field, or a default-allow branch: P1.

## Secrets
- A credential, token, or private key committed in code, fixtures, or history; bundled into a client artifact (a public env var, exposed config); or written to logs or error responses: P1.

## Sinks
- Unsanitized user input reaching HTML (`innerHTML`, `dangerouslySetInnerHTML`, an unescaped template slot): P1.
- User input reaching a shell line, a filesystem path (traversal), or a redirect target without validation or an allowlist: P1.

## Crypto
- Hand-rolled encryption or signing, weak primitives for the job (MD5/SHA1 on passwords, DES, ECB mode), a reused or fixed nonce/IV, or a predictable RNG (`Math.random`, `rand`) minting tokens: P1.

## SSRF and redirects
- A server-side fetch of a user-supplied URL without scheme and host pinning or an allowlist: P1 — internal addresses and metadata endpoints are the payload.
- An open redirect on an auth, logout, or payment path the attacker can aim off-site: P2.

## Surface changes
- A dependency added or bumped past an advisory the lockfile names, or a config change that widens exposure — debug mode shipped on, CORS `*` with credentials, a new public route, a permissive default flipped: verify against the deployed setting, not the file alone.

## Exposure
- PII, credentials, or internal detail leaking through logs, error bodies, or API responses to a caller without the rights to it: P1.

## Rejects
- Imagined hardening: "could be more secure", defense-in-depth missing behind a boundary already enforced, a stronger primitive than the threat needs.
- Unreachable triggers: dead code, inputs validated upstream, attacks needing host compromise or physical access.
