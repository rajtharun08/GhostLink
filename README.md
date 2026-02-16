# GhostLink

GhostLink is a lightweight, self-destructing URL shortener.  
Unlike traditional shorteners, GhostLink URLs automatically delete themselves once they reach a specific click limit or a predefined expiration time.

---

## Features

- Self-Destruction: Links are permanently deleted from the SQLite database after usage limits or time-to-live (TTL) expires.
- Custom Slugs: Create your own short codes (e.g., `/my-secret-link`).
- Memory Efficient: Optimized for systems with synchronous FastAPI and auto-closing SQLite connections.
- Developer Dashboard: Quick endpoints to check active links without triggering click counts.
- Ghosted UI: Themed HTML error pages when links have vanished.

---

## Tech Stack

- Backend: FastAPI (Python 3.x)
- Database: SQLite3
- Environment: python-dotenv

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/rajtharun08/GhostLink.git
cd GhostLink
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

Create a `.env` file in the root directory:

```
DATABASE_URL=ghostlink.db
BASE_URL=http://localhost:8000
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

Open in browser:

```
http://localhost:8000/docs
```

---

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| POST | `/shorten` | Create a short URL with custom `max_clicks` and `ttl_hours`. |
| GET | `/{short_code}` | Redirect and validate link life. |
| GET | `/stats/{short_code}` | View metadata without consuming a click. |

### Management Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| DELETE | `/{short_code}` | Manually delete a link. |
| POST | `/ghost/{short_code}` | Expire a link immediately without deleting the record. |
| PATCH | `/revive/{short_code}` | Add more hours to an existing link's life. |
| DELETE | `/cleanup` | Bulk delete all naturally expired links. |

---

## Usage Examples

### Create a Self-Destructing Link

```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "long_url": "https://google.com",
    "max_clicks": 3,
    "ttl_hours": 24,
    "custom_code": "secret-note"
  }'
```

### Check Link Status

```bash
curl -X GET "http://localhost:8000/stats/secret-note"
```

### Extend Link Life

```bash
curl -X PATCH "http://localhost:8000/revive/secret-note?hours=48"
```

---

