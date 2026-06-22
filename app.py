import streamlit as st
import yfinance as yf
import pandas as pd
import time

# स्टॉक्सची यादी
stocks = ["GLENMARK.NS", "PAYTM.NS", "IREDA.NS", "CONCOR.NS", "TATATECH.NS", "DIXON.NS", "SUZLON.NS", "RVNL.NS", "BHEL.NS"] # तुम्ही पूर्ण लिस्ट टाका

st.set_page_config(page_title="Pharma2Tech Live Scanner", layout="wide")
st.title("🚀 Live Strategy Scanner")

# Session State Initialize
if 'signals' not in st.session_state:
    st.session_state.signals = pd.DataFrame(columns=['Stock', 'Type', 'Entry', 'SL', 'T1', 'T2', 'Status', 'Current'])

def get_live_price(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m")
    return data['Close'].iloc[-1] if not data.empty else 0

def scan():
    new_signals = []
    for symbol in stocks:
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        if df.empty: continue
        
        c1 = df.iloc[0]
        # Logic: Open=Low (Buy) / Open=High (Sell)
        if c1['Open'] <= c1['Low'] * 1.001: # Buy Signal
            signal = {'Stock': symbol, 'Type': 'BUY', 'Entry': c1['High'], 'SL': c1['Low'], 
                      'T1': c1['High'] + (c1['High']-c1['Low']), 'T2': c1['High'] + (c1['High']-c1['Low'])*1.5, 'Status': 'Active'}
            new_signals.append(signal)
            
    return pd.DataFrame(new_signals)

# UI
if st.button("🔄 Refresh Market Data"):
    scanned_df = scan()
    st.session_state.signals = scanned_df

# Table Update Logic
if not st.session_state.signals.empty:
    df = st.session_state.signals
    for i, row in df.iterrows():
        curr = get_live_price(row['Stock'])
        df.at[i, 'Current'] = curr
        
        # Check SL/Target
        if row['Type'] == 'BUY':
            if curr <= row['SL']: df.at[i, 'Status'] = '🔴 SL HIT'
            elif curr >= row['T1']: df.at[i, 'Status'] = '🟢 T1 HIT'
            if curr >= row['T2']: df.at[i, 'Status'] = '🎯 T2 HIT'
    
    st.table(df)
    
    # Notifications (Toast)
    active_alerts = df[df['Status'].str.contains('HIT')]
    for _, alert in active_alerts.iterrows():
        st.toast(f"Alert: {alert['Stock']} -> {alert['Status']} (Price: {alert['Current']})")
else:
    st.info("डेटा लोड करण्यासाठी Refresh दाबा.")
