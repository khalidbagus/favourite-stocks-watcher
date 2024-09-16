import streamlit as st
from cassandra.cluster import Cluster
import json
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import altair as alt
import time
from datetime import datetime
import requests
import yfinance as yf
import plotly.graph_objs as go
import os

import streamlit_authenticator as stauth

# User Authentication Setup
import yaml
from yaml.loader import SafeLoader
import hashlib


# Load user data from YAML file (use a file or database for storage)
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Cassandra connection setup
def connect_to_cassandra():
    cluster = Cluster(['localhost'])
    session = cluster.connect('financial_data')  # Keyspace
    return session

# Check if ticker exists in Cassandra
def check_ticker_in_cassandra(session, ticker):
    query = "SELECT * FROM company_reports WHERE ticker=%s"
    result = session.execute(query, [ticker])
    return result.one() is not None

# Trigger Kafka Producer and Spark Streaming for all tickers
def trigger_kafka_spark_pipeline(tickers):
    subprocess.run(['python', 'kafka_script/company_report_producer.py'] + tickers)

# Fetch report data from Cassandra
def get_report_from_cassandra(session, ticker):
    query = "SELECT report_data FROM company_reports WHERE ticker=%s"
    result = session.execute(query, [ticker])
    return json.loads(result.one().report_data)

# Fetch ticker symbols from API only if not cached
def get_ticker_symbols():
    if 'ticker_symbols' not in st.session_state or 'ticker_display' not in st.session_state:
        try:
            response = requests.get("http://127.0.0.1:8000/api/get-companies")
            response.raise_for_status()
            data = response.json()

            # Sort the data based on subsector name
            sorted_data = sorted(data, key=lambda company: company['subsector']['name'])

            # Create two lists: one for display, one for tickers
            ticker_display = [
                f"{company['symbol']} - {company['subsector']['name']}" for company in sorted_data
            ]
            ticker_symbols = [company['symbol'] for company in sorted_data]  # Only ticker

            # Cache both the display and actual ticker list
            st.session_state['ticker_symbols'] = ticker_symbols
            st.session_state['ticker_display'] = ticker_display

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching ticker symbols: {e}")
            st.session_state['ticker_symbols'] = []  # Set empty list if error
            st.session_state['ticker_display'] = []  # Set empty list if error

    
# Create directory if it doesn't exist
if not os.path.exists('extracted_data'):
    os.makedirs('extracted_data')

# Function to download and cache data for the selected ticker and period
def download_or_load_data(ticker, period):
    # Set interval based on period
    interval = '1m' if period == '1d' else '1d'
    
    file_path = f"extracted_data/{ticker.lower()}_{period}_{interval}.csv"
    
    # Check if the CSV already exists
    if os.path.exists(file_path):
        st.write(f"Loading cached data for {ticker} ({period}, {interval})")
        data = pd.read_csv(file_path, parse_dates=True)
        
        # Check for the correct date column and set it as index
        if 'Datetime' in data.columns:
            data.set_index('Datetime', inplace=True)
        elif 'Date' in data.columns:
            data.set_index('Date', inplace=True)
        else:
            st.error(f"Error: No 'Datetime' or 'Date' column found for {ticker}")
            return None
    else:
        st.write(f"Downloading data for {ticker} ({period}, {interval})")
        data = yf.download(ticker, period=period, interval=interval)
        
        # Save the data to CSV
        data.to_csv(file_path)

    return data

# Function to plot candlestick chart using Plotly
def plot_candlestick(data, ticker):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=ticker
    )])
    fig.update_layout(
        title=f'Candlestick Chart for {ticker}',
        yaxis_title='Stock Price (IDR)',
        xaxis_title='Date/Time',
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig)

# Plot valuation comparison
def plot_valuation_comparison(reports):
    valuation_data = {}
    for ticker, report in reports.items():
        valuation_data[ticker] = report['valuation']['forward_pe']
    
    df_val = pd.DataFrame(list(valuation_data.items()), columns=['Ticker', 'Forward PE'])
    st.bar_chart(df_val.set_index('Ticker'))

