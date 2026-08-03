# API Token from Environment Variable — Detailed Implementation Guide

This document expands the implementation plan in `01-PLAN.md` with concrete
code-level guidance: exact file to change, the precise edit with surrounding
context, import requirements, edge cases, test strategy, and security rationale.
It is written for an engineer starting implementation on a clean branch.

---

## Table of Contents

1. [Prerequisites and Context](#1-prerequisites-and-context)
2. [Single-File Change: `authenticate_token`](#2-single-file-change-authenticate_token)
3. [Import Requirements](#3-import-requirements)
4. [The Edit: Before and After](#4-the-edit-before-and-after)
5. [Edge Cases and Rationale](#5-edge-cases-and-rationale)
6. [Security Considerations](#6-security-considerations)
7. [Verification Checklist](#7-verification-checklist)
8. [Testing Strategy](#8-testing-strategy)
9. [No-Change Zones](#9-no-change-zones)
10. [Call Graph After Change](#10-call-graph-after-change)

---

## 1. Prerequisites and Context

### 1.1 Existing Code to Understand

Read this file before making any changes:

| File | Why |
|------|-----|
| `platypush/backend/http/app/utils/auth/__init__.py` | Contains `authenticate_token` — the sole function that needs modification |
| `platypush/user/_model.py` | Defines `User` — understand the constructor signature: `User(user_id, username, ...)` |
| `tests/test_auth_env_token.py` | Existing test file — tests should pass after implementation |

### 1.2 The Current Token Authentication Chain

`authenticate_token(req)` at `platypush/backend/http/app/utils/auth/__init__.py:65`:

1. **Extract token** from `X-Token` header, `Authorization: Bearer`, or `?token` query parameter (lines 69–76).
2. **Return `None`** if no token was supplied (lines 78–79).
3. **DB token lookup** via `user_manager.validate_api_token(user_token)`.
4. **Legacy JWT** via `user_manager.validate_jwt_token(user_token)`.
5. **Legacy global token** — plain-text equality against `Config.get('user.global_token')`.

After this change, a new step is inserted between steps 2 and 3: an
environment-variable token check that short-circuits the DB/JWT paths when a
match is found.

### 1.3 Design Constraint

The env token must **never** appear in the UI or any API listing endpoint. Since
it is not stored in the database (no `UserToken` row), this constraint is
satisfied by construction. The UI's "API Tokens" page only displays `UserToken`
rows for registered users.

---

## 2. Single-File Change: `authenticate_token`

**File:** `platypush/backend/http/app/utils/auth/__init__.py`

**Function:** `authenticate_token(req)` (at line 65).

### 2.1 What to Add

Insert an environment-variable token check **after** the token extraction and
empty-token guard (lines 69–79) and **before** the DB-backed
`user_manager.validate_api_token()` call.

The check must:

1. Read the `API_TOKEN` environment variable with `os.environ.get('API_TOKEN')`.
2. If the variable is set, non-empty, and the user-supplied token is non-empty,
   compare them using `secrets.compare_digest`.
3. If they match, return a synthetic `User` object:
   - `username='__env_token__'` (distinct from `'__token__'` used by the global-token fallback, so the origin can be identified in logs).
   - `user_id=0` (distinct from `user_id=1` used by the global-token fallback).
4. If they **don't** match, fall through to the existing DB/JWT/global-token chain
   — do **not** short-circuit with `None`.

### 2.2 Why Before the DB Lookup?

Placing the check before `user_manager.validate_api_token()` means the env token
works even when:

- No users are registered in the database.
- The database plugin is not configured.
- The database is temporarily unreachable.

This is the primary use case: headless / containerized deployments where the
full user-registration flow is impractical.

### 2.3 Why `secrets.compare_digest`?

The Python stdlib `secrets.compare_digest` performs a constant-time string
comparison. This prevents timing side-channel attacks where an attacker measures
response-time differences to infer the byte-by-byte value of the token.

Note: the existing global-token path (line 105) uses plain `==`, which is
**not** constant-time. That is a pre-existing issue outside the scope of this
change.

---

## 3. Import Requirements

The two required modules are **already imported** at the top of the file:

```python
import os          # line 2
import secrets     # line 3
```

No new imports are needed.

---

## 4. The Edit: Before and After

### 4.1 Locate the Insertion Point

Find the block at lines 78–79:

```python
    if not user_token:
        return None

    try:
        # Stantard API token authentication
        return user_manager.validate_api_token(user_token)
```

The new code goes between `return None` and `try:`.

### 4.2 The Code to Insert

Insert exactly this block:

```python
    # Environment-variable token authentication.
    # If the API_TOKEN environment variable is set, requests bearing that
    # exact token value are accepted without a DB lookup.  This is intended
    # for headless / containerised deployments where the normal
    # user-registration flow is impractical.
    env_token = os.environ.get('API_TOKEN')
    if env_token and user_token and secrets.compare_digest(user_token, env_token):
        return User(username='__env_token__', user_id=0)
```

### 4.3 Resulting Function (lines 65–115 after edit)

```python
def authenticate_token(req) -> Optional[User]:
    global_token = Config.get('user.global_token')
    user_token = None

    if 'X-Token' in req.headers:
        user_token = req.headers['X-Token']
    elif 'Authorization' in req.headers and req.headers['Authorization'].startswith(
        'Bearer '
    ):
        user_token = req.headers['Authorization'][7:]
    else:
        user_token = get_arg(req, 'token')

    if not user_token:
        return None

    # Environment-variable token authentication.
    # If the API_TOKEN environment variable is set, requests bearing that
    # exact token value are accepted without a DB lookup.  This is intended
    # for headless / containerised deployments where the normal
    # user-registration flow is impractical.
    env_token = os.environ.get('API_TOKEN')
    if env_token and user_token and secrets.compare_digest(user_token, env_token):
        return User(username='__env_token__', user_id=0)

    try:
        # Stantard API token authentication
        return user_manager.validate_api_token(user_token)
    except Exception as e:
        try:
            # Legacy JWT token authentication
            return user_manager.validate_jwt_token(user_token)
        except Exception as ee:
            logger().debug(
                'Invalid token. API token error: %s, JWT token error: %s', e, ee
            )

            # Legacy global token authentication.
            # The global token should be specified in the configuration file,
            # as a root parameter named `token`.
            if bool(global_token and user_token == global_token):
                return User(username='__token__', user_id=1)

            logger().info(e)
```

No other function in this file is touched.

---

## 5. Edge Cases and Rationale

### 5.1 `API_TOKEN` Not Set

`os.environ.get('API_TOKEN')` returns `None`.
`None` is falsy → the `if env_token and ...` guard short-circuits.
The check is skipped entirely. No performance impact when the feature is not in
use.

### 5.2 `API_TOKEN` Set to Empty String

`os.environ.get('API_TOKEN')` returns `''`.
`''` is falsy → same short-circuit as 5.1.
An empty env var grants no access.

### 5.3 User Sends Empty Token

`user_token = ''`.
`''` is falsy → the `if env_token and user_token and ...` guard short-circuits.
But `user_token` was already checked on line 78 (`if not user_token: return
None`), so this case is handled even earlier — execution never reaches the env
token check.

### 5.4 Wrong Token Value

`env_token = 'correct-secret'`, `user_token = 'wrong-value'`.
`secrets.compare_digest('wrong-value', 'correct-secret')` → `False`.
The block does not return. Execution falls through to the DB/JWT/global-token
chain. The env token path adds no observable difference in timing or error
message compared to when `API_TOKEN` is unset.

### 5.5 Coexistence with Registered Users

The env token check runs **before** any DB query. If a registered user exists
and the request carries the env token, the env token wins — the DB is never
queried. This is intentional: the env token is an operator-level credential and
should not require a user record to exist.

If the request carries a **different** token (one that matches a registered
user's token but not `API_TOKEN`), the env check fails and execution falls
through to the normal `validate_api_token` path. Normal user tokens continue to
work.

### 5.6 Coexistence with the Legacy `global_token`

The env token check runs **before** the global-token fallback. If both are
configured, the env token path returns `user_id=0, username='__env_token__'`
while the global token path returns `user_id=1, username='__token__'`. They are
independent — which one fires depends on which token value the client sends.

---

## 6. Security Considerations

### 6.1 Constant-Time Comparison

`secrets.compare_digest` prevents timing-based side-channel attacks. See
[section 2.3](#23-why-secretscompare_digest).

### 6.2 No Persistence

The env token is never written to disk, the database, or any log by Platypush.
It exists only in the process environment (the `os.environ` dict, populated by
the OS before the Python process starts). The operator is responsible for
keeping it secret through their chosen mechanism:

- **Docker:** `docker run -e API_TOKEN=...` or Docker secrets.
- **Kubernetes:** `env[].valueFrom.secretKeyRef`.
- **systemd:** `EnvironmentFile=` pointing to a `0600` file.
- **Manual:** `export API_TOKEN=...` before starting Platypush.

### 6.3 No UI Leakage

The synthetic `User(username='__env_token__', user_id=0)` has no corresponding
row in the `user` table and no `UserToken` row. The UI's token management page
queries `UserToken` rows for the current user — this token will never appear
there.

### 6.4 Audit Trail

Log entries from requests authenticated via the env token will reference
`user='__env_token__'` (from Flask's `g.user`) or `user_id=0`, depending on the
logging layer. This is distinguishable from:

| Auth Method | `username` | `user_id` |
|-------------|-----------|----------|
| Env token | `__env_token__` | `0` |
| Global token | `__token__` | `1` |
| Normal user | actual username | `>= 2` |

---

## 7. Verification Checklist

After implementing the change, verify each of these:

- [ ] Request with `X-Token: <correct env token>` → authenticated, user is `__env_token__`.
- [ ] Request with `Authorization: Bearer <correct env token>` → authenticated.
- [ ] Request with `?token=<correct env token>` → authenticated.
- [ ] Request with wrong token value → rejected, falls through to DB/JWT/global chain.
- [ ] Request with empty token → rejected.
- [ ] Request when `API_TOKEN` is unset → normal auth flow, no errors.
- [ ] Request when `API_TOKEN` is set to empty string → same as unset.
- [ ] Existing tests for token, JWT, session, and user/pass auth still pass.
- [ ] The env token does not appear in the UI's API Tokens page.
- [ ] Logs show `__env_token__` as the username for env-token-authenticated requests.

---

## 8. Testing Strategy

### 8.1 Test File

**File:** `tests/test_auth_env_token.py`

### 8.2 Test Approach

The tests use `unittest.mock.patch.dict` to temporarily set `API_TOKEN` in
`os.environ`. This isolates each test from the others and from the host
environment. The tests construct minimal fake request objects and call
`authenticate_token` directly — no HTTP server, no database, no Flask
application context is needed.

### 8.3 Fake Request Helper

```python
class _FakeRequest:
    """Minimal request stub that `authenticate_token` can inspect."""

    def __init__(self, headers=None, args=None):
        self.headers = headers or {}
        self._args = args or {}

    # Flask-style args
    @property
    def args(self):
        return self._args
```

### 8.4 Test Cases

| Test | Input | Expected |
|------|-------|----------|
| `test_x_token_header_accepted` | `X-Token: <env_token>`, `API_TOKEN` set | Returns `User(username='__env_token__')` |
| `test_bearer_authorization_accepted` | `Authorization: Bearer <env_token>`, `API_TOKEN` set | Returns `User(username='__env_token__')` |
| `test_query_param_accepted` | `?token=<env_token>`, `API_TOKEN` set | Returns `User(username='__env_token__')` |
| `test_wrong_token_rejected` | `X-Token: wrong-value`, `API_TOKEN` set | Returns `None` |
| `test_no_env_var_set` | `API_TOKEN` absent from environment | Returns `None` |
| `test_empty_env_var_rejected` | `API_TOKEN=''`, user sends `''` | Returns `None` |

### 8.5 Running the Tests

```bash
# Run only the env-token tests
python -m pytest tests/test_auth_env_token.py -v

# Run the full auth test suite to check for regressions
python -m pytest tests/ -k "auth" -v
```

### 8.6 What the Unit Tests Don't Cover

- **Full HTTP integration:** The unit tests call `authenticate_token` directly
  with fake requests. They do not exercise the Flask routing layer
  (`get_current_user_or_auth_status` → `authenticate_token`). An integration
  test against a running Platypush instance with `API_TOKEN` set would cover
  this — see the verification checklist in section 7.
- **Timing side-channel resistance:** Unit tests cannot verify that
  `secrets.compare_digest` runs in constant time. This is a trust-in-stdlib
  property.

---

## 9. No-Change Zones

The following areas are **not** modified by this feature:

| Area | Why Untouched |
|------|---------------|
| `UserManager` / `validate_api_token` | Env token bypasses DB entirely |
| `UserToken` model or DB schema | No persistence needed |
| `platypush/config.py` or config schema | Token source is the environment, not a config key |
| Any Flask route or Blueprint | `authenticate_token` is the single chokepoint for all token auth |
| UI / frontend token management | Env token is invisible by design — no `UserToken` row |
| `get_current_user_or_auth_status` | Calls `authenticate_token` with no changes needed |
| `authenticate_user_pass` | Unrelated HTTP Basic auth method |
| `authenticate_session` / `authenticate_session_with_csrf` | Unrelated session auth methods |
| Global token path (`config.yaml` `token:` key) | Preserved as-is; env token check runs before it |

---

## 10. Call Graph After Change

```
Request arrives at any authenticated endpoint
│
▼
get_current_user_or_auth_status(req)
│
├── authenticate_user_pass(req)              [HTTP Basic Auth]
│
├── authenticate_token(req)                  ← THE CHANGED FUNCTION
│   │
│   ├── 1. Extract token from X-Token / Bearer / ?token
│   ├── 2. If no token → return None
│   ├── 3. ★ NEW: If API_TOKEN is set and matches → return User('__env_token__', user_id=0)
│   ├── 4. Try user_manager.validate_api_token(user_token)   [DB lookup]
│   ├── 5. Try user_manager.validate_jwt_token(user_token)   [Legacy JWT]
│   └── 6. Fallback: global_token plain-text equality          [Legacy config]
│
├── authenticate_session(req)                [Session cookie]
│
└── If no user AND no users exist → REGISTRATION_REQUIRED
```

---

*End of implementation guide. See `01-PLAN.md` for the requirements context and
acceptance criteria, and `tests/test_auth_env_token.py` for the test cases.*
