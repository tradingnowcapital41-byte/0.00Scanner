import streamlit as st
import yfinance as yf
import pandas as pd
import time

# स्टॉक्सची यादी (तुमच्या गरजेनुसार)
stocks = ["GLENMARK.NS", "PAYTM.NS", "IREDA.NS", "CONCOR.NS", "TATATECH.NS", "DIXON.NS", "SUZLON.NS", "RVNL.NS"]

st.set_page_config(page_title="Pharma2Tech Live Scanner", layout="wide")
st.title("🚀 Live Strategy Scanner - Auto Refresh")

if 'signals' not in st.session_state:
    st.session_state.signals = pd.DataFrame()

def run_scanner():
    data_list = []
    for symbol in stocks:
        try:
            df = yf.download(symbol, period="1d", interval="5m", progress=False)
            if df.empty: continue
            
            c1 = df.iloc[0] # पहिली ५ मिनिटांची कॅन्डल
            curr = df['Close'].iloc[-1] # आताची किंमत
            
            # लॉजिक: Open=Low (Buy)
            if c1['Open'] <= c1['Low'] * 1.001:
                t1 = c1['High'] + (c1['High'] - c1['Low'])
                t2 = c1['High'] + (c1['High'] - c1['Low']) * 1.5
                status = 'Active'
                if curr <= c1['Low']: status = '🔴 SL HIT'
                elif curr >= t2: status = '🎯 T2 HIT'
                elif curr >= t1: status = '🟢 T1 HIT'
                
                data_list.append({'Stock': symbol, 'Type': 'BUY', 'Entry': round(c1['High'],2), 'SL': round(c1['Low'],2), 'Target1': round(t1,2), 'Target2': round(t2,2), 'Current': round(curr,2), 'Status': status})
        except: continue
    return pd.DataFrame(data_list)

# Auto-Refresh Logic
placeholder = st.empty()

while True:
    with placeholder.container():
        df_results = run_scanner()
        if not df_results.empty:
            st.table(df_results)
            # Alert for Hits
            hits = df_results[df_results['Status'] != 'Active']
            for _, row in hits.iterrows():
                st.toast(f"{row['Stock']} : {row['Status']} @ {row['Current']}")
        else:
            st.write("सध्या सिग्नल स्कॅन होत आहेत...")
            
    time.sleep(30) # दर ३० सेकंदाला अपडेट
    st.rerun()
