# main.py

import streamlit as st
from multiapp import MultiApp
from apps import CryptoPredict, StockPredict

app = MultiApp()
app.add_app("Crypto", CryptoPredict.app)
app.add_app("Stocks", StockPredict.app)
app.run()