# Function to display company overview as two tables
def display_company_overview_split(report):
    overview = report['overview']
    
    # Table 1: Company details
    company_details = {
        "Listing Board": overview.get('listing_board', 'N/A'),
        "Industry": overview.get('industry', 'N/A'),
        "Sub-Industry": overview.get('sub_industry', 'N/A'),
        "Sector": overview.get('sector', 'N/A'),
        "Sub-Sector": overview.get('sub_sector', 'N/A'),
        "Market Cap (IDR)": f'{overview.get("market_cap", 0):,}',  # Format large number, use 0 if missing
        "Market Cap Rank": overview.get('market_cap_rank', 'N/A'),
        "Employee Count": overview.get('employee_num', 'N/A'),
        "Listing Date": overview.get('listing_date', 'N/A')
    }
    
    # Table 2: Contact and financial details
    address = overview.get('address', 'Address not available')
    
    contact_details = {
        "Website": overview.get('website', 'N/A'),
        "Phone": overview.get('phone', 'N/A'),
        "Email": overview.get('email', 'N/A'),
        "Last Close Price": overview.get('last_close_price', 'N/A'),
        "Latest Close Date": overview.get('latest_close_date', 'N/A'),
        "Daily Close Change (%)": f'{overview.get("daily_close_change", 0) * 100:.2f}%',  # Default to 0
        "Address": address
    }
    
    return company_details, contact_details

# Function to create tabs for each ticker and display their overview
def display_ticker_tabs(reports):
    ticker_symbols = list(reports.keys())  # List of tickers
    tabs = st.tabs(ticker_symbols)  # Create tabs for each ticker
    
    # Loop over tabs and display corresponding company overview
    for i, ticker in enumerate(ticker_symbols):
        with tabs[i]:
            st.markdown(f"### {reports[ticker]['company_name']} ({ticker})")
            
            # Display the two tables side by side
            company_details, contact_details = display_company_overview_split(reports[ticker])
            
            col1, col2 = st.columns(2)  # Split into two columns
            with col1:
                st.write("**Company Details**")
                st.table(pd.DataFrame(company_details.items(), columns=['Field', 'Value']))
            
            with col2:
                st.write("**Contact & Financial Details**")
                st.table(pd.DataFrame(contact_details.items(), columns=['Field', 'Value']))

# Function to prepare valuation data for Altair
def prepare_historical_data(reports, metric):
    all_data = []
    
    for ticker, report in reports.items():
        # Check if valuation and historical_valuation exist
        if 'valuation' in report and report['valuation'] is not None:
            if 'historical_valuation' in report['valuation'] and report['valuation']['historical_valuation'] is not None:
                historical_data = report['valuation']['historical_valuation']
                for entry in historical_data:
                    # Add data safely for the specified metric
                    all_data.append({
                        'Ticker': ticker,
                        'Year': datetime(entry['year'], 1, 1),
                        metric.upper(): entry.get(metric, None)  # Use .get() to avoid KeyError
                    })
            else:
                st.warning(f"Historical valuation data is not available for {ticker}")
        else:
            st.warning(f"Valuation data is not available for {ticker}")
    
    return pd.DataFrame(all_data)

# Plot valuation comparison
def plot_historical_valuation_comparison_altair(reports, metric):
    df = prepare_historical_data(reports, metric)
    if not df.empty:
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('year(Year):T', title='Year'),
            y=alt.Y(f'{metric.upper()}:Q', title=metric.upper()),
            color='Ticker:N',
            tooltip=['Ticker', 'Year:T', f'{metric.upper()}:Q']
        ).properties(
            title=f'Historical {metric.upper()} Comparison',
            width=700,
            height=400
        ).interactive()
        st.altair_chart(chart)

# Another Altair
# Function to prepare dividend data for Altair
def prepare_dividend_data(reports, metric):
    all_data = []
    
    for ticker, report in reports.items():
        if 'dividend' in report and 'historical_dividends' in report['dividend'] and report['dividend']['historical_dividends'] is not None:
            historical_data = report['dividend']['historical_dividends']
            payout_ratio = report['dividend'].get('payout_ratio')
            
            for entry in historical_data:
                if metric == "payout_ratio":
                    all_data.append({
                        'Ticker': ticker,
                        'Year': datetime(entry['year'], 1, 1),
                        metric: payout_ratio  # Use payout ratio for each year
                    })
                else:
                    all_data.append({
                        'Ticker': ticker,
                        'Year': datetime(entry['year'], 1, 1),
                        metric: entry.get(metric, None)  # Safely get the metric
                    })
        else:
            st.warning(f"Dividend data is not available for {ticker}")
    
    return pd.DataFrame(all_data)

