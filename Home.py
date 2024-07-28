import streamlit as st
from db import create_connection, create_tables, login_admin, register_admin
from tracker import show_tracker
from streamlit_cookies_manager import EncryptedCookieManager

  
   # Initialize the cookie manager
cookies = EncryptedCookieManager(prefix="myapp_", password="password")

if not cookies.ready():
       st.stop()



def main():
       database = "chores.db"
       conn = create_connection(database)
       if conn is not None:
           create_tables(conn)
       else:
           st.error("Error! Cannot create the database connection.")
           return

       if 'logged_in' not in st.session_state:
           st.session_state['logged_in'] = False

       if 'mode' not in st.session_state:
           st.session_state['mode'] = 'login'

       # Check for token in cookies
       token = cookies.get("auth_token")
       if token:
           st.session_state['logged_in'] = True
           st.session_state['admin_id'] = token

       if st.session_state['logged_in']:
           show_tracker(conn, st.session_state['admin_id'])
       else:
           col1, col2, col3 = st.columns([1, 2, 1])
           with col2:
               st.title("Login")
               if st.session_state['mode'] == 'login':
                   with st.form("Login Form"):
                       username = st.text_input("Username")
                       password = st.text_input("Password", type="password")
                       submitted = st.form_submit_button("Login")
                       if submitted:
                           admin_id, is_authenticated = login_admin(conn, username, password)
                           if is_authenticated:
                               st.session_state['logged_in'] = True
                               st.session_state['username'] = username
                               st.session_state['admin_id'] = admin_id
                               cookies["auth_token"] = str(admin_id)
                               st.rerun()
                           else:
                               st.error("Incorrect username or password")
                       st.write("New user?")
                       if st.form_submit_button("Register here"):
                           st.session_state['mode'] = 'register'
                           st.rerun()
               elif st.session_state['mode'] == 'register':
                   with st.form("Register Form"):
                       new_username = st.text_input("Choose Username")
                       new_password = st.text_input("Choose Password", type="password")
                       confirm_password = st.text_input("Confirm Password", type="password")
                       register_submitted = st.form_submit_button("Register")
                       if register_submitted:
                           if new_password != confirm_password:
                               st.error("Passwords do not match!")
                           else:
                               if register_admin(conn, new_username, new_password):
                                   st.success("User registered successfully!")
                                   st.session_state['mode'] = 'login'
                                   st.rerun()
                               else:
                                   st.error("Registration failed. User might already exist.")
                   if st.button("Back to Login"):
                       st.session_state['mode'] = 'login'
                       st.rerun()

if __name__ == "__main__":
       main()