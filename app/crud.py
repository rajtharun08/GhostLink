from datetime import datetime, timedelta

def create_link(conn, long_url, max_clicks, ttl_hours, short_code):
    """Inserts a new shortened link into the database."""
    expires_at = datetime.now() + timedelta(hours=ttl_hours)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO links (short_code, long_url, max_clicks, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (short_code, long_url, max_clicks, expires_at)
    )
    conn.commit()
    return short_code

def get_link(conn, short_code):
    """Fetches a link record by its short code."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM links WHERE short_code = ?", (short_code,))
    return cursor.fetchone()

def increment_clicks(conn, short_code):
    """Adds 1 to the current click count."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE links SET current_clicks = current_clicks + 1 WHERE short_code = ?",
        (short_code,)
    )
    conn.commit()

def delete_link(conn, short_code):
    """Permanently removes a link from the database."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM links WHERE short_code = ?", (short_code,))
    conn.commit()