# Plot dividend comparison
def plot_dividend_comparison_altair(reports, metric):
    df = prepare_dividend_data(reports, metric)
    if not df.empty:
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('year(Year):T', title='Year'),
            y=alt.Y(f'{metric}:Q', title=metric.replace("_", " ").title()),
            color='Ticker:N',
            tooltip=['Ticker', 'Year:T', f'{metric}:Q']
        ).properties(
            title=f'{metric.replace("_", " ").title()} Comparison',
            width=700,
            height=400
        ).interactive()
        st.altair_chart(chart)

## Another Altair
# Function to prepare financial data for Altair
def prepare_financial_data(reports, metric):
    all_data = []
    
    for ticker, report in reports.items():
        if 'financials' in report and 'historical_financials' in report['financials']:
            historical_data = report['financials']['historical_financials']
            for entry in historical_data:
                all_data.append({
                    'Ticker': ticker,
                    'Year': datetime(entry['year'], 1, 1),
                    metric: entry.get(metric, None)  # Use get() to avoid KeyError for missing values
                })
        else:
            st.warning(f"Financial data is not available for {ticker}")
    
    return pd.DataFrame(all_data)

# Custom function to format large numbers in Milliar (M) or Triliun (T)
def rupiah_formatter(val):
    if abs(val) >= 1_000_000_000_000:
        return f'{val / 1_000_000_000_000:.1f}T'
    elif abs(val) >= 1_000_000_000:
        return f'{val / 1_000_000_000:.1f}M'
    else:
        return f'{val:,}'  # Show in full if it's less than a billion

# Plot financial comparison
def plot_financial_comparison_altair(reports, metric):
    df = prepare_financial_data(reports, metric)
    if not df.empty:
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('year(Year):T', title='Year'),
            y=alt.Y(f'{metric}:Q', title=metric.replace("_", " ").title(), axis=alt.Axis(format='.2s', labelExpr="datum.value >= 1e12 ? datum.value / 1e12 + 'T' : datum.value >= 1e9 ? datum.value / 1e9 + 'M' : datum.value")),
            color='Ticker:N',
            tooltip=['Ticker', 'Year:T', alt.Tooltip(f'{metric}:Q', format=',.2f', title=metric.replace("_", " ").title())]
        ).properties(
            title=f'{metric.replace("_", " ").title()} Comparison',
            width=700,
            height=400
        ).interactive()
        st.altair_chart(chart)
#### 
def plot_valuation_comparison(reports):
    valuation_data = {}
    for ticker, report in reports.items():
        valuation_data[ticker] = report['valuation']['historical_valuation']
    
    df_val = pd.DataFrame(list(valuation_data.items()), columns=['Ticker', 'Forward PE'])
    st.bar_chart(df_val.set_index('Ticker'))

# Plot financials comparison
def plot_financials_comparison(reports):
    financial_data = {}
    for ticker, report in reports.items():
        financial_data[ticker] = report['financials']['historical_financials'][0]['revenue']
    
    df_fin = pd.DataFrame(list(financial_data.items()), columns=['Ticker', 'Revenue'])
    st.bar_chart(df_fin.set_index('Ticker'))

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Initialize session state
if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

# Toggle between Login and Register form
def show_registration_form():
    st.session_state['show_register'] = True

def show_login_form():
    st.session_state['show_register'] = False

# Sidebar buttons
if st.sidebar.button('Register'):
    show_registration_form()

if st.sidebar.button('Login'):
    show_login_form()

# Conditionally display forms
if st.session_state['show_register']:
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
        if email_of_registered_user:
            st.success('User registered successfully')
            # Ask the user for their password
            password = st.text_input("Enter password", type="password")
            hashed_password = stauth.Hasher([password]).generate()[0]
            
            # Update the YAML config with hashed password
            config['credentials'][username_of_registered_user] = {
                'name': name_of_registered_user,
                'password': hashed_password,  # Store hashed password
                'email': email_of_registered_user
            }
            
            # Save the updated config to YAML
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file)
    except Exception as e:
        st.error(e)
