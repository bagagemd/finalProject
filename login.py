import streamlit as st
import string
import sqlite3
import SessionState
import streamlit as st
from multiapp import MultiApp
from apps import page

#loggedIn = False


app = MultiApp()
app.add_app("Crypto & Stocks", page.app)

conn = sqlite3.connect('logins.db')
c = conn.cursor()
#c.execute('''DROP TABLE IF EXISTS users''')
c.execute('''CREATE TABLE IF NOT EXISTS users
             (userid integer, username text, pass text)''')

st.text("Login.")

c.execute("INSERT INTO users VALUES (1, 'user', 'password')")

input_user = st.text_input("Enter your username.")
input_pass = st.text_input("Enter your password.", type='password')
loginSession = SessionState.get(loggedIn = False)
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
        loginSession.loggedIn = True
        app.run()
    else:
        st.error("Error, username and password not found in database.")

button1 = 0
session = SessionState.get(button1 = 0)
if st.button("Create Account") or session.button1==1:
    session.button1 = 1
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


c.close()
