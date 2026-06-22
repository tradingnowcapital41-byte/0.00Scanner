import streamlit as st
import yfinance as yf
import pandas as pd
import time

# १. सर्व स्टॉक्सची लिस्ट (NTPCGREEN आणि इतर सर्व समाविष्ट)
all_stocks = [
    "GLENMARK.NS", "PAYTM.NS", "PREMIERENE.NS", "PRESTIGE.NS", "IREDA.NS", "CONCOR.NS", 
    "WAAREEENER.NS", "MOTILALOFS.NS", "NATIONALUM.NS", "NYKAA.NS", "POLYCAB.NS", "IDEA.NS", 
    "HDFCAMC.NS", "NMDC.NS", "KALYANKJIL.NS", "MFSL.NS", "NTPCGREEN.NS", "MANKIND.NS", 
    "SAIL.NS", "TATATECH.NS", "DIXON.NS", "OBEROIRLTY.NS", "BHARTIHEXA.NS", "ACC.NS", 
    "HUDCO.NS", "APLAPOLLO.NS", "AUBANK.NS", "JUBLFOOD.NS", "MAXHEALTH.NS", "PATANJALI.NS", 
    "TIINDIA.NS", "MPHASIS.NS", "LICHSGFIN.NS", "ATGL.NS", "EXIDEIND.NS", "TORNTPOWER.NS", 
    "SBICARD.NS", "GODREJPROP.NS", "ASTRAL.NS", "SUZLON.NS", "PETRONET.NS", "BANDHANBNK.NS", 
    "MUTHOOTFIN.NS", "RVNL.NS", "CUMMINSIND.NS", "VOLTAS.NS", "SONACOMS.NS", "IRCTC.NS", 
    "BHEL.NS", "TATAELXSI.NS", "KPITTECH.NS", "IRB.NS", "BIOCON.NS", "UNIONBANK.NS", 
    "APOLLOTYRE.NS", "YESBANK.NS", "ASHOKLEY.NS", "MARICO.NS", "TATACOMM.NS", "HINDZINC.NS", 
    "IGL.NS", "PHOENIXLTD.NS", "UPL.NS", "ABCAPITAL.NS", "INDUSTOWER.NS", "SRF.NS", 
    "GMRAIRPORT.NS", "SJVN.NS", "SUPREMEIND.NS", "PERSISTENT.NS", "COCHINSHIP.NS", "OLAELEC.NS", 
    "NHPC.NS", "MAHABANK.NS", "PAGEIND.NS", "LUPIN.NS", "LTF.NS", "MAZDOCK.NS", "AUROPHARMA.NS", 
    "IDFCFIRSTB.NS", "M&MFIN.NS", "HINDPETRO.NS", "POLICYBZR.NS", "COLPAL.NS", "FEDERALBNK.NS", 
    "BANKINDIA.NS", "ESCORTS.NS", "ABFRL.NS", "INDIANB.NS", "ALKEM.NS", "MRF.NS", "OFSS.NS", 
    "OIL.NS", "BSE.NS", "COFORGE.NS", "BHARATFORG.NS", "PIIND.NS", "SOLARINDS.NS", "BDL.NS"
]

# २. पेज सेटअप
st.set_page_config(page_title="Auto Open=Low/High Scanner", layout="wide")
st.title("📈 5-Min Open=Low/High Auto-Scanner")
st.caption("हा स्कॅनर दर ६० सेकंदांनी ऑटोमॅटिक रेंडर होतो आणि टारगेट/SL ट्रॅक करतो.")

# ३. ऑटो रिफ्रेश सेटिंग (दर ६० सेकंदांनी पेज रिफ्रेश होईल - क्रॅश न होता)
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1

