# main.py

import streamlit as st
from multiapp import MultiApp
from apps import page

app = MultiApp()
app.add_app("Crypto", page.app)
app.run()
