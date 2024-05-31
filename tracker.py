import streamlit as st
from db import create_connection, create_tables, get_users, get_tasks, log_activity, get_user_activities, login_admin
import pandas as pd
from datetime import datetime


def main():
    # Set up the Streamlit page
    st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
    database = "chores.db"
    conn = create_connection(database)
    create_tables(conn)

    # Handle login
    if 'admin_id' not in st.session_state:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            admin_id = login_admin(conn, username, password)
            if admin_id:
                st.session_state['admin_id'] = admin_id
            else:
                st.sidebar.error("Invalid username or password")
    
    if 'admin_id' in st.session_state:
        show_tracker(conn, st.session_state['admin_id'])

def show_tracker(conn, admin_id):
    st.sidebar.title("Chore Tracker")
    
    # Fetching user-specific data
    user_list = get_users(conn, admin_id)
    
    
    user_names = {user[0]: user[1] for user in user_list}
    selected_user_id = st.sidebar.selectbox('Select Child', options=list(user_names.keys()), format_func=lambda x: user_names[x])
    
    current_date = datetime.now().date()
    if selected_user_id:
        display_user_progress(conn, selected_user_id, admin_id, current_date)
        st.sidebar.title("Manage Activities")
        with st.sidebar:
            manage_tasks(conn, selected_user_id, admin_id)
        
    else:
        st.error("Please select a user.")

def display_user_progress(conn, user_id, admin_id, current_date):
    """Displays the progress of the selected user."""
    user_details = get_users(conn, admin_id)
    # Filter user_details to match the provided user_id
    user_details = [user for user in user_details if user[0] == user_id]
    if user_details:
        user_name, current_level, total_xp = user_details[0][1], user_details[0][2], user_details[0][3]
        st.title(f"{user_name}'s Chore Progress")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Current Level")
            st.subheader(f"Level {current_level}")
            st.progress(total_xp / 1000)  # Example XP progression
            st.caption(f"{total_xp} XP to Next Level")
        with col2:
            st.header("Total XP")
            st.subheader(f"{total_xp} XP")
        
        # Fetch and display today's tasks for the user
        today_tasks = get_user_activities(conn, admin_id, user_id, str(current_date))
        if not today_tasks.empty:
            st.header("Today's Tasks")
            st.dataframe(today_tasks)
        else:
            st.write("No tasks for today.")
def manage_tasks(conn, user_id, admin_id):
    """Manages tasks and activities for the selected user."""
    task_list = get_tasks(conn, admin_id)
    # Assuming get_tasks returns a list of tuples like [(task_id, task_name), ...]
    task_options = {task[0]: task[1] for task in task_list}  # Create a dictionary to map task IDs to task names
    task_id = st.sidebar.selectbox('Select Task', options=list(task_options.keys()), format_func=lambda x: task_options[x])
    date = st.sidebar.date_input("Date")
    time_spent = st.sidebar.slider("Time Spent (minutes)", 0, 120, 30)
    if st.sidebar.button('Log Task'):
        log_activity(conn, admin_id, user_id, task_id, str(date), time_spent)
        st.success("Task logged successfully!")
        st.rerun()

if __name__ == "__main__":
    main()
