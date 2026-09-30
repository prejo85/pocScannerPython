import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as grp
from plotly.subplots import make_subplots
import requests
import json

st.set_page_config(layout="wide", page_title="VolNodes Pro", page_icon="📐")

st.markdown("""
<style>
    @import url('https://googleapis.com');
    .stApp { background: radial-gradient(circle at top right, #1a1f36 0%, #0d0f18 100%); font-family: 'Plus Jakarta Sans', sans-serif; color: #f8fafc; }
    h1 { font-weight: 800; background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding-bottom: 15px; }
    div[data-testid="stMetric"] { background: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(56, 189, 248, 0.15) !important; border-radius: 14px !important; padding: 20px !important; }
    div.stButton > button:first-child { background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important; color: #ffffff !important; font-weight: 600 !important; border: none !important; border-radius: 10px !important; padding: 0.7rem 2.2rem !important; }
    button[data-baseweb="tab"] { font-size: 15px !important; font-weight: 600 !important; color: #64748b !important; padding: 12px 24px !important; }
    button[aria-selected="true"] { color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }
    div[data-baseweb="select"], input, textarea { background-color: #0f172a !important; border-color: #334155 !important; color: #f8fafc !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

st.title("📐 Analisi Pro — Dashboard Multitasking")

if "asset_type_index" not in st.session_state:
    st.session_state.asset_type_index = 0
T_ID = "2072895073"
TESTA_INTERNET = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

SP500_FULL = "MMM,AOS,ABT,ABBV,ACN,ADBE,AMD,AES,AFL,A,APD,ABNB,AKAM,ALB,ARE,ALGN,ALLE,AAPL,AMAT,APP,ACGL,ADM,NVDA,TSLA,V,WMT,DIS"
NASDAQ_FULL = "MDLZ,ADI,ADP,ADSK,AAL,ALGN,AMAT,AMD,AMGN,AMZN,ANSS,ASML,TEAM,ADBE,BIIB,BKNG,AVGO,CDNS,CSCO,COST,NFLX,NVDA,TSLA,MSFT"
FTSEMIB_FULL = "A2A.MI,AMP.MI,AZM.MI,BAMI.MI,BCA.MI,BMED.MI,BPER.MI,CPR.MI,DIA.MI,ENI.MI,ERG.MI,G.MI,ISP.MI,LDO.MI,RACE.MI,UCG.MI"
CRYPTO_FULL = "BTC-USD,ETH-USD,SOL-USD,BNB-USD,XRP-USD,ADA-USD,DOGE-USD,AVAX-USD,DOT-USD,LINK-USD,MATIC-USD,LTC-USD"

def ottieni_paniere(nome_paniere):
    if nome_paniere == "S&P 500": return SP500_FULL
    elif nome_paniere == "NASDAQ 100": return NASDAQ_FULL
    elif nome_paniere == "FTSE MIB (FIB)": return FTSEMIB_FULL
    elif nome_paniere == "Crypto": return CRYPTO_FULL
    return "AAPL,MSFT"

def calc_vp(df, div=200):
    if df.empty: return None, None, None, [], []
    p_min, p_max = float(df['Low'].min()), float(df['High'].max())
    if p_max - p_min <= 0: return p_min, p_min, p_min, [], []
    bins = np.linspace(p_min, p_max, div + 1)
    vols = np.zeros(div)
    highs, lows, volumes = df['High'].values, df['Low'].values, df['Volume'].values
    for h, l, v in zip(highs, lows, volumes):
        if v <= 0 or h == l: continue
        mask = (bins[1:] >= l) & (bins[:-1] <= h)
        vols[mask] += v / max(1, np.sum(mask))
    prices = [float((bins[i] + bins[i+1]) / 2) for i in range(div)]
    vols_list = vols.tolist()
    poc_idx = vols_list.index(max(vols_list))
    poc = prices[poc_idx]
    v_total, v_target = sum(vols_list), sum(vols_list) * 0.70
    v_current, idx_b, idx_a = vols_list[poc_idx], poc_idx, poc_idx
    while v_current < v_target:
        v_s = vols_list[idx_b - 1] if idx_b > 0 else 0
        v_p = vols_list[idx_a + 1] if idx_a < div - 1 else 0
        if v_s == 0 and v_p == 0: break
        if v_s >= v_p: idx_b -= 1; v_current += v_s
        else: idx_a += 1; v_current += v_p
    return poc, prices[min(div - 1, idx_a)], prices[max(0, idx_b)], prices, vols_list

tab1, tab2, tab3 = st.tabs(["Analisi Triple-POC", "Backtesting", "Alert Telegram"])
with tab1:
    st.subheader("📊 Analisi Grafica Avanzata Volume Profile & Indicatori")
    st.markdown("##### ⚙️ Personalizzazione Livelli Grafici")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1: mostra_poc = st.checkbox("Mostra Linea POC Entry (Rosso)", value=True, key="chk_poc")
    with t_col2: mostra_va = st.checkbox("Mostra Value Area & Istogrammi", value=True, key="chk_va")
    with t_col3: mostra_rr = st.checkbox("Mostra Zone Target / Stop Loss (R/R)", value=True, key="chk_rr")
    with t_col4: mostra_bb = st.checkbox("Mostra Bande di Bollinger", value=True, key="chk_bb")
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        paniere_selezionato = st.selectbox("Seleziona Indice:", ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)", "Crypto"], key="an_paniere")
        ticker_caricati = ottieni_paniere(paniere_selezionato)
        st.session_state.asset_type_index = 1 if paniere_selezionato == "Crypto" else 0
    with col2: asset_type = st.selectbox("Tipo Asset:", ["Azione", "Criptovaluta"], index=st.session_state.asset_type_index, key="an_type")
    with col3:
        period_label = st.selectbox("Estensione Profilo Recente:", ["3 Mesi", "6 Mesi", "9 Mesi"], key="an_period")
        g3 = {"3 Mesi": 90, "6 Mesi": 180, "9 Mesi": 270}[period_label]
    with col4:
        tf_label = st.selectbox("Timeframe Candele:", ["Giornaliero (Daily)", "Settimanale (Weekly)"], key="an_timeframe")
        tf_attivo = {"Giornaliero (Daily)": "1d", "Settimanale (Weekly)": "1wk"}[tf_label]

    tickers_input = st.text_area("Modifica i Tickers:", value=ticker_caricati, height=120, key=f"an_area_{paniere_selezionato}")
    if st.button("🔍 Avvia Analisi Grafica Nodes", type="primary"):
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        if not tickers: st.warning("Inserisci almeno un ticker valido.")
        else:
            st.success("Generazione fogli ticker...")
            fogli_ticker = st.tabs(tickers)
            for ticker, foglio_attivo in zip(tickers, fogli_ticker):
                with foglio_attivo:
                    tk_yf = ticker + "-USD" if asset_type == "Criptovaluta" and not ticker.endswith("-USD") else ticker
                    df_c = yf.download(tickers=tk_yf, period="max", interval=tf_attivo, auto_adjust=False, multi_level_index=False, progress=False)
                    if df_c is not None and not df_c.empty:
                        delta = df_c["Close"].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        df_c["RSI"] = 100 - (100 / (1 + (gain / np.where(loss == 0, 0.00001, loss))))
                        tr = pd.concat([df_c["High"]-df_c["Low"], (df_c["High"]-df_c["Close"].shift(1)).abs(), (df_c["Low"]-df_c["Close"].shift(1)).abs()], axis=1).max(axis=1)
                        df_c["ATR"] = tr.rolling(window=14).mean()
                        st.markdown("#### 📊 Oscillatore Momentum RSI (14)\n**Analisi di Momentum:** Verifica se il test del POC avviene in esaurimento trend o se ha spazio per rimbalzare.")
                        st.markdown("#### 📈 Average True Range — ATR (14)\n**Analisi Volatilità:** Un ATR calante indica compressione dei volumi, un ATR in rialzo indica breakout.")
                        
                        fig = make_subplots(rows=5, cols=1, vertical_spacing=0.06, row_heights=[0.24, 0.24, 0.24, 0.14, 0.14], subplot_titles=(f"1. STORICO COMPLETO ({ticker})", f"2. DALL'ATH", f"3. RECENTE {period_label.upper()}", "Indicator RSI", "Indicator ATR"))
                        cfg = [(1, df_c.copy(), p1, vh1, vl1, "Generale"), (2, df_c.loc[df_c["High"].idxmax():].copy(), p2, vh2, vl2, "ATH"), (3, df_c.tail(g3).copy(), p3, vh3, vl3, "Recente")]
                        # Calcola i VP locali per evitare variabili mancanti
                        p1, vh1, vl1, _, _ = calc_vp(df_c.copy())
                        p2, vh2, vl2, _, _ = calc_vp(df_c.loc[df_c["High"].idxmax():].copy())
                        p3, vh3, vl3, _, _ = calc_vp(df_c.tail(g3).copy())
                        cfg = [(1, df_c.copy(), p1, vh1, vl1, "Generale"), (2, df_c.loc[df_c["High"].idxmax():].copy(), p2, vh2, vl2, "ATH"), (3, df_c.tail(g3).copy(), p3, vh3, vl3, "Recente")]
                        
                        for r_idx, df_s, p_poc, p_vh, p_vl, nm in cfg:
                            if df_s.empty: continue
                            fig.add_trace(grp.Candlestick(x=df_s.index, open=df_s["Open"].astype(float), high=df_s["High"].astype(float), low=df_s["Low"].astype(float), close=df_s["Close"].astype(float), name=nm), row=r_idx, col=1)
                            if mostra_bb and len(df_s) > 20:
                                b_m = df_s["Close"].rolling(20).mean(); b_s = df_s["Close"].rolling(20).std()
                                fig.add_trace(grp.Scatter(x=df_s.index, y=b_m+(b_s*2), mode="lines", line=dict(color="rgba(56,189,248,0.4)", width=1, dash="dash")), row=r_idx, col=1)
                                fig.add_trace(grp.Scatter(x=df_s.index, y=b_m-(b_s*2), mode="lines", line=dict(color="rgba(56,189,248,0.4)", width=1, dash="dash")), row=r_idx, col=1)
                            if mostra_poc:
                                fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index[-1], y0=p_poc, y1=p_poc, line=dict(color="#dc3545", width=2), row=r_idx, col=1)
                        
                        df_recent_ind = df_c.tail(180 if tf_attivo == "1wk" else 365)
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["RSI"], mode="lines", line=dict(color="#c084fc", width=2)), row=4, col=1)
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["ATR"], mode="lines", line=dict(color="#34d399", width=2)), row=5, col=1)
                        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=1800, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{ticker}")
with tab2:
    st.subheader("⚙️ Motore di Simulazione Storica (Backtest)")
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        bt_ticker = st.text_input("Ticker da testare:", value="AAPL")
        capitale_iniziale = st.number_input("Capitale iniziale ($):", min_value=100, value=10000)
    with b_col2:
        bt_periodo = st.selectbox("Orizzonte dati:", ["1 Anno", "3 Anni", "5 Anni"])
        rischio_trade = st.slider("Rischio per operazione (%):", min_value=0.5, max_value=5.0, value=1.0)
    with b_col3: comun_fee = st.number_input("Commissioni eseguito ($):", min_value=0.0, value=1.99)

    if st.button("🚀 Esegui Backtest Strategia", type="primary"):
        df_bt = yf.download(tickers=bt_ticker, period={"1 Anno":"1y","3 Anni":"3y","5 Anni":"5y"}[bt_periodo], interval="1d", auto_adjust=False, progress=False)
        if df_bt is not None and len(df_bt) > 60:
            capitale, in_posizione, trade_history, equity_curve, date_curve = capitale_iniziale, False, [], [capitale_iniziale], [df_bt.index]
            for i in range(50, len(df_bt)):
                df_s = df_bt.iloc[:i]; r_a = df_bt.iloc[i]; p_c, d_c = float(r_a["Close"]), df_bt.index[i]
                if not in_posizione:
                    p_poc, _, p_vl, _, _ = calc_vp(df_s)
                    if p_poc is None: continue
                    in_posizione = True; p_ingresso = p_c; livello_sl = p_vl * 0.985
                    size_contratti = (capitale * (rischio_trade / 100)) / max(0.01, abs(p_ingresso - livello_sl))
                else:
                    if float(r_a["Low"]) <= livello_sl:
                        pnl = (livello_sl - p_ingresso) * size_contratti - (comun_fee * 2); capitale += pnl
                        trade_history.append({"Data": d_c.strftime("%d/%m/%Y"), "Tipo": "LONG", "Ingresso": round(p_ingresso,2), "Uscita": round(livello_sl,2), "PnL ($)": round(pnl,2), "Capitale": round(capitale,2)})
                        equity_curve.append(capitale); date_curve.append(d_c); in_posizione = False
            
            if trade_history:
                df_t = pd.DataFrame(trade_history)
                st.columns(4)[0].metric("Ritorno Totale", f"{round(((capitale-capitale_iniziale)/capitale_iniziale)*100,2)} %")
                fig_eq = grp.Figure(grp.Scatter(x=date_curve, y=equity_curve, mode='lines', line=dict(color='#38bdf8')))
                fig_eq.update_layout(template="plotly_dark", height=300); st.plotly_chart(fig_eq, use_container_width=True)
                st.dataframe(df_t, use_container_width=True)
                st.download_button("📥 Scarica Report CSV", data=df_t.to_csv(index=False).encode('utf-8'), file_name="backtest.csv", mime="text/csv")
with tab3:
    st.subheader("🔔 Canale Notifiche in Tempo Reale via Telegram")
    st.success("✅ Algoritmo vettoriale Numpy attivo.")
    fl1, fl2 = st.columns(2)
    with fl1: soglia_distanza = st.slider("Distanza massima dal POC (%):", min_value=0.1, max_value=3.0, value=0.5)
    with fl2: p_selezionato_alert = st.selectbox("Paniere da scansionare:", ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)", "Crypto"], key="tg_paniere")
    
    lista_ticker_alert = [t.strip() for t in ottieni_paniere(p_selezionato_alert).split(",") if t.strip()]
    if st.button("🚀 Attiva Scansione & Invia Alert", type="primary"):
        st.info("Scannerizzazione parziale protetta avviata...")
        segnali = 0; bar = st.progress(0.0)
        for idx, ticker in enumerate(lista_ticker_alert[:15]):
            bar.progress((idx + 1) / 15)
            df_live = yf.download(tickers=ticker, period="max", interval="1d", auto_adjust=False, progress=False, timeout=5)
            if df_live is not None and not df_live.empty:
                p_c = float(df_live["Close"].iloc[-1]); p_poc, _, _, _, _ = calc_vp(df_live)
                if p_poc and abs(((p_c - p_poc) / p_poc) * 100) <= soglia_distanza:
                    segnali += 1
                    invia_messaggio_telegram_sbloccato(T_ID, f"📐 <b>SEGNALE TRIPLE-POC</b>\n\n🎯 Asset: #{ticker}\n📊 Prezzo: {round(p_c,2)}\n🔴 Entry POC: {round(p_poc,2)}")
        st.success(f"Scansione completata! Inviati {segnali} alert precisi su Telegram.")
