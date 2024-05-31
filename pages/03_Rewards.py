import streamlit as st
from db import create_connection, get_levels, update_reward

st.set_page_config(page_title="Rewards", page_icon="�", layout="wide")

def manage_rewards_page():
    st.title("Manage Rewards")

    # Connect to the SQLite database
    database = "chores.db"
    conn = create_connection(database)
    
    levels = get_levels(conn, st.session_state['admin_id'])
    if levels:
        # Display levels and allow reward updates
        for level in levels:
            with st.expander(f"Level {level[0]}: {level[2]} Cumulative XP"):
                current_reward = st.text_input(f"Reward for Level {level[0]}", value=level[3])
                if st.button(f"Update Reward for Level {level[0]}"):
                    update_reward(conn, level[0], current_reward, st.session_state['admin_id'])
                    st.success(f"Reward updated for Level {level[0]}")
                    st.experimental_rerun()
    else:
        st.write("No level data available.")

if st.session_state.get('logged_in'):
    manage_rewards_page()
else:
    st.error("Login to access this page.")