# ४. मुख्य स्कॅनिंग फंक्शन
def scan_markets():
    signals = []
    
    for symbol in all_stocks:
        try:
            # ५ मिनिटांचा आजचा डेटा फेटच करणे
            df = yf.download(symbol, period="1d", interval="5m", progress=False)
            if df.empty or len(df) < 1:
                continue
                
            c1 = df.iloc[0] # पहिली ५ मिनिटांची कॅन्डल
            curr_price = df['Close'].iloc[-1] # सध्याची लाईव्ह किंमत
            
            c1_open = float(c1['Open'])
            c1_high = float(c1['High'])
            c1_low = float(c1['Low'])
            c1_close = float(c1['Close'])
            
            # कॅन्डलची रेंज १% पेक्षा कमी असावी ही अट
            candle_range_pct = ((c1_high - c1_low) / c1_open) * 100
            
            if candle_range_pct <= 1.0:
                # --- OPEN = LOW (BUY STRATEGY) ---
                if c1_open == c1_low:
                    entry = c1_high
                    sl = c1_low
                    risk = entry - sl
                    t1 = entry + risk
                    t2 = entry + (risk * 1.5)
                    
                    status = "🎯 Pending (High break ची वाट पाहत आहे)"
                    # जर सध्याची किंमत हायच्या वर गेली असेल तर एंट्री ट्रिगर झाली
                    if curr_price >= entry:
                        status = "🟢 Active Trade"
                        if curr_price <= sl:
                            status = "🔴 SL HIT"
                        elif curr_price >= t2:
                            status = "🎯 TARGET 2 HIT"
                        elif curr_price >= t1:
                            status = "✅ TARGET 1 HIT"
                            
                    signals.append({
                        "Stock": symbol.replace(".NS", ""),
                        "Type": "⚡ BUY (O=L)",
                        "Entry Price": round(entry, 2),
                        "StopLoss": round(sl, 2),
                        "Target 1 (1:1)": round(t1, 2),
                        "Target 2 (1:1.5)": round(t2, 2),
                        "Current Price": round(curr_price, 2),
                        "Status": status
                    })
                
                # --- OPEN = HIGH (SELL STRATEGY) ---
                elif c1_open == c1_high:
                    entry = c1_low
                    sl = c1_high
                    risk = sl - entry
                    t1 = entry - risk
                    t2 = entry - (risk * 1.5)
                    
                    status = "🎯 Pending (Low break ची वाट पाहत आहे)"
                    if curr_price <= entry:
                        status = "🟢 Active Trade"
                        if curr_price >= sl:
                            status = "🔴 SL HIT"
                        elif curr_price <= t2:
                            status = "🎯 TARGET 2 HIT"
                        elif curr_price <= t1:
                            status = "✅ TARGET 1 HIT"
                            
                    signals.append({
                        "Stock": symbol.replace(".NS", ""),
                        "Type": "💥 SELL (O=H)",
                        "Entry Price": round(entry, 2),
                        "StopLoss": round(sl, 2),
                        "Target 1 (1:1)": round(t1, 2),
                        "Target 2 (1:1.5)": round(t2, 2),
                        "Current Price": round(curr_price, 2),
                        "Status": status
                    })
        except Exception as e:
            continue
            
    return pd.DataFrame(signals)

# ५. डेटा रेंडरिंग
with st.spinner("लाईव्ह मार्केट डेटा स्कॅन होत आहे... कृपया थांबा..."):
    df_results = scan_markets()

# ६. डिस्प्ले आणि पॉप-अप अलर्ट्स
if not df_results.empty:
    # पॉप-अप अलर्ट्स (Toast Notifications) साठी लूप
    for _, row in df_results.iterrows():
        if "HIT" in row["Status"]:
            st.toast(f"⚠️ {row['Stock']} चा {row['Status']} झालाय! Price: {row['Current Price']}", icon="📢")
        elif "Active" in row["Status"]:
            st.toast(f"🚀 Entry Triggered: {row['Stock']} ({row['Type']}) at {row['Entry Price']}", icon="🔥")

    # मुख्य डॅशबोर्ड टेबल
    st.subheader(f"📊 आजचे सिग्नल्स आणि हिस्टरी (एकूण सापडलेले: {len(df_results)})")
    
    # स्टेटस नुसार रंगांचे कस्टमायझेशन सोपे जावे म्हणून टेबल दाखवणे
    st.dataframe(df_results, use_container_width=True, hide_index=True)
else:
    st.info("सध्याच्या ५ मिनिटांच्या पहिल्या कॅन्डलमध्ये कोणतीही Open=Low किंवा Open=High ची स्थिती (१% च्या आत) सापडलेली नाही.")

# ७. ऑटो-रिफ्रेश करण्यासाठी बॅकएंड टाईमर ट्रिक (क्रॅश प्रूफ)
time.sleep(60)
st.rerun()