else:
    authenticator.login(location='main')
    if st.session_state['authentication_status']:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        # Streamlit UI setup
        st.title("Favorite Stock Watcher")

        # tickers = st.text_input("Enter up to 3 ticker symbols (comma separated)", "")
        # tickers_list = [ticker.strip().upper() for ticker in tickers.split(',') if ticker]
        # Fetch ticker symbols from the API
        get_ticker_symbols()

        # Use multiselect to choose ticker symbols (display)
        tickers_display_list = st.multiselect(
            "Select up to 3 ticker symbols", st.session_state['ticker_display']
        )

        # Extract the original ticker symbols from the selected display list
        selected_tickers = [
            st.session_state['ticker_symbols'][st.session_state['ticker_display'].index(ticker_display)]
            for ticker_display in tickers_display_list
        ]

        if st.button("Compare"):
            if len(selected_tickers) > 3:
                st.error("You can compare a maximum of 3 tickers.")
            else:
                session = connect_to_cassandra()
                reports = {}

                missing_tickers = []
                for ticker in selected_tickers:
                    if check_ticker_in_cassandra(session, ticker):
                        st.write(f"Data for {ticker} already exists in Cassandra.")
                        reports[ticker] = get_report_from_cassandra(session, ticker)
                    else:
                        missing_tickers.append(ticker)

                if missing_tickers:
                    st.write(f"Fetching data for {', '.join(missing_tickers)} using Kafka and Spark.")
                    trigger_kafka_spark_pipeline(missing_tickers)
                    st.write("Please wait for the data to be processed...")

                    # Wait until all missing tickers are available in Cassandra
                    while missing_tickers:
                        time.sleep(8)  # Wait for 5 seconds before rechecking
                        for ticker in missing_tickers[:]:  # Iterate over a copy
                            if check_ticker_in_cassandra(session, ticker):
                                st.write(f"Data for {ticker} is now available in Cassandra.")
                                reports[ticker] = get_report_from_cassandra(session, ticker)
                                missing_tickers.remove(ticker)

                # Visualize the comparison
                if reports:
                    # st.write("## Price Movement Comparison")
                    # plot_price_movement(reports)
                    st.write("## Price Movement")
                    # Tabs for selecting period and downloading data
                    tab1, tab2, tab3, tab4 = st.tabs(["1d", "5d", "1mo", "3mo"])
                    
                    # Preload data for all selected periods
                    period_data = {}
                    for ticker in selected_tickers:
                        period_data[ticker] = {}
                        for period in ['1d', '5d', '1mo', '3mo']:
                            period_data[ticker][period] = download_or_load_data(ticker, period)

                    with tab1:
                        st.write("Comparing data for period: 1 day (1-minute interval)")
                        for ticker in selected_tickers:
                            data = period_data[ticker]['1d']
                            if not data.empty:
                                plot_candlestick(data, ticker)
                            else:
                                st.warning(f"No data available for {ticker} (1 day)")

                    with tab2:
                        st.write("Comparing data for period: 5 days (1-day interval)")
                        for ticker in selected_tickers:
                            data = period_data[ticker]['5d']
                            if not data.empty:
                                plot_candlestick(data, ticker)
                            else:
                                st.warning(f"No data available for {ticker} (5 days)")

                    with tab3:
                        st.write("Comparing data for period: 1 month (1-day interval)")
                        for ticker in selected_tickers:
                            data = period_data[ticker]['1mo']
                            if not data.empty:
                                plot_candlestick(data, ticker)
                            else:
                                st.warning(f"No data available for {ticker} (1 month)")

                    with tab4:
                        st.write("Comparing data for period: 3 months (1-day interval)")
                        for ticker in selected_tickers:
                            data = period_data[ticker]['3mo']
                            if not data.empty:
                                plot_candlestick(data, ticker)
                            else:
                                st.warning(f"No data available for {ticker} (3 months)")

                    st.write("## Company Overview")
                    display_ticker_tabs(reports)

                    st.write("## Valuation Comparison")
                    # plot_valuation_comparison(reports)
                    # Streamlit tabs for selecting valuation metric
                    tab1, tab2, tab3 = st.tabs(["PB", "PE", "PS"])

                    with tab1:
                        st.write("Comparing PB across tickers")
                        plot_historical_valuation_comparison_altair(reports, 'pb')

                    with tab2:
                        st.write("Comparing PE across tickers")
                        plot_historical_valuation_comparison_altair(reports, 'pe')

                    with tab3:
                        st.write("Comparing PS across tickers")
                        plot_historical_valuation_comparison_altair(reports, 'ps')

                    # Another Altair
                    # Streamlit tabs for selecting the dividend metric
                    st.write("## Dividend Comparison")
                    tab1, tab2, tab3 = st.tabs(["Total Yield", "Total Dividend", "Payout Ratio"])

                    with tab1:
                        st.write("Comparing Total Yield across tickers")
                        plot_dividend_comparison_altair(reports, 'total_yield')

                    with tab2:
                        st.write("Comparing Total Dividend across tickers")
                        plot_dividend_comparison_altair(reports, 'total_dividend')

                    with tab3:
                        st.write("Comparing Payout Ratio across tickers")
                        plot_dividend_comparison_altair(reports, 'payout_ratio')

                    # Another Altair
                    # Streamlit tabs for selecting the financial metric
                    st.write("## Financials Comparison")
                    # Streamlit tabs for selecting financial metrics
                    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Revenue", "Earnings", "Total Debt", "Total Assets", "Total Equity", "Operating PNL", "Total Liabilities"])

                    with tab1:
                        st.write("Comparing Revenue across tickers")
                        plot_financial_comparison_altair(reports, 'revenue')

                    with tab2:
                        st.write("Comparing Earnings across tickers")
                        plot_financial_comparison_altair(reports, 'earnings')

                    with tab3:
                        st.write("Comparing Total Debt across tickers")
                        plot_financial_comparison_altair(reports, 'total_debt')

                    with tab4:
                        st.write("Comparing Total Assets across tickers")
                        plot_financial_comparison_altair(reports, 'total_assets')

                    with tab5:
                        st.write("Comparing Total Equity across tickers")
                        plot_financial_comparison_altair(reports, 'total_equity')

                    with tab6:
                        st.write("Comparing Operating PNL across tickers")
                        plot_financial_comparison_altair(reports, 'operating_pnl')

                    with tab7:
                        st.write("Comparing Total Liabilities across tickers")
                        plot_financial_comparison_altair(reports, 'total_liabilities')
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')


