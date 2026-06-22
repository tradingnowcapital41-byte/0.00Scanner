import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# तुमच्या स्टॉक्सची यादी
stocks = ["GLENMARK.NS", "PAYTM.NS", "PRESTIGE.NS", "IREDA.NS", "CONCOR.NS", "WAAREEENER.NS", "MOTILALOFS.NS", "NATIONALUM.NS", "NYKAA.NS", "POLYCAB.NS", "IDEA.NS", "HDFCAMC.NS", "NMDC.NS", "KALYANKJIL.NS", "MFSL.NS", "NTPCGREEN.NS", "MANKIND.NS", "SAIL.NS", "TATATECH.NS", "DIXON.NS", "OBEROIRLTY.NS", "BHARTIHEXA.NS", "ACC.NS", "HUDCO.NS", "APLAPOLLO.NS", "AUBANK.NS", "JUBLFOOD.NS", "MAXHEALTH.NS", "PATANJALI.NS", "TIINDIA.NS", "MPHASIS.NS", "LICHSGFIN.NS", "ATGL.NS", "EXIDEIND.NS", "TORNTPOWER.NS", "SBICARD.NS", "GODREJPROP.NS", "ASTRAL.NS", "SUZLON.NS", "PETRONET.NS", "BANDHANBNK.NS", "MUTHOOTFIN.NS", "RVNL.NS", "CUMMINSIND.NS", "VOLTAS.NS", "SONACOMS.NS", "IRCTC.NS", "BHEL.NS", "TATAELXSI.NS", "KPITTECH.NS", "IRB.NS", "BIOCON.NS", "UNIONBANK.NS", "APOLLOTYRE.NS", "YESBANK.NS", "ASHOKLEY.NS", "MARICO.NS", "TATACOMM.NS", "HINDZINC.NS", "IGL.NS", "PHOENIXLTD.NS", "UPL.NS", "ABCAPITAL.NS", "INDUSTOWER.NS", "SRF.NS", "GMRAIRPORT.NS", "SJVN.NS", "SUPREMEIND.NS", "PERSISTENT.NS", "COCHINSHIP.NS", "OLAELEC.NS", "NHPC.NS", "MAHABANK.NS", "PAGEIND.NS", "LUPIN.NS", "LTF.NS", "MAZDOCK.NS", "AUROPHARMA.NS", "IDFCFIRSTB.NS", "M&MFIN.NS", "HINDPETRO.NS", "POLICYBZR.NS", "COLPAL.NS", "FEDERALBNK.NS", "BANKINDIA.NS", "ESCORTS.NS", "ABFRL.NS", "INDIANB.NS", "ALKEM.NS", "MRF.NS", "OFSS.NS", "OIL.NS", "BSE.NS", "COFORGE.NS", "BHARATFORG.NS", "PIIND.NS", "SOLARINDS.NS", "BDL.NS"]

st.set_page_config(page_title="Live Open=Low Scanner", layout="wide")
st.title("📈 Live Equity Open=Low/High Scanner")

if 'history' not in st.session_state:
    st.session_state.history = []

def scan_stocks():
    results = []
    for symbol in stocks:
        try:
            df = yf.download(symbol, period="1d", interval="5m")
            if df.empty: continue
            
            first_candle = df.iloc[0]
            open_p, high_p, low_p, close_p = first_candle['Open'], first_candle['High'], first_candle['Low'], first_candle['Close']
            
            # Open = Low (Bullish)
            if open_p <= low_p * 1.001 and abs(close_p - open_p) <= (open_p * 0.01):
                target1 = open_p + (high_p - low_p)
                target2 = open_p + (high_p - low_p) * 1.5
                results.append({'Stock': symbol, 'Signal': 'BUY', 'Price': close_p, 'SL': low_p, 'T1': target1, 'T2': target2})
            
            # Open = High (Bearish)
            elif open_p >= high_p * 0.999:
                target1 = open_p - (high_p - low_p)
                target2 = open_p - (high_p - low_p) * 1.5
                results.append({'Stock': symbol, 'Signal': 'SELL', 'Price': close_p, 'SL': high_p, 'T1': target1, 'T2': target2})
                
        except: continue
    return results

if st.button("🚀 Scan Live Market"):
    signals = scan_stocks()
    for s in signals:
        st.session_state.history.append(s)
        st.toast(f"Alert: {s['Stock']} {s['Signal']} at {s['Price']:.2f}")

st.subheader("आजचे सिग्नल (History)")
if st.session_state.history:
    st.table(pd.DataFrame(st.session_state.history))
else:
    st.write("सध्या कोणतेही सिग्नल नाहीत.")
