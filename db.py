import sqlite3
import pandas as pd

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def create_tables(conn):
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        current_level INTEGER DEFAULT 1,
        total_xp INTEGER DEFAULT 0
    );
    """
    create_tasks_table_sql = """
    CREATE TABLE IF NOT EXISTS Tasks (
        task_id INTEGER PRIMARY KEY,
        task_name TEXT NOT NULL,
        base_xp INTEGER NOT NULL,
        time_multiplier REAL NOT NULL
    );
    """
    create_activity_log_table_sql = """
    CREATE TABLE IF NOT EXISTS ActivityLog (
        activity_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        task_id INTEGER,
        date TEXT NOT NULL,
        time_spent INTEGER,
        xp_earned INTEGER,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
    );
    """
    create_levels_table_sql = """
    CREATE TABLE IF NOT EXISTS Levels (
        Level INTEGER PRIMARY KEY,
        XPRequired INTEGER,
        CumulativeXP INTEGER,
        Reward TEXT
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_users_table_sql)
        c.execute(create_tasks_table_sql)
        c.execute(create_activity_log_table_sql)
        c.execute(create_levels_table_sql)
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def calculate_xp(base_xp, time_spent, multiplier):
    return base_xp + (time_spent * multiplier)

def log_activity(db_path, user_id, task_id, date, time_spent):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get task details
    c.execute("SELECT base_xp, time_multiplier FROM Tasks WHERE task_id = ?", (task_id,))
    task = c.fetchone()
    xp_earned = calculate_xp(task[0], time_spent, task[1])

    # Log the activity
    c.execute("INSERT INTO ActivityLog (user_id, task_id, date, time_spent, xp_earned) VALUES (?, ?, ?, ?, ?)",
              (user_id, task_id, date, time_spent, xp_earned))
    conn.commit()

    # Update user total XP and level
    c.execute("UPDATE Users SET total_xp = total_xp + ? WHERE user_id = ?", (xp_earned, user_id))
    conn.commit()

    # Assuming a function update_level exists to handle level progression
    update_level(conn, user_id)

    conn.close()

def update_level(conn, user_id):
    # Retrieve the current XP
    c = conn.cursor()
    c.execute("SELECT total_xp FROM Users WHERE user_id = ?", (user_id,))
    total_xp = c.fetchone()[0]

    # Define level thresholds
    levels = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]  # Add more as needed
    new_level = len([x for x in levels if x <= total_xp])

    # Update the user's level if it has changed
    c.execute("UPDATE Users SET current_level = ? WHERE user_id = ?", (new_level, user_id))
    conn.commit()

def get_users(conn):
    c = conn.cursor()
    c.execute("SELECT user_id, name, current_level, total_xp FROM Users")
    users = c.fetchall()
    return users

def get_tasks(conn):
    c = conn.cursor()
    c.execute("SELECT task_id, task_name, base_xp, time_multiplier FROM Tasks")
    tasks = c.fetchall()
    return tasks



def add_task(conn, task_name, base_xp, time_multiplier):
    c = conn.cursor()
    c.execute("INSERT INTO Tasks (task_name, base_xp, time_multiplier) VALUES (?, ?, ?)", (task_name, base_xp, time_multiplier))
    conn.commit()

def update_task(conn, task_id, task_name, base_xp, time_multiplier):
    c = conn.cursor()
    c.execute("UPDATE Tasks SET task_name = ?, base_xp = ?, time_multiplier = ? WHERE task_id = ?", (task_name, base_xp, time_multiplier, task_id))
    conn.commit()

def delete_task(conn, task_id):
    c = conn.cursor()
    c.execute("DELETE FROM Tasks WHERE task_id = ?", (task_id,))
    conn.commit()

def add_user(conn, name):
    c = conn.cursor()
    c.execute("INSERT INTO Users (name, current_level, total_xp) VALUES (?, 1, 0)", (name,))
    conn.commit()

def update_user(conn, user_id, name):
    c = conn.cursor()
    c.execute("UPDATE Users SET name = ? WHERE user_id = ?", (name, user_id))
    conn.commit()

def delete_user(conn, user_id):
    c = conn.cursor()
    c.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
    conn.commit()

def get_levels(conn):
    c = conn.cursor()
    c.execute("SELECT Level, XPRequired, CumulativeXP, Reward FROM Levels ORDER BY Level")
    return c.fetchall()

def update_reward(conn, level, reward):
    c = conn.cursor()
    c.execute("UPDATE Levels SET Reward = ? WHERE Level = ?", (reward, level))
    conn.commit()
def get_user_xp(conn):
    c = conn.cursor()
    c.execute("SELECT name, total_xp FROM Users ORDER BY total_xp DESC")
    data = c.fetchall()
    return pd.DataFrame(data, columns=['Name', 'Total XP'])

def get_user_activities(conn, user_id, date):
    c = conn.cursor()
    query = """
    SELECT a.date, t.task_name, a.time_spent, a.xp_earned
    FROM ActivityLog a
    JOIN Tasks t ON a.task_id = t.task_id
    WHERE a.user_id = ? AND a.date = ?
    """
    c.execute(query, (user_id, date))
    activities = c.fetchall()
    df = pd.DataFrame(activities, columns=['Date', 'Task Name', 'Time Spent', 'XP Earned'])
    return df
