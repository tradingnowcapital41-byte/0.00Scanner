import streamlit as st
import yfinance as yf
import pandas as pd

# स्टॉक्सची यादी
stocks = ["GLENMARK.NS", "PAYTM.NS", "IREDA.NS", "CONCOR.NS", "TATATECH.NS", "DIXON.NS", "SUZLON.NS", "RVNL.NS"]

st.set_page_config(page_title="Live Scanner", layout="wide")
st.title("🚀 Live Strategy Scanner")

# रिफ्रेश बटण
if st.button("🔄 Refresh Data"):
    st.rerun()

def get_data():
    all_data = []
    for symbol in stocks:
        try:
            df = yf.download(symbol, period="1d", interval="5m", progress=False)
            if df.empty: continue
            
            c1 = df.iloc[0]
            curr = df['Close'].iloc[-1]
            
            # लॉजिक: Open=Low (Buy)
            if c1['Open'] <= c1['Low'] * 1.001:
                t1 = c1['High'] + (c1['High'] - c1['Low'])
                t2 = c1['High'] + (c1['High'] - c1['Low']) * 1.5
                status = 'Active'
                if curr <= c1['Low']: status = '🔴 SL HIT'
                elif curr >= t2: status = '🎯 T2 HIT'
                elif curr >= t1: status = '🟢 T1 HIT'
                
                all_data.append({'Stock': symbol, 'Type': 'BUY', 'Entry': round(c1['High'],2), 'SL': round(c1['Low'],2), 'Target1': round(t1,2), 'Target2': round(t2,2), 'Current': round(curr,2), 'Status': status})
        except: continue
    return pd.DataFrame(all_data)

df = get_data()
if not df.empty:
    st.table(df)
else:
    st.write("डेटा लोड होत आहे किंवा मार्केट बंद आहे...")
