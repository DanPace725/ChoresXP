import streamlit as st
from chores import get_user_xp
from db import create_connection, get_users
import pandas as pd

# Connect to the SQLite database
database = "chores.db"
conn = create_connection(database)

def dashboard_page():
    
    st.title("XP Chart for All Kids")
    user_xp_data = get_user_xp(conn)  # Assuming you have many users
    st.bar_chart(user_xp_data.set_index('Name'))


def generate_user_level_chart(conn):
    users = get_users(conn)
    if users:
        user_levels = pd.DataFrame(users, columns=["User ID", "Name", "Current Level", "Total XP"])
        st.bar_chart(user_levels.set_index('Name')['Current Level'])
    else:
        st.write("No user data available.")

# Generate the user level chart
generate_user_level_chart(conn)

if __name__ == "__main__":
    dashboard_page()
