import streamlit as st
import pandas as pd
from db import create_connection, get_users
import plotly.graph_objects as go


# Connect to the SQLite database
database = "chores.db"
conn = create_connection(database)

def display_key_metrics(users):
    if users.empty:
        st.write("No user data available.")
        return
    
    highest_level = users['Current Level'].max()
    average_xp = int(users['Total XP'].mean())
    total_users = users.shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Highest Level", highest_level)
    col2.metric("Average XP", average_xp)
    col3.metric("Total Kids", total_users)

def plot_progress_bars(users):
    st.write("## Progress to Next Level")
    for index, row in users.iterrows():
        label = f"{row['Name']} (Level {row['Current Level']} - {row['Total XP']} XP)"
        progress = row['Total XP'] % 100  # Assuming each level up requires 100 XP for simplicity
        st.progress(progress)
        st.write(label)



def generate_user_detail_charts(users):
    if users.empty:
        st.write("No user data available.")
        return

    fig = go.Figure()
    # Add traces
    fig.add_trace(go.Bar(
        x=users['Name'],
        y=users['Current Level'],
        name='Current Level',
        marker_color='indigo'
    ))

    fig.add_trace(go.Scatter(
        x=users['Name'],
        y=users['Total XP'],
        name='Total XP',
        marker_color='green',
        yaxis='y2'
    ))

    # Here we modify the tickangle of the xaxis, making text labels more readable.
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(
            title='Level'
        ),
        yaxis2=dict(
            title='XP',
            overlaying='y',
            side='right'
        ),
        title="Overview of Kids' Levels and Total XP"
    )

    st.plotly_chart(fig, use_container_width=True)

   

def create_progress_chart(name, current_xp, next_level_xp, current_level):
    progress = (current_xp % 100) / 100 * next_level_xp  # Calculate the actual progress towards the next level
    remaining = next_level_xp - progress

    fig = go.Figure(data=[go.Pie(
        labels=["Progress", "Remaining"],
        values=[progress, remaining],
        hole=.7,
        marker_colors=["cyan", "lightgrey"],
        hoverinfo="label+percent"
    )])

    fig.update_layout(
        title=f"{name} - Level {current_level}",
        showlegend=True,
        annotations=[dict(text=f"{int((progress / next_level_xp) * 100)}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    return fig


def dashboard_page():
    st.title("Kids' Progress Dashboard")
    
    # Connect to the SQLite database
    database = "chores.db"
    conn = create_connection(database)

    # Fetch data
    user_data = pd.DataFrame(get_users(conn, st.session_state['admin_id']), columns=["User ID", "Name", "Current Level", "Total XP"])
    
    # Display Metrics and Charts
    display_key_metrics(user_data)
    generate_user_detail_charts(user_data)
    st.subheader ("Progress to Next Level")
    users = pd.DataFrame(get_users(conn, st.session_state['admin_id']), columns=["User ID", "Name", "Current Level", "Total XP"])
    next_level_xp = 100  # Assuming a flat rate for simplification; this could be dynamic.

    cols = st.columns(3)  # Adjust the number of columns based on layout preferences
    col_index = 0

    for _, row in users.iterrows():
        with cols[col_index]:
            fig = create_progress_chart(row['Name'], row['Total XP'], next_level_xp, row['Current Level'])
            st.plotly_chart(fig, use_container_width=True)
        col_index = (col_index + 1) % len(cols)  # Move to the next column

if st.session_state.get('logged_in'):
    dashboard_page()
else:
    st.error("Login to access this page.")



    


