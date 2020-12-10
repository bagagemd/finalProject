import streamlit as st
import string
import sqlite3
import SessionState
import streamlit as st
import requests
import webbrowser


conn = sqlite3.connect('logins.db')
c = conn.cursor()
#c.execute('''DROP TABLE IF EXISTS users''')
c.execute('''CREATE TABLE IF NOT EXISTS users
             (userid integer, username text, pass text)''')

#conn.close()

st.text("Login.")

conn = sqlite3.connect('logins.db')
c = conn.cursor()
c.execute("INSERT INTO users VALUES (1, 'user', 'password')")
conn.commit()

input_user = st.text_input("Enter your username.")
input_pass = st.text_input("Enter your password.", type='password')
if st.button("Login"):
    username = input_user
    password = input_pass
    st.write(input_user)
    c.execute("""SELECT username
                          ,pass
                   FROM users
                   WHERE username=?
                       OR pass=?""",
                (username, password))
    result = c.fetchone()
    if result:
        st.success("Login success")
        strURL = "http://18.188.202.87:8501/"
        webbrowser.open(strURL)
    else:
        st.error("Error, username and password not found in database.")



session = SessionState.get(open = 0)
if st.button("Create Account") or session.open==1:
    session.open = 1
    new_user = st.text_input("Enter your new username.")
    new_pass = st.text_input("Enter your new password.", type='password')
    c.execute("SELECT count(*) FROM users")
    uid = c.fetchone()[0] + 1
    if st.button("Create"):
        c.execute("""SELECT username FROM users WHERE username=?""", (new_user,))
        result = c.fetchone()
        if result:
            st.error("Error, a user with that name already exists.")
        else:
            c.execute("""INSERT INTO users VALUES (?, ?, ?);""", (new_user, new_pass, uid))
            st.success("New user successfully created.")
            conn.commit()
conn.commit()
conn.close()
