import streamlit as st
from db import create_connection, add_task, delete_task, add_user, delete_user, update_user, get_users, get_tasks, get_levels, add_level, update_level_details
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(page_title="Admin", page_icon="🔑", layout="wide")
cookies = EncryptedCookieManager(prefix="myapp_", password="password")

if not cookies.ready():
    st.stop()

def manage_levels(conn, admin_id):
    with st.expander("Manage Levels"):
        col1, col2 = st.columns(2)

        # Adding new level
        with col1:
            with st.form("Add Level"):
                level = st.number_input("Level Number", min_value=1, step=1)
                xp_required = st.number_input("XP Required", min_value=0, step=10)
                cumulative_xp = st.number_input("Cumulative XP", min_value=0, step=10)
                reward = st.text_input("Reward")
                if st.form_submit_button("Add Level"):
                    add_level(conn, admin_id, level, xp_required, cumulative_xp, reward)
                    st.success("Level added successfully!")

        # Updating existing level
        with col2:
            levels = get_levels(conn, admin_id)
            level_options = {level[0]: f"Level {level[0]}" for level in levels}
            selected_level = st.selectbox("Select Level to Edit", options=list(level_options.keys()), format_func=lambda x: level_options[x])
            level_details = next((lvl for lvl in levels if lvl[0] == selected_level), None)
            
            if level_details:
                xp_required_value = int(level_details[1]) if level_details[1] is not None else 0
                cumulative_xp_value = int(level_details[2]) if level_details[2] is not None else 0
                xp_required = st.number_input("Edit XP Required", min_value=0, step=10, value=xp_required_value)
                cumulative_xp = st.number_input("Edit Cumulative XP", min_value=0, step=10, value=cumulative_xp_value)
                reward = st.text_input("Edit Reward", value=level_details[3])
                
                if st.button(f"Update Level {selected_level}"):
                    update_level_details(conn, admin_id, selected_level, xp_required, cumulative_xp, reward)
                    st.success(f"Level {selected_level} updated successfully!")
                    st.experimental_rerun()  # Optionally, rerun to update the level list immediately.
    
def admin_page():
    st.title("Admin Tools")
    database = "chores.db"
    conn = create_connection(database)

    with st.expander("Manage Tasks"):
        col1, col2 = st.columns(2)
        with col1:
            with st.form("Add Task"):
                new_task_name = st.text_input("New Task Name")
                new_task_xp = st.number_input("Base XP", min_value=0)
                new_task_multiplier = st.number_input("Time Multiplier", min_value=0.0, step=0.1)
                if st.form_submit_button('Add New Task'):
                    add_task(conn, st.session_state['admin_id'], new_task_name, new_task_xp, new_task_multiplier)
                    st.success("New task added!")
        with col2:
            with st.form("Remove Tasks"):
                tasks = get_tasks(conn, st.session_state['admin_id'])
                task_to_remove = st.selectbox("Select a task to remove", tasks, format_func=lambda x: x[1], key="remove_task")
                if st.form_submit_button("Remove Task"):
                    delete_task(conn, task_to_remove[0])
                    st.success(f"Task '{task_to_remove[1]}' removed successfully!")
                    st.rerun()

    with st.expander("Manage Children"):
        col1, col2 = st.columns(2)
        with col1:
            with st.form("Add Child"):
                child_name = st.text_input("Child's Name")
                if st.form_submit_button("Add Child"):
                    add_user(conn, st.session_state['admin_id'], child_name)
                    st.success("Child added successfully!")
        with col2:
            children = get_users(conn, st.session_state['admin_id'])
            child_to_remove = st.selectbox("Select a child to remove", children, format_func=lambda x: x[1], key="remove_child")
            if st.button("Remove Child"):
                delete_user(conn, child_to_remove[0])
                st.success(f"Child '{child_to_remove[1]}' removed successfully!")
                st.experimental_rerun()

    manage_levels(conn, st.session_state['admin_id'])
    with st.expander("View All Data"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("All Users and XP Data")
            users = get_users(conn, st.session_state['admin_id'])
            if users:
                users_df = pd.DataFrame(users, columns=["User ID", "Name", "Current Level", "Total XP"])
                users_df.set_index("User ID", inplace=True)
                st.dataframe(users_df)
            else:
                st.write("No users data available.")
        with col2:
            st.subheader("All Tasks")
            tasks = get_tasks(conn, st.session_state['admin_id'])
            if tasks:
                tasks_df = pd.DataFrame(tasks, columns=["Task ID", "Task Name", "Base XP", "Time Multiplier"])
                tasks_df.set_index("Task ID", inplace=True)
                st.dataframe(tasks_df)
            else:
                st.write("No tasks data available.")
        with col3:
            st.subheader("All Rewards")
            levels = get_levels(conn, st.session_state['admin_id'])
            if levels:
                levels_df = pd.DataFrame(levels, columns=["Level", "XP Required", "Cumulative XP", "Reward"])
                levels_df.set_index("Level", inplace=True)
                st.dataframe(levels_df)
            else:
                st.write("No level data available.")

    if st.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        cookies.delete("auth_token")
        st.success("You have been logged out.")
        st.experimental_set_query_params(page='home')
        st.experimental_rerun()

if st.session_state.get('logged_in'):
    admin_page()
else:
    st.error("Login to access this page.")