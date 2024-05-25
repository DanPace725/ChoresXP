import streamlit as st
from db import create_connection, add_task, delete_task, add_user, delete_user, update_user, get_users, get_tasks, get_levels
import pandas as pd

st.set_page_config(page_title="Admin", page_icon="🔑", layout="wide")
    
def admin_page():
    st.title("Admin Tools")

    # Connect to the SQLite database
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
                    add_task(conn, new_task_name, new_task_xp, new_task_multiplier)
                    st.success("New task added!")

        with col2:
            with st.form("Remove Tasks"):
                tasks = get_tasks(conn)
                task_to_remove = st.selectbox("Select a task to remove", tasks, format_func=lambda x: x[1], key="remove_task")
                if st.form_submit_button("Remove Task"):
                    delete_task(conn, task_to_remove[0])  # Pass the task_id of the selected task
                    st.success(f"Task '{task_to_remove[1]}' removed successfully!")
                    st.rerun()  # Optionally, rerun to update the task list immediately

    with st.expander("Manage Children"):
        col1, col2 = st.columns(2)

        with col1:
            with st.form("Add Child"):
                child_name = st.text_input("Child's Name")
                if st.form_submit_button("Add Child"):
                    add_user(conn, child_name)
                    st.success("Child added successfully!")

        with col2:
            children = get_users(conn)
            child_to_remove = st.selectbox("Select a child to remove", children, format_func=lambda x: x[1], key="remove_child")
            if st.button("Remove Child"):
                delete_user(conn, child_to_remove[0])  # Pass the user_id of the selected child
                st.success(f"Child '{child_to_remove[1]}' removed successfully!")
                st.rerun()  # Optionally, rerun to update the child list immediately
                

    with st.expander("View All Data"):
        

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("All Users and XP Data")
            users = get_users(conn)
            if users:
                users_df = pd.DataFrame(users, columns=["User ID", "Name", "Current Level", "Total XP"])
                users_df.set_index("User ID", inplace=True)
                st.dataframe(users_df)
            else:
                st.write("No users data available.")

        with col2:
            st.subheader("All Tasks")
            tasks = get_tasks(conn)
            if tasks:
                tasks_df = pd.DataFrame(tasks, columns=["Task ID", "Task Name", "Base XP", "Time Multiplier"])
                tasks_df.set_index("Task ID", inplace=True)
                st.dataframe(tasks_df)
            else:
                st.write("No tasks data available.")

        with col3:
            st.subheader("All Rewards")
            levels = get_levels(conn)
            if levels:
                levels_df = pd.DataFrame(levels, columns=["Level", "XP Required", "Cumulative XP", "Reward"])
                levels_df.set_index("Level", inplace=True)
                st.dataframe(levels_df)
            else:
                st.write("No level data available.")

if st.session_state['logged_in']:
    admin_page()