# if st.session_state['authentication_status']:
#     # Streamlit UI setup
#     # Logout button
#     authenticator.logout(location="sidebar")
#     st.title("Favorite Stock Watcher")

#     tickers = st.text_input("Enter up to 3 ticker symbols (comma separated)", "")
#     tickers_list = [ticker.strip().upper() for ticker in tickers.split(',') if ticker]

#     if st.button("Compare"):
#         if len(tickers_list) > 3:
#             st.error("You can compare a maximum of 3 tickers.")
#         else:
#             session = connect_to_cassandra()
#             reports = {}

#             missing_tickers = []
#             for ticker in tickers_list:
#                 if check_ticker_in_cassandra(session, ticker):
#                     st.write(f"Data for {ticker} already exists in Cassandra.")
#                     reports[ticker] = get_report_from_cassandra(session, ticker)
#                 else:
#                     missing_tickers.append(ticker)

#             if missing_tickers:
#                 st.write(f"Fetching data for {', '.join(missing_tickers)} using Kafka and Spark.")
#                 trigger_kafka_spark_pipeline(missing_tickers)
#                 st.write("Please wait for the data to be processed...")

#                 # Wait until all missing tickers are available in Cassandra
#                 while missing_tickers:
#                     time.sleep(5)  # Wait for 5 seconds before rechecking
#                     for ticker in missing_tickers[:]:  # Iterate over a copy
#                         if check_ticker_in_cassandra(session, ticker):
#                             st.write(f"Data for {ticker} is now available in Cassandra.")
#                             reports[ticker] = get_report_from_cassandra(session, ticker)
#                             missing_tickers.remove(ticker)

#             # Visualize the comparison
#             if reports:
#                 st.write("## Price Movement Comparison")
#                 plot_price_movement(reports)

#                 st.write("## Valuation Comparison")
#                 plot_valuation_comparison(reports)

#                 st.write("## Financials Comparison")
#                 plot_financials_comparison(reports)

# elif st.session_state['authentication_status'] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state['authentication_status'] is None:
#     st.warning('Please enter your username and password')


# Reset password feature
if st.sidebar.button('Reset Password'):
    if st.session_state['authentication_status']:
        try:
            if authenticator.reset_password(st.session_state['username']):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)
