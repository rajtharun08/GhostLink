# GhostLink
A self-destructing URL shortener built with FastAPI and SQLite. URLs 'ghost' after reaching click limits or expiration.

## Endpoints
- `POST /shorten`: Create a ghost link.
- `GET /{short_code}`: Redirect and consume a click.
- `GET /stats/{short_code}`: Check link status.