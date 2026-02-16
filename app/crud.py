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