import streamlit as st
from db import create_connection, create_tables, get_users, get_tasks, log_activity, get_user_activities
import pandas as pd
from datetime import datetime

# Set page config with a more descriptive name
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")



def main():
    # Connect to the SQLite database
    database = "chores.db"
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
    else:
        st.error("Error! Cannot create the database connection.")

    st.sidebar.title("Chore Tracker")

    # User selection
    user_list = get_users(conn)
    user_names = {user[0]: user[1] for user in user_list}  # Dictionary of user_id to user name
    selected_user_id = st.sidebar.selectbox(
        'Select Child', 
        options=list(user_names.keys()), 
        format_func=lambda x: user_names[x],
        key='selected_user_id'
    )
    current_date = datetime.now().date()  # Gets the current date

    if selected_user_id is not None:
        selected_user_details = next((user for user in user_list if user[0] == selected_user_id), None)
        if selected_user_details:
            user_name, current_level, total_xp = selected_user_details[1], selected_user_details[2], selected_user_details[3]

            # Display selected user's progress
            st.title(f"{user_name}'s Chore Progress")
            col1, col2 = st.columns(2)
            with col1:
                st.header("Current Level")
                st.subheader(f"Level {current_level}")
                st.progress(total_xp / 1000)  # Assuming max XP per level increment is 1000
                st.caption(f"{total_xp} XP to Next Level")

            with col2:
                st.header("Total XP")
                st.subheader(f"{total_xp} XP")

            daily_activities = get_user_activities(conn, selected_user_id, str(current_date))
            st.header("Today's Tasks")
            st.dataframe(daily_activities)
       
        st.header("All Tasks")
        all_tasks_query = "SELECT date, task_name, time_spent, xp_earned FROM ActivityLog JOIN Tasks ON ActivityLog.task_id = Tasks.task_id WHERE user_id = ? ORDER BY date DESC"
        c = conn.cursor()
        c.execute(all_tasks_query, (selected_user_id,))
        all_tasks = c.fetchall()
        all_tasks_df = pd.DataFrame(all_tasks, columns=['Date', 'Task Name', 'Time Spent', 'XP Earned'])
        st.dataframe(all_tasks_df)

        

        # Task Management
        with st.sidebar:
            st.header("Task Management")
            task_list = get_tasks(conn)
            task_id = st.selectbox('Select Task', task_list, format_func=lambda x: x[1])
            date = st.date_input("Date")
            time_spent = st.slider("Time Spent (minutes)", 0, 120, 30)
            if st.button('Log Task'):
                log_activity(database, selected_user_id, task_id[0], str(date), time_spent)
                st.session_state.user_activities = get_user_activities(conn, selected_user_id, str(current_date))
                st.success("Task logged successfully!")
                st.experimental_rerun()
                
            
    else:
        st.error("Please select a user.")

if __name__ == "__main__":
    main()
