# Implementation Plan: API Token from Environment Variable

## Overview

Add support for an `API_TOKEN` environment variable. When set, Platypush should
accept that token as a valid API token on any authenticated endpoint.

This is targeted at headless / containerized deployments where the full
user-registration and token-issuance HTTP flow is impractical. The operator
simply passes `API_TOKEN=<value>` via the environment (or Docker `-e`), and the
service is immediately accessible using that token.

The token **must not** be displayed in the UI or returned by any "list tokens"
endpoint – it is an operator-level secret, not a user-level one.

## Current Authentication Flow

`platypush/backend/http/app/utils/auth/__init__.py`:

```
authenticate_token(req)
  1. Read X-Token header, Bearer Authorization, or ?token query param
  2. Try validate_api_token(user_token)   ← hashed DB lookup
  3. Try validate_jwt_token(user_token)   ← legacy JWT
  4. Fall back to global_token from config (plain-text equality)
```

## Proposed Change

### `authenticate_token` in `platypush/backend/http/app/utils/auth/__init__.py`

Add a check between steps 3 and 4 (or replace the existing `global_token`
fall-through):

```python
env_token = os.environ.get('API_TOKEN')
if env_token and user_token and secrets.compare_digest(user_token, env_token):
    return User(username='__env_token__', user_id=0)
```

Using `secrets.compare_digest` prevents timing attacks. The returned synthetic
`User` object follows the same pattern as the existing `global_token` path
(`User(username='__token__', user_id=1)`), but uses a distinct username so the
origin can be identified in logs.

### No DB / UI changes required

The env token is ephemeral and intentionally not stored in the database. The
UI's "API Tokens" page only shows `UserToken` rows for normal users – the env
token will not appear there, satisfying the requirement.

## Files to Change

| File | Change |
|------|--------|
| `platypush/backend/http/app/utils/auth/__init__.py` | Add `os` + `secrets` imports (if missing), add env-token check in `authenticate_token` |

## Tests

Add a test case in the existing HTTP/auth test suite (or create
`tests/backend/http/test_auth_env_token.py`) that:

1. Sets `API_TOKEN` in the environment.
2. Sends a request with that token in the `X-Token` / `Authorization: Bearer` /
   `?token` query-string positions.
3. Asserts the request is authenticated.
4. Unsets `API_TOKEN` and asserts the same token is rejected.

## Security Considerations

- `secrets.compare_digest` is used to prevent timing-based side-channel attacks.
- The env token is never written to disk or the DB by Platypush.
- It is the operator's responsibility to keep the environment variable secret
  (use Docker secrets / Kubernetes Secrets / systemd `EnvironmentFile`, etc.).
- The token does not appear in the UI or API listing endpoints.
