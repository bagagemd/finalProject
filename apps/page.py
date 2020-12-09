# StockPredict.py

import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup
import requests 
import json
import time

def app():

    #image = Image.open('logo2.jpg')

    #st.image(image, caption="Stockmarket", use_column_width=True)

    st.title('S&P 500 App')

    st.markdown("""
    This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
    * **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
    * **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
    """)

    st.sidebar.header('User Input Features')

    # Web scraping of S&P 500 data
    #
    @st.cache
    def load_data():
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        html = pd.read_html(url, header = 0)
        df = html[0]
        return df

    df = load_data()
    sector = df.groupby('GICS Sector')

    # Sidebar - Sector selection
    sorted_sector_unique = sorted( df['GICS Sector'].unique() )
    selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

    # Filtering data
    df_selected_sector = df[ (df['GICS Sector'].isin(selected_sector)) ]

    st.header('Display Companies in Selected Sector')
    st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
    st.dataframe(df_selected_sector)

    # Download S&P500 data
    # https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    # https://pypi.org/project/yfinance/

    data = yf.download(
            tickers = list(df_selected_sector[:10].Symbol),
            period = "ytd",
            interval = "1d",
            group_by = 'ticker',
            auto_adjust = True,
            prepost = True,
            threads = True,
            proxy = None
        )

    # Plot Closing Price of Query Symbol
    def price_plot(symbol):
        df = pd.DataFrame(data[symbol].Close)
        df['Date'] = df.index
        plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
        plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
        plt.xticks(rotation=90)
        plt.title(symbol, fontweight='bold')
        plt.xlabel('Date', fontweight='bold')
        plt.ylabel('Closing Price', fontweight='bold')
        return st.pyplot()

    num_company = st.sidebar.slider('Number of Companies', 1, 5)

    if st.button('Show Plots'):
        st.header('Stock Closing Price')
        for i in list(df_selected_sector.Symbol)[:num_company]:
            price_plot(i)


    #image = Image.open('logo.jpg')

    #st.image(image, caption="Cryptocurrencies", use_column_width=True)

    st.title('Crypto Price App')
    st.markdown("""
    This app retrieves Cryptocurrency prices for the top 100 cryptocurrencies

    """)

    expander_bar = st.beta_expander("About")
    expander_bar.markdown("""
    * **Python libraries used:** base64, pandas, streamlit, numpy, matplotlib, BeautifulSoup, requests, json, time
    * **Data Source:** [CoinMarketCap](https://www.coinmarketcap.com/).
    """)

    col1 = st.sidebar
    col2, col3 = st.beta_columns((2,1))

    col1.header('Input Options')

    currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))

    @st.cache
    def load_data():
        cmc = requests.get('https://coinmarketcap.com')
        soup = BeautifulSoup(cmc.content, 'html.parser')

        data = soup.find('script', id='__NEXT_DATA__', type='application/json')
        coins = {}
        coin_data = json.loads(data.contents[0])
        listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
        for i in listings:
            coins[str(i['id'])] = i['slug']

        coin_name = []
        coin_symbol = []
        market_cap = []
        percent_change_1h = []
        percent_change_24h = []
        percent_change_7d = []
        price = []
        volume_24h = []

        for i in listings:
            coin_name.append(i['slug'])
            coin_symbol.append(i['symbol'])
            price.append(i['quote'][currency_price_unit]['price'])
            percent_change_1h.append(i['quote'][currency_price_unit]['percent_change_1h'])
            percent_change_24h.append(i['quote'][currency_price_unit]['percent_change_24h'])
            percent_change_7d.append(i['quote'][currency_price_unit]['percent_change_7d'])
            market_cap.append(i['quote'][currency_price_unit]['market_cap'])
            volume_24h.append(i['quote'][currency_price_unit]['volume_24h'])

        df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'market_cap', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'price', 'volume_24h'])
        df['coin_name'] = coin_name
        df['coin_symbol'] = coin_symbol
        df['price'] = price
        df['percent_change_1h'] = percent_change_1h
        df['percent_change_24h'] = percent_change_24h
        df['percent_change_7d'] = percent_change_7d
        df['market_cap'] = market_cap
        df['volume_24h'] = volume_24h
        return df

    df = load_data()

    sorted_coin = sorted( df['coin_symbol'] )
    selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

    df_selected_coin = df[ (df['coin_symbol'].isin(selected_coin)) ] # Filtering data

    num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
    df_coins = df_selected_coin[:num_coin]

    percent_timeframe = col1.selectbox('Percent change time frame',
                                        ['7d','24h', '1h'])
    percent_dict = {"7d":'percent_change_7d',"24h":'percent_change_24h',"1h":'percent_change_1h'}
    selected_percent_timeframe = percent_dict[percent_timeframe]

    sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

    col2.subheader('Price Data of Selected Cryptocurrency')
    col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

    col2.dataframe(df_coins)

    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
        return href

    col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

    col2.subheader('Table of % Price Change')
    df_change = pd.concat([df_coins.coin_symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d], axis=1)
    df_change = df_change.set_index('coin_symbol')
    df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
    df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
    df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0
    col2.dataframe(df_change)

    col3.subheader('Bar plot of % Price Change')

    if percent_timeframe == '7d':
        if sort_values == 'Yes':
            df_change = df_change.sort_values(by=['percent_change_7d'])
        col3.write('*7 days period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['percent_change_7d'].plot(kind='barh', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    elif percent_timeframe == '24h':
        if sort_values == 'Yes':
            df_change = df_change.sort_values(by=['percent_change_24h'])
        col3.write('*24 hour period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['percent_change_24h'].plot(kind='barh', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    else:
        if sort_values == 'Yes':
            df_change = df_change.sort_values(by=['percent_change_1h'])
        col3.write('*1 hour period*')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['percent_change_1h'].plot(kind='barh', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
