import psycopg2
import re
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # User
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Stat
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_stats (
            id SERIAL PRIMARY KEY,
            user_id INT UNIQUE NOT NULL,
            victories INT DEFAULT 0,
            killed_by_wumpus INT DEFAULT 0,
            fell_in_pit INT DEFAULT 0,
            miss_shot INT DEFAULT 0,
            games_played INT DEFAULT 0,
            CONSTRAINT player_stats_user_fk
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # Classement
    cur.execute("""
        CREATE OR REPLACE VIEW leaderboard AS
        SELECT u.username,
               ps.victories AS score_total,
               ps.games_played,
               ps.killed_by_wumpus,
               ps.fell_in_pit,
               ps.miss_shot
        FROM player_stats ps
        JOIN users u ON ps.user_id = u.id
        ORDER BY ps.victories DESC, ps.games_played ASC;
    """)

    conn.commit()
    cur.close()
    conn.close()

def add_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    hashed_password = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
        (username, hashed_password)
    )
    user_id = cur.fetchone()[0]

    cur.execute(
        "INSERT INTO player_stats (user_id) VALUES (%s);",
        (user_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

def is_user_used(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE username = %s;", (username,))
    is_used = cur.fetchone()

    cur.close()
    conn.close()

    return is_used is not None

def is_pwd_ok(password):
    regex = r"^(?=.*[A-Z])(?=.*\d).{6,}$"
    return bool(re.match(regex, password))

def verify_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT password FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user is None:
        return False

    return check_password_hash(user[0], password)

def update_stats(username, event):
    """Incrémente la statistique globale et l'événement de fin de partie."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE player_stats SET games_played = games_played + 1
        WHERE user_id = (SELECT id FROM users WHERE username = %s);
    """, (username,))

    if event == "win":
        query = """
            UPDATE player_stats SET victories = victories + 1
            WHERE user_id = (SELECT id FROM users WHERE username = %s);
        """
    elif event == "wumpus":
        query = """
            UPDATE player_stats SET killed_by_wumpus = killed_by_wumpus + 1
            WHERE user_id = (SELECT id FROM users WHERE username = %s);
        """
    elif event == "pits":
        query = """
            UPDATE player_stats SET fell_in_pit = fell_in_pit + 1
            WHERE user_id = (SELECT id FROM users WHERE username = %s);
        """
    else:
        query = """
            UPDATE player_stats SET miss_shot = miss_shot + 1
            WHERE user_id = (SELECT id FROM users WHERE username = %s);
        """

    cur.execute(query, (username,))
    conn.commit()
    cur.close()
    conn.close()

def get_leaderboard():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM leaderboard;")
    rankings = cur.fetchall()

    cur.close()
    conn.close()
    return rankings

def suppcompte(username) :
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM users WHERE username = %s;
    """, (username,))
    conn.commit()
    cur.close()
    conn.close()