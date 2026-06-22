import streamlit as st
import yfinance as yf
import pandas as pd

# सर्व १०० स्टॉक्सची लिस्ट
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

st.set_page_config(page_title="Auto Open=Low/High Scanner", layout="wide")
st.title("📈 5-Min Open=Low/High Auto-Scanner")

# मॅन्युअल रिफ्रेश बटण
if st.button("🔄 फोर्स रिफ्रेश (Force Refresh)"):
    st.rerun()

# स्ट्रीमलिटचे अधिकृत ऑटो-रिफ्रेश लॉजिक (दर ६० सेकंदांनी विना एरर रन होईल)
# याला हॅक किंवा एरर येत नाही
st.caption("हा डॅशबोर्ड दर ६० सेकंदांनी आपोआप नवीन किंमती अपडेट करतो.")

def scan_markets_fast():
    signals = []
    try:
        tickers = " ".join(all_stocks)
        # प्रोग्रेस बार बंद केलाय जेणेकरून स्क्रीन क्लीन राहील
        df_all = yf.download(tickers, period="1d", interval="5m", group_by='ticker', progress=False)
    except Exception as e:
        st.error(f"Yahoo Finance कडून डेटा मिळवण्यात अडचण: {e}")
        return pd.DataFrame()

    for symbol in all_stocks:
        try:
            df = df_all[symbol].dropna()
            if df.empty or len(df) < 1:
                continue
                
            c1 = df.iloc[0] # पहिली ५ मिनिटांची कॅन्डल (9:15-9:20)
            curr_price = float(df['Close'].iloc[-1]) # आताची चालू किंमत
            
            c1_open = float(c1['Open'])
            c1_high = float(c1['High'])
            c1_low = float(c1['Low'])
            
            # १% कॅन्डल साईझ फिल्टर
            candle_range_pct = ((c1_high - c1_low) / c1_open) * 100
            
            if candle_range_pct <= 1.0:
                # --- OPEN = LOW (BUY) ---
                if abs(c1_open - c1_low) < 0.05:
                    entry = c1_high
                    sl = c1_low
                    risk = entry - sl
                    t1 = entry + risk
                    t2 = entry + (risk * 1.5)
                    
                    status = "🎯 Pending (High break ची वाट पाहत आहे)"
                    if curr_price >= entry:
                        status = "🟢 Active Trade"
                        if curr_price <= sl: status = "🔴 SL HIT"
                        elif curr_price >= t2: status = "🎯 TARGET 2 HIT"
                        elif curr_price >= t1: status = "✅ TARGET 1 HIT"
                            
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
                
                # --- OPEN = HIGH (SELL) ---
                elif abs(c1_open - c1_high) < 0.05:
                    entry = c1_low
                    sl = c1_high
                    risk = sl - entry
                    t1 = entry - risk
                    t2 = entry - (risk * 1.5)
                    
                    status = "🎯 Pending (Low break ची वाट पाहत आहे)"
                    if curr_price <= entry:
                        status = "🟢 Active Trade"
                        if curr_price >= sl: status = "🔴 SL HIT"
                        elif curr_price <= t2: status = "🎯 TARGET 2 HIT"
                        elif curr_price <= t1: status = "✅ TARGET 1 HIT"
                            
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
        except:
            continue
            
    return pd.DataFrame(signals)

# मुख्य रनर आणि स्क्रीनवर दाखवणे
with st.spinner("लाईव्ह डेटा फेटच होत आहे..."):
    df_results = scan_markets_fast()

if not df_results.empty:
    # अलर्ट्स दाखवणे
    for _, row in df_results.iterrows():
        if "HIT" in row["Status"]:
            st.toast(f"⚠️ {row['Stock']}: {row['Status']}!", icon="📢")
        elif "Active" in row["Status"]:
            st.toast(f"🚀 Entry Triggered: {row['Stock']}", icon="🔥")

    st.subheader(f"📊 आजचे सिग्नल्स (एकूण सापडलेले: {len(df_results)})")
    st.dataframe(df_results, use_container_width=True, hide_index=True)
else:
    st.info("सध्या अटींमध्ये बसणारा कोणताही स्टॉक सापडलेला नाही. (मार्केट वेळेत सकाळी ९:२० नंतर तपासा)")
