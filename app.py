import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as grp
from plotly.subplots import make_subplots
import requests
import json

st.set_page_config(layout="wide", page_title="POC Scanner Pro", page_icon="📐")

# Stile scuro personalizzato per rendere la dashboard moderna
st.markdown("""
<style>
    @import url('https://googleapis.com');
    .stApp { background: radial-gradient(circle at top right, #1a1f36 0%, #0d0f18 100%); font-family: 'Plus Jakarta Sans', sans-serif; color: #f8fafc; }
    h1 { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding-bottom: 15px; }
    div[data-testid="stMetric"] { background: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(56, 189, 248, 0.15) !important; border-radius: 14px !important; padding: 20px !important; }
    div.stButton > button:first-child { background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important; color: #ffffff !important; font-weight: 600 !important; border-radius: 10px !important; padding: 0.7rem 2.2rem !important; }
    button[data-baseweb="tab"] { font-size: 15px !important; font-weight: 600 !important; color: #64748b !important; }
    button[aria-selected="true"] { color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }
    div[data-baseweb="select"], input, textarea { background-color: #0f172a !important; border-color: #334155 !important; color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

st.title("📐 Analisi POC Pro — Dashboard Multitasking")

if "asset_type_index" not in st.session_state:
    st.session_state.asset_type_index = 0
T_ID = "2072895073"
TESTA_INTERNET = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

# ------------------------------------------------------------------------------
# 🚀 MOTORE DI CACHING AVANZATO PER LE CHIAMATE API (VELOCIZZA DEL 90%)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def scarica_dati_sicuri(ticker, period_str, interval_str):
    try:
        df = yf.download(
            tickers=ticker, 
            period=period_str, 
            interval=interval_str, 
            auto_adjust=False, 
            multi_level_index=False, 
            progress=False, 
            timeout=7
        )
        if df is not None and not df.empty:
            df.columns = [str(c).strip() for c in df.columns]
            return df
    except Exception:
        return None
    return None

# ==============================================================================
# DATABASE INTERNO DEI PANIERI AZIONARI AGGIORNATO E AMPLIATO
# ==============================================================================
SP500_FULL = (
    "MMM,AOS,ABT,ABBV,ACN,ADBE,AMD,AES,AFL,A,APD,ABNB,AKAM,ALB,ARE,ALGN,ALLE,LNT,ALL,GOOGL,GOOG,MO,AMZN,AMCR,AEE,"
    "AEP,AXP,AIG,AMT,AWK,AMP,AME,AMGN,APH,ADI,AON,APA,APO,AAPL,AMAT,APP,APTV,ACGL,ADM,ARES,ANET,AJG,AIZ,T,ATO,ADSK,"
    "ADP,AZO,AVY,AXON,BKR,BALL,BAC,BAX,BDX,BRK-B,BBY,TECH,BIIB,BLK,BX,BE,BNY,BA,BKNG,BSX,BMY,AVGO,BR,BRO,BF-B,BG,"
    "BXP,CHRW,CDNS,CPT,COF,CAH,CCL,CARR,CVNA,CASY,CAT,CBOE,CBRE,CDW,COR,CNC,CNP,CF,CRL,SCHW,CHTR,CVX,CMG,CB,CHD,"
    "CIEN,CI,CINF,CTAS,CSCO,C,CFG,CLX,CME,CMS,KO,CTSH,COHR,COIN,CL,CMCSA,FIX,COP,ED,STZ,CEG,COO,CPRT,GLW,CPAY,CTVA,"
    "CSGP,COST,CRH,CRWD,CCI,CSX,CMI,CVS,DHR,DRI,DDOG,DVA,DECK,DE,DELL,DAL,DVN,DXCM,FANG,DLR,DG,DLTR,D,DPZ,DASH,DOV,"
    "DOW,DHI,DTE,DUK,DD,ETN,EBAY,ECHO,ECL,EIX,EW,ELV,EME,EMR,ETR,EOG,EQT,EFX,EQIX,ERIE,ESS,EL,EG,EVRG,P,ES,EXC,EXE,"
    "EXPE,EXPD,EXR,XOM,FFIV,FDS,FICO,FAST,FRT,FDX,FDXF,FERG,FIS,FITB,FSLR,FE,FISV,FLEX,F,FTNT,FTV,FOXA,FOX,BEN,FCX,"
    "GRMN,IT,GE,GEHC,GEV,GEN,GNRC,GD,GIS,GM,GPC,GILD,GPN,GL,GDDY,GS,HAL,HIG,HAS,HCA,DOC,HSIC,HSY,HPE,HLT,HD,HON,HRL,"
    "HST,HWM,HUBB,HUM,HBAN,HII,IBM,IEX,IDXX,ITW,ILMN,INCY,IR,PODD,INTC,IBKR,ICE,IFF,IP,INTU,ISRG,IVZ,INVH,IQV,"
    "IRM,JBHT,JBL,JKHY,J,JNJ,JCI,JPM,KVUE,KDP,KEY,KEYS,KMB,KIM,KMI,KKR,KLAC,KHC,KR,LHX,LH,LRCX,LVS,LDOS,LEN,LII,LLY,"
    "LIN,LYV,LMT,L,LOW,LULU,LITE,LYB,MTB,MPC,MAR,MRSH,MLM,MRVL,MAS,MA,MKC,MCD,MCK,MDT,MRK,META,MET,MTD,MGM,MCHP,MU,"
    "MSFT,MAA,MRNA,MDLZ,MPWR,MNST,MCO,MS,MOS,MSI,MSCI,NDAQ,NTAP,NFLX,NEM,NWSA,NWS,NEE,NKE,NI,NDSN,NSC,NTRS,NOC,NCLH,"
    "NRG,NUE,NVDA,NVR,NXPI,ORLY,OXY,ODFL,OMC,ON,OKE,ORCL,OTIS,PCAR,PKG,PLTR,PANW,PSKY,PH,PAYX,PYPL,PNR,PEP,PFE,PCG,"
    "PM,PSX,PNW,PNC,PPG,PPL,PFG,PG,PGR,PLD,PRU,PEG,PTC,PSA,PHM,PWR,QCOM,DGX,Q,RL,RJF,RDDT,RTX,O,REG,REGN,RF,RSG,"
    "RMD,RVTY,HOOD,ROK,ROL,ROP,ROST,RCL,SPGI,CRM,SBAC,SLB,STX,SRE,NOW,SHW,SPG,SWKS,SJM,SW,SNA,SOLV,SO,LUV,SWK,SBUX,"
    "STT,STLD,STE,SYK,SMCI,SYF,SNPS,SYY,TMUS,TROW,TTWO,TPR,TRGP,TGT,TEL,TDY,TER,TSLA,TXN,TPL,TXT,TMO,TJX,TKO,TSCO,"
    "TT,TDG,TRV,TRMB,TFC,TYL,TSN,USB,UBER,UDR,ULTA,UNP,UAL,UPS,URI,UNH,UHS,VLO,VEEV,VTR,VLTO,VRSN,VRSK,VZ,VRTX,VRT,"
    "VTRS,VICI,V,VST,VMC,WRB,GWW,WAB,WMT,DIS,WBD,WM,WAT,WEC,WFC,WELL,WST,WDC,WY,WSM,WMB,WTW,WDAY,WYNN,XEL,XYL,YUM,"
    "ZBRA,ZBH,ZTS,VYLR"
)

NASDAQ_FULL = (
    "MDLZ,ADI,ADP,ADSK,AAL,ALGN,AMAT,AMD,AMGN,AMZN,ANSS,ASML,TEAM,ADBE,BIIB,BMRN,BKNG,AVGO,CDNS,CDW,CHTR,"
    "CHKP,CTAS,CSCO,CTSH,CMCSA,CPRT,COST,CRWD,DLTR,DXCM,EBAY,EA,EXPE,FAST,META,FISV,FOXA,FOX,GILD,GOOGL,GOOG,"
    "IDXX,ILMN,INCY,INTC,INTU,ISRG,JBHT,JD,KDP,KLAC,KHC,LRCX,MELI,MAR,MTCH,MCHP,MU,MSFT,MRNA,MNST,"
    "NTES,NFLX,NVDA,NXPI,ORLY,OKTA,ODFL,PCAR,PAYX,PYPL,PEP,PDD,REGN,ROST,SIRI,SWKS,SBUX,SNPS,TMUS,TSLA,"
    "TXN,TCOM,VRSN,VRTX,WBA,WDAY,XEL,ZM,ALAB,CRWV,RKLB,NBIS,STX,MPWR,TER"
)

FTSEMIB_FULL = (
    "A2A.MI,AMP.MI,AZM.MI,BAMI.MI,BCA.MI,BMED.MI,BPER.MI,CPR.MI,DIA.MI,ENI.MI,ERG.MI,EVO.MI,FBK.MI,G.MI,"
    "HER.MI,INW.MI,ISP.MI,LDO.MI,MB.MI,MONC.MI,NEXI.MI,PIRC.MI,PRY.MI,PST.MI,RACE.MI,REC.MI,SGO.MI,SRG.MI,"
    "STLAM.MI,STMPA.MI,TEN.MI,TRN.MI,UCG.MI,UNI.MI,YSVP.MI,BMPS.MI,BPSO.MI,BC.MI,AVIO.MI,IP.MI"
)

TOTAL1_LEADERS = "BTC-USD,ETH-USD,USDT-USD,USDC-USD"
TOTAL2_MAJORS = "SOL-USD,BNB-USD,XRP-USD,ADA-USD,TRX-USD,DOT-USD,LINK-USD,AVAX-USD,TON-USD,SHIB-USD,SUI-USD"
TOTAL3_ALTS = (
    "MATIC-USD,LTC-USD,UNI-USD,NEAR-USD,APT-USD,ICP-USD,STX-USD,FIL-USD,ATOM-USD,"
    "IMX-USD,RNDR-USD,GRT-USD,FTM-USD,OP-USD,ARB-USD,INJ-USD,LDO-USD,TIA-USD,"
    "SEI-USD,AAVE-USD,MKR-USD,RUNE-USD,EGLD-USD,THETA-USD,ALGO-USD,XLM-USD,VET-USD,"
    "FLOW-USD,AXS-USD,SAND-USD,MANA-USD,GALA-USD,CHZ-USD,DYDX-USD,CRV-USD,ENS-USD,"
    "LRC-USD,ANKR-USD,WOO-USD,GMX-USD,JUP-USD,FET-USD,TAO-USD,WLD-USD,ONDO-USD,PYTH-USD,JTO-USD"
)
CRYPTO_FULL = f"{TOTAL1_LEADERS},{TOTAL2_MAJORS},{TOTAL3_ALTS}"

MIDCAP_US = (
    "ONDS,RGTI,AGIO,AIRS,ALG,HUBS,CLX,IREN,RIVN,MARA,JAN,LIFE,MXL,IESC,HALO,TXRH,DKS,WFR,DT,"
    "SMR,XPO,GFL,FLEX,JBL,AA,MTDR,CHX,OVV,STNG,WBS,DINO,AMR,SF,LANC,PNR,XOM,AAL,X"
)
CRYPTO_STOCKS = "COIN,MARA,IREN,CLSK,WULF,MSTR,HUT,CORZ,RIOT,CIFR,BTBT,BOOM"
EUROSTOXX_FULL = (
    "ADS.DE,ALV.DE,BAS.DE,BAYN.DE,BMW.DE,DB1.DE,DBK.DE,DPW.DE,DTE.DE,EOAN.DE,IFX.DE,MBG.DE,MUV2.DE,RWE.DE,SAP.DE,SIE.DE,"
    "AI.PA,AIR.PA,ALO.PA,CS.PA,BNP.PA,CA.PA,DG.PA,EL.PA,ERF.PA,OR.PA,MC.PA,ML.PA,ORAN.PA,RI.PA,RMS.PA,SAN.PA,SGO.PA,"
    "SU.PA,TTE.PA,VIE.PA,VIV.PA,ASML.AS,ADYEN.AS,INGA.AS,KPN.AS,PRX.AS,BBVA.MC,SAN.MC,ITX.MC,REP.MC,ENI.MI,ISP.MI,UCG.MI"
)

ELENCO_PANIERI = ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)", "Crypto", "US Mid-Caps", "Crypto & AI Stocks", "Euro Stoxx 50"]

def ottieni_paniere(nome_paniere):
    if nome_paniere == "S&P 500": return SP500_FULL
    elif nome_paniere == "NASDAQ 100": return NASDAQ_FULL
    elif nome_paniere == "FTSE MIB (FIB)": return FTSEMIB_FULL
    elif nome_paniere == "Crypto": return CRYPTO_FULL
    elif nome_paniere == "US Mid-Caps": return MIDCAP_US
    elif nome_paniere == "Crypto & AI Stocks": return CRYPTO_STOCKS
    elif nome_paniere == "Euro Stoxx 50": return EUROSTOXX_FULL
    return "AAPL,MSFT"

def invia_messaggio_telegram_sbloccato(chat_id, testo_messaggio):
    payload = {"chat_id": int(chat_id), "text": str(testo_messaggio), "parse_mode": "HTML", "disable_web_page_preview": False}
    try:
        part1, part2 = "https://" + "api.", "telegram.org/bot"
        part3 = "8887634238:AAFH6eMqMhSTbe3pkUU_u0dpOulZXrud7RE/sendMessage"
        url_pulito = part1 + part2 + part3
        res = requests.post(url_pulito, data=json.dumps(payload), headers=TESTA_INTERNET, timeout=12)
        return res.status_code == 200
    except Exception:
        return False

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
# ==========================================
# --- TAB 1: TRE POC DINAMICI ---
# ==========================================
with tab1:
    st.subheader("📊 Analisi Grafica Avanzata Volume Profile & Indicatori")
    st.markdown("##### ⚙️ Personalizzazione Livelli Grafici")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1: mostra_poc = st.checkbox("Mostra Linea POC Entry (Rosso)", value=True, key="chk_poc")
    with t_col2: mostra_va = st.checkbox("Mostra Value Area & Istogrammi (VAH/VAL)", value=True, key="chk_va")
    with t_col3: mostra_rr = st.checkbox("Mostra Zone Target / Stop Loss Strategici (ATR 1:2)", value=True, key="chk_rr")
    with t_col4: mostra_bb = st.checkbox("Mostra Bande di Bollinger (Volatilità Price)", value=True, key="chk_bb")
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        paniere_selezionato = st.selectbox("Seleziona Indice/Paniere:", ELENCO_PANIERI, key="an_paniere")
        ticker_caricati = ottieni_paniere(paniere_selezionato)
        st.session_state.asset_type_index = 1 if paniere_selezionato == "Crypto" else 0
    with col2: asset_type = st.selectbox("Tipo Asset:", ["Azione", "Criptovaluta"], index=st.session_state.asset_type_index, key="an_type")
    with col3:
        period_label = st.selectbox("Seleziona Estensione Profilo Recente:", ["3 Mesi", "6 Mesi", "9 Mesi"], key="an_period")
        g3 = {"3 Mesi": 90, "6 Mesi": 180, "9 Mesi": 270}[period_label]
    with col4:
        tf_label = st.selectbox("Seleziona Timeframe Candele:", ["Giornaliero (Daily)", "Settimanale (Weekly)"], key="an_timeframe")
        tf_attivo = {"Giornaliero (Daily)": "1d", "Settimanale (Weekly)": "1wk"}[tf_label]

    tickers_input = st.text_area("Modifica o verifica i Tickers estratti:", value=ticker_caricati, height=150, key=f"an_area_{paniere_selezionato}")
    if st.button("🔍 Avvia Analisi Grafica Nodes", type="primary"):
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        if not tickers: st.warning("Inserisci almeno un ticker valido.")
        else:
            st.success("Generazione fogli ticker...")
            fogli_ticker = st.tabs([t.replace("-USD", "") for t in tickers])
            for ticker, foglio_attivo in zip(tickers, fogli_ticker):
                with foglio_attivo:
                    tk_yf = ticker + "-USD" if asset_type == "Criptovaluta" and not ticker.endswith("-USD") else ticker
                    df_c = yf.download(tickers=tk_yf, period="max", interval=tf_attivo, auto_adjust=False, multi_level_index=False, progress=False)
                    if df_c is not None and len(df_c) > 200:
                        df_c.columns = [str(c).strip() for c in df_c.columns]
                        close_series = df_c["Close"].astype(float)
                        high_series = df_c["High"].astype(float)
                        low_series = df_c["Low"].astype(float)
                        d_ath = high_series.idxmax()
                        p_att = float(close_series.iloc[-1])
                        
                        df_c["EMA200"] = close_series.ewm(span=200, adjust=False).mean()
                        ema200_att = df_c["EMA200"].iloc[-1]
                        delta = close_series.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        df_c["RSI"] = 100 - (100 / (1 + (gain / np.where(loss == 0, 0.00001, loss))))
                        rsi_att = df_c["RSI"].iloc[-1]
                        
                        tr = pd.concat([high_series-low_series, (high_series-close_series.shift(1)).abs(), (low_series-close_series.shift(1)).abs()], axis=1).max(axis=1)
                        df_c["ATR"] = tr.rolling(window=14).mean()
                        atr_att = df_c["ATR"].iloc[-1]
                        
                        df1, df2, df3 = df_c.copy(), df_c.loc[d_ath:].copy(), df_c.tail(g3).copy()
                        p1, vh1, vl1, prz1, vl_v1 = calc_vp(df1)
                        p2, vh2, vl2, prz2, vl_v2 = calc_vp(df2)
                        p3, vh3, vl3, prz3, vl_v3 = calc_vp(df3)
                        
                        if None in [p1, vh1, vl1, p2, vh2, vl2, p3, vh3, vl3]: continue
                        # --- CALCOLO VALORI DI INGRESSO E DIREZIONE PER IL MENU DI RIEPILOGO ---
                        is_long_1 = p_att >= p1
                        is_long_2 = p_att >= p2
                        is_long_3 = p_att >= p3
                        
                        dec_f = 4 if asset_type == "Criptovaluta" else 2
                        st.markdown(f"""
                        <div style='background: rgba(15, 23, 42, 0.6); padding: 15px; border-radius: 14px; margin-bottom: 25px; border: 1px solid rgba(56, 189, 248, 0.2);'>
                            <h4 style='margin-top:0; color:#38bdf8; font-family: "Plus Jakarta Sans", sans-serif;'>🎯 Riepilogo Ingressi Operativi</h4>
                            <p style='margin-bottom:6px; font-size:15px;'>📈 <b>1. Profilo Generale (Storico):</b> <span style='color:{"#22c55e" if is_long_1 else "#ef4444"}; font-weight:bold;'>{'LONG 🟢' if is_long_1 else 'SHORT 🔴'}</span> | Ingresso: <b>{round(p_att, dec_f)}</b> | POC: <b>{round(p1, dec_f)}</b></p>
                            <p style='margin-bottom:6px; font-size:15px;'>🏛️ <b>2. Profilo Dall'ATH:</b> <span style='color:{"#22c55e" if is_long_2 else "#ef4444"}; font-weight:bold;'>{'LONG 🟢' if is_long_2 else 'SHORT 🔴'}</span> | Ingresso: <b>{round(p_att, dec_f)}</b> | POC: <b>{round(p2, dec_f)}</b></p>
                            <p style='margin-bottom:0; font-size:15px;'>⚡ <b>3. Profilo Recente ({period_label}):</b> <span style='color:{"#22c55e" if is_long_3 else "#ef4444"}; font-weight:bold;'>{'LONG 🟢' if is_long_3 else 'SHORT 🔴'}</span> | Ingresso: <b>{round(p_att, dec_f)}</b> | POC: <b>{round(p3, dec_f)}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        fig = make_subplots(
                            rows=5, cols=1, vertical_spacing=0.06, row_heights=[0.24, 0.24, 0.24, 0.14, 0.14], 
                            subplot_titles=(
                                f"1. STORICO COMPLETO ({ticker}) — {'LONG 🟢' if is_long_1 else 'SHORT 🔴'} Entry: {round(p_att,2)} | POC: {round(p1,2)} | EMA200: {round(ema200_att,2)}", 
                                f"2. DALL'ATH ({d_ath.strftime('%d/%m/%Y')}) — {'LONG 🟢' if is_long_2 else 'SHORT 🔴'} Entry: {round(p_att,2)} | POC: {round(p2,2)}", 
                                f"3. PROFILO RECENTE {period_label.upper()} — {'LONG 🟢' if is_long_3 else 'SHORT 🔴'} Entry: {round(p_att,2)} | POC: {round(p3,2)}", 
                                "📊 RSI (14) — Momentum di Filtro", "📈 ATR (14) — Volatilità Dinamica"
                            )
                        )
                        cfg = [(1, df1, prz1, vl_v1, p1, vh1, vl1, "Generale"), (2, df2, prz2, vl_v2, p2, vh2, vl2, "ATH"), (3, df3, prz3, vl_v3, p3, vh3, vl3, f"{g3}D")]
                        for r_idx, df_s, p_vp, v_vp, p_poc, p_vh, p_vl, nm in cfg:
                            if df_s.empty: continue
                            fig.add_trace(grp.Candlestick(x=df_s.index, open=df_s["Open"].astype(float), high=df_s["High"].astype(float), low=df_s["Low"].astype(float), close=df_s["Close"].astype(float), name=nm), row=r_idx, col=1)
                            fig.add_trace(grp.Scatter(x=df_s.index, y=df_s["EMA200"], mode="lines", name="EMA 200", line=dict(color="#f43f5e", width=1.5)), row=r_idx, col=1)
                            
                            if mostra_bb and len(df_s) > 20:
                                b_m = df_s["Close"].rolling(20).mean(); b_s = df_s["Close"].rolling(20).std()
                                fig.add_trace(grp.Scatter(x=df_s.index, y=b_m+(b_s*2), mode="lines", line=dict(color="rgba(56,189,248,0.25)", width=1, dash="dash")), row=r_idx, col=1)
                                fig.add_trace(grp.Scatter(x=df_s.index, y=b_m-(b_s*2), mode="lines", line=dict(color="rgba(56,189,248,0.25)", width=1, dash="dash")), row=r_idx, col=1)
                            
                            if mostra_va and v_vp and max(v_vp) > 0:
                                m_v, d_i, d_f = max(v_vp), df_s.index.min(), df_s.index.max()
                                ext = (d_f - d_i).days; step_k = max(1, len(v_vp) // 60)
                                for i in range(0, len(v_vp), step_k):
                                    idx_f = min(i + step_k, len(v_vp) - 1); y0_v, y1_v = float(p_vp[i]), float(p_vp[idx_f])
                                    if y0_v == y1_v: sp_m = (max(p_vp) - min(p_vp)) * 0.005; y0_v -= sp_m; y1_v += sp_m
                                    w = (float(v_vp[i]) / m_v) * (ext * 0.18) if m_v > 0 else 0
                                    fig.add_shape(type="rect", x0=d_i, x1=d_i + pd.Timedelta(days=int(w) if w > 0 else 1), y0=y0_v, y1=y1_v, fillcolor="rgba(242,142,43,0.20)" if p_vl <= p_vp[i] <= p_vh else "rgba(0,165,181,0.06)", line=dict(width=0), row=r_idx, col=1)
                            
                            is_long = p_att >= p_poc
                            sl = p_att - (1.5 * atr_att) if is_long else p_att + (1.5 * atr_att)
                            tp = p_att + (3.0 * atr_att) if is_long else p_att - (3.0 * atr_att)
                            col_z = "rgba(34, 197, 94, 0.08)" if is_long else "rgba(239, 68, 68, 0.08)"
                            ic, dir_n = ("🟢", "LONG") if is_long else ("🔴", "SHORT")
                            
                            d_li, d_lf = df_s.index[int(len(df_s)*0.70)], df_s.index[-1]
                            if mostra_rr and not np.isnan(atr_att):
                                fig.add_shape(type="rect", x0=d_li, x1=d_lf, y0=min(p_att, tp), y1=max(p_att, tp), fillcolor=col_z, line=dict(width=0), row=r_idx, col=1)
                                fig.add_shape(type="line", x0=d_li, x1=d_lf, y0=sl, y1=sl, line=dict(color="#f59e0b", width=1.5, dash="dash"), row=r_idx, col=1)
                                fig.add_shape(type="line", x0=d_li, x1=d_lf, y0=tp, y1=tp, line=dict(color="#06b6d4", width=2), row=r_idx, col=1)
                            
                            if mostra_poc:
                                fig.add_shape(type="line", x0=df_s.index.min(), x1=d_lf, y0=p_poc, y1=p_poc, line=dict(color="#ef4444", width=2.5), row=r_idx, col=1)
                            
                            # --- TRACCIAMENTO LINEA DI INGRESSO E FRECCIA DIREZIONALE SUL GRAFICO ---
                            fig.add_shape(type="line", x0=df_s.index.min(), x1=d_lf, y0=p_att, y1=p_att, line=dict(color="#a855f7", width=2, dash="dot"), row=r_idx, col=1)
                            
                            fig.add_annotation(
                                x=d_lf, y=p_att,
                                text=f"📊 ENTRY {dir_n} {round(p_att, 2)}",
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor="#22c55e" if is_long else "#ef4444",
                                ax=-55,
                                ay=-35 if is_long else 35,
                                font=dict(color="white", size=10, family="Plus Jakarta Sans"),
                                bgcolor="#22c55e" if is_long else "#ef4444",
                                bordercolor="white",
                                borderwidth=1,
                                borderpad=4,
                                row=r_idx, col=1
                            )
                            
                            txt_leg = f"<b>📊 PROFILO {nm.upper()}</b><br>Setup: {ic} {dir_n}<br>🟣 ENTRY: {round(p_att,2)}<br>🔴 POC: {round(p_poc,2)}<br>🟠 VAH: {round(p_vh,2)}<br>🔵 VAL: {round(p_vl,2)}"
                            fig.add_annotation(xref="paper", yref="paper", x=0.01, y={1:0.98, 2:0.72, 3:0.44}[r_idx], text=txt_leg, showarrow=False, align="left", bgcolor="rgba(20,24,33,0.95)", bordercolor="rgba(242,142,43,0.4)", borderwidth=1.5, borderpad=8, font=dict(color="white", size=10))
                        
                        df_recent_ind = df_c.tail(180 if tf_attivo == "1wk" else 365)
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["RSI"], mode="lines", name="RSI", line=dict(color="#a855f7", width=2)), row=4, col=1)
                        fig.add_shape(type="line", x0=df_recent_ind.index.min(), x1=df_recent_ind.index[-1], y0=75, y1=75, line=dict(color="rgba(239, 68, 68, 0.4)", width=1.5, dash="dot"), row=4, col=1)
                        fig.add_shape(type="line", x0=df_recent_ind.index.min(), x1=df_recent_ind.index[-1], y0=25, y1=25, line=dict(color="rgba(34, 197, 94, 0.4)", width=1.5, dash="dot"), row=4, col=1)
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["ATR"], mode="lines", name="ATR", line=dict(color="#10b981", width=2)), row=5, col=1)
                        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False, xaxis3_rangeslider_visible=False, xaxis4_rangeslider_visible=False, xaxis5_rangeslider_visible=False, height=2000, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{ticker}")
                    else: st.warning(f"Dati storici insufficienti per {ticker}.")

# ==========================================
# --- TAB 2: MAPPATURA ANCHORED POC DINAMICI ---
# ==========================================
with tab2:
    st.subheader("📐 Mappatura Quantitativa — POC Dinamici di Momentum")
    st.markdown("*Genera gli istogrammi dei volumi ancorati ad ogni cambio di momentum storico fino all'ATH, con proiezione orizzontale continua del POC.*")
    
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        bt_ticker = st.text_input("Inserisci il Ticker da mappare (es. AAPL):", value="AAPL", key="bt_tick_av")
    with b_col2:
        bt_periodo = st.selectbox("Estensione temporale dello storico:", ["1 Anno", "3 Anni", "5 Anni", "Storico Massimo"], index=2, key="bt_per_av")
        mappa_periodi = {"1 Anno": "1y", "3 Anni": "3y", "5 Anni": "5y", "Storico Massimo": "max"}

    if st.button("🚀 Avvia Mappatura Grafica POC", type="primary", key="btn_run_bt_av"):
        st.info(f"Analisi vettoriale e scansione dei blocchi volumetrici per {bt_ticker}...")
        df_bt = scarica_dati_sicuri(bt_ticker, mappa_periodi[bt_periodo], "1d")
        
        if df_bt is not None and len(df_bt) > 100:
            close_series = df_bt["Close"].astype(float)
            high_series = df_bt["High"].astype(float)
            low_series = df_bt["Low"].astype(float)
            
            # Calcolo indicatori per intercettare i cambi di trend strutturali
            df_bt["EMA200"] = close_series.ewm(span=200, adjust=False).mean()
            delta = close_series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            df_bt["RSI"] = 100 - (100 / (1 + (gain / np.where(loss == 0, 0.00001, loss))))
            df_bt["RSI_NEXT"] = df_bt["RSI"].shift(-1)
            
            d_ath_globale = high_series.idxmax()
            idx_ath_globale = df_bt.index.get_loc(d_ath_globale)
            
            # Algoritmo di segmentazione automatica delle ancore
            punti_ancora = [0]
            stato_trend = "LONG" if close_series.iloc[0] > df_bt["EMA200"].iloc[0] else "SHORT"
            
            for i in range(20, len(df_bt)):
                if i == idx_ath_globale:
                    punti_ancora.append(i)
                    break
                prezzo_c = close_series.iloc[i]
                ema_c = df_bt["EMA200"].iloc[i]
                rsi_c = df_bt["RSI"].iloc[i]
                rsi_next = df_bt["RSI_NEXT"].iloc[i]
                
                # Svolta 1: Incrocio della media mobile a 200 periodi
                nuovo_trend = "LONG" if prezzo_c > ema_c else "SHORT"
                if nuovo_trend != stato_trend:
                    punti_ancora.append(i)
                    stato_trend = nuovo_trend
                    continue
                
                # Svolta 2: Rientro dalle bande estreme dell'RSI (Iperestensione)
                if rsi_c > 75 or rsi_c < 25:
                    if not np.isnan(rsi_next):
                        if (rsi_c > 75 and rsi_next <= 75) or (rsi_c < 25 and rsi_next >= 25):
                            punti_ancora.append(i)
                            
            if len(df_bt) - 1 not in punti_ancora: 
                punti_ancora.append(len(df_bt) - 1)
            punti_ancora = sorted(list(set(punti_ancora)))
            
            profili_volumetrici_locali = []
            linee_poc_estese = []
            # Calcolo dei singoli Volume Profile per ogni finestra temporale individuata
            for s in range(len(punti_ancora) - 1):
                idx_inizio, idx_fine = punti_ancora[s], punti_ancora[s+1]
                df_segmento = df_bt.iloc[idx_inizio:idx_fine+1]
                if len(df_segmento) < 5: continue
                
                # Risoluzione a 80 bins per garantire fluidità di rendering su Streamlit Cloud
                p_poc, p_vh, p_vl, prezzi_v, volumi_v = calc_vp(df_segmento, div=80)
                if p_poc is None: continue
                
                profili_volumetrici_locali.append({
                    "data_ancora": df_bt.index[idx_inizio], "data_fine_blocco": df_bt.index[idx_fine], 
                    "prezzi": prezzi_v, "volumi": volumi_v, "val_min": p_vl, "val_max": p_vh
                })
                
                # Estensione lineare continua: ogni linea rossa del POC arriva fino all'ULTIMA data disponibile del grafico
                linee_poc_estese.append({
                    "data_inizio": df_bt.index[idx_inizio], "data_fine_assoluta": df_bt.index[-1], 
                    "livello_prezzo": p_poc, "tipo": "Intermedio" if idx_inizio != idx_ath_globale else "Dall'ATH"
                })

            # --- CORPO GRAFICO MULTILIVELLO TRADINGVIEW-STYLE ---
            fig_tv = grp.Figure()
            
            # Candele giapponesi di sfondo dello storico selezionato
            fig_tv.add_trace(grp.Candlestick(
                x=df_bt.index, open=df_bt["Open"], high=df_bt["High"], low=df_bt["Low"], close=df_bt["Close"], name="Prezzo"
            ))
            
            # Rendering geometrico degli istogrammi laterali all'inizio di ciascun blocco di momentum
            for prof in profili_volumetrici_locali:
                prezzi_p, volumi_p = prof["prezzi"], prof["volumi"]
                if len(volumi_p) > 0 and max(volumi_p) > 0:
                    max_vol = max(volumi_p)
                    data_inizio_b, data_fine_b = prof["data_ancora"], prof["data_fine_blocco"]
                    ampiezza_blocco_giorni = max(1, (data_fine_b - data_inizio_b).days)
                    passo_disegno = max(1, len(volumi_p) // 40) # Condensamento dei cassetti verticali per massima fluidità
                    
                    for idx_v in range(0, len(volumi_p), passo_disegno):
                        v_attuale, p_livello = volumi_p[idx_v], prezzi_p[idx_v]
                        # Larghezza dell'istogramma impostata al massimo al 20% dello spazio orizzontale del blocco
                        larghezza_barra_giorni = int((v_attuale / max_vol) * (ampiezza_blocco_giorni * 0.20))
                        if File_barra_giorni := (larghezza_barra_giorni < 1): 
                            larghezza_barra_giorni = 1
                            
                        colore_barra = "rgba(56, 189, 248, 0.25)" if prof["val_min"] <= p_livello <= prof["val_max"] else "rgba(100, 116, 139, 0.08)"
                        fig_tv.add_shape(type="rect", x0=data_inizio_b, x1=data_inizio_b + pd.Timedelta(days=larghezza_barra_giorni), y0=p_livello - (p_livello * 0.003), y1=p_livello + (p_livello * 0.003), fillcolor=colore_barra, line=dict(width=0))
            
            # Sovrapposizione delle linee orizzontali del POC estese fino a fine grafico (Colore Rosso)
            for poc_l in linee_poc_estese:
                colore_poc = "#ef4444" if poc_l["tipo"] == "Intermedio" else "#f43f5e"
                spessore_linea = 2 if poc_l["tipo"] == "Intermedio" else 3
                
                fig_tv.add_shape(
                    type="line", 
                    x0=poc_l["data_inizio"], x1=poc_l["data_fine_assoluta"], 
                    y0=poc_l["livello_prezzo"], y1=poc_l["livello_prezzo"], 
                    line=dict(color=colore_poc, width=spessore_linea, dash="dash" if poc_l["tipo"] == "Intermedio" else "solid")
                )
                # Etichetta numerica del livello a fine asse destro
                fig_tv.add_annotation(
                    x=poc_l["data_fine_assoluta"], y=poc_l["livello_prezzo"], 
                    text=f" POC: {round(poc_l['livello_prezzo'], 2)}", 
                    showarrow=False, align="left", xanchor="left", font=dict(color=colore_poc, size=9)
                )
            
            fig_tv.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False, showlegend=False)
            st.plotly_chart(fig_tv, use_container_width=True)
            st.success(f"Mappatura completata con successo! Tracciati {len(linee_poc_estese)} profili di momentum strutturale.")
        else:
            st.error("Dati storici insufficienti per generare la mappatura. Controlla il Ticker inserito.")


# ==========================================
# --- TAB 3: LIVE ALERTS STRATEGICI ---
# ==========================================
with tab3:
    st.subheader("🔔 Canale Notifiche Quantitative in Tempo Reale via Telegram")
    st.success("✅ Algoritmo di Strategia Bilanciata Integrato.")
    
    fl1, fl2, fl3 = st.columns(3)
    with fl1: soglia_distanza = st.slider("Seleziona la distanza massima dal POC (%):", min_value=0.5, max_value=4.0, value=2.0, step=0.1, key="tg_dist")
    with fl2: poc_scelti = st.multiselect("Seleziona quali profili analizzare:", options=["Generale", "ATH", "Recente (90D)"], default=["Generale", "ATH", "Recente (90D)"], key="tg_sel_p")
    with fl3:
        orizzonte_recente = st.selectbox("Estensione profilo Recente:", ["3 Mesi", "6 Mesi", "9 Mesi"], index=0, key="tg_oriz_t")
        g_recenti_scelti = {"3 Mesi": 90, "6 Mesi": 180, "9 Mesi": 270}[orizzonte_recente]

    p_selezionato_alert = st.selectbox("Seleziona il paniere completo da scansionare:", ELENCO_PANIERI, key="tg_paniere")
    lista_ticker_alert = [t.strip() for t in ottieni_paniere(p_selezionato_alert).split(",") if t.strip()]
    
    if st.button("🚀 Attiva Scansione Strategica", type="primary"):
        if not poc_scelti: st.error("❌ Seleziona almeno una tipologia di POC nei filtri.")
        else:
            st.info(f"Avvio scansione quantitativa bilanciata su {p_selezionato_alert}...")
            segnali_trovati, totale_titoli = 0, len(lista_ticker_alert)
            barra_progresso = st.progress(0.0)
            
            for idx, ticker in enumerate(lista_ticker_alert):
                barra_progresso.progress((idx + 1) / totale_titoli)
                is_crypto_mode = (p_selezionato_alert == "Crypto")
                tk_yf = ticker + "-USD" if is_crypto_mode and not ticker.endswith("-USD") else ticker
                
                df_live = yf.download(tickers=tk_yf, period="max", interval="1d", auto_adjust=False, multi_level_index=False, progress=False, timeout=8)
                if df_live is None or len(df_live) < 200: continue
                
                df_live.columns = [str(c).strip() for c in df_live.columns]
                close_series = df_live['Close'].astype(float)
                high_series = df_live['High'].astype(float)
                low_series = df_live['Low'].astype(float)
                p_attuale = float(close_series.iloc[-1])
                d_ath = high_series.idxmax()
                
                ema200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1]
                delta = close_series.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi_attuale = (100 - (100 / (1 + (gain / np.where(loss == 0, 0.00001, loss))))).iloc[-1]
                tr = pd.concat([high_series - low_series, (high_series - close_series.shift(1)).abs(), (low_series - close_series.shift(1)).abs()], axis=1).max(axis=1)
                atr_attuale = tr.rolling(window=14).mean().iloc[-1]
                
                df_generale, df_ath_data, df_recente = df_live.copy(), df_live.loc[d_ath:].copy(), df_live.tail(g_recenti_scelti).copy()
                controlli_da_effettuare = []
                if "Generale" in poc_scelti: controlli_da_effettuare.append(("GENERALE", df_generale))
                if "ATH" in poc_scelti: controlli_da_effettuare.append(("DALL'ATH", df_ath_data))
                if "Recente (90D)" in poc_scelti: controlli_da_effettuare.append((f"RECENTE ({orizzonte_recente})", df_recente))
                    
                for nome_profilo, df_singolo_profilo in controlli_da_effettuare:
                    if df_singolo_profilo.empty: continue
                    p_poc, p_vh, p_vl, prz_v, vl_v = calc_vp(df_singolo_profilo)
                    if p_poc is None or atr_attuale is None or np.isnan(atr_attuale): continue
                    distanza_percentuale = ((p_attuale - p_poc) / p_poc) * 100
                    
                    if abs(distanza_percentuale) <= soglia_distanza:
                        is_rsi_ok_long = rsi_attuale < 75
                        is_rsi_ok_short = rsi_attuale > 25
                        passa_trend_long = p_attuale > ema200 if "RECENTE" in nome_profilo else True
                        passa_trend_short = p_attuale < ema200 if "RECENTE" in nome_profilo else True
                        
                        setup_valido = False
                        if p_attuale >= p_poc and passa_trend_long and is_rsi_ok_long:
                            direzione, stop_l, take_p, setup_valido = "LONG 🟢", p_attuale - (1.5 * atr_attuale), p_attuale + (3.0 * atr_attuale), True
                        elif p_attuale < p_poc and passa_trend_short and is_rsi_ok_short:
                            direzione, stop_l, take_p, setup_valido = "SHORT 🔴", p_attuale + (1.5 * atr_attuale), p_attuale - (3.0 * atr_attuale), True
                        
                        if setup_valido:
                            segnali_trovati += 1
                            ticker_pulito = str(ticker).replace(".MI", "").replace("-USD", "").strip()
                            url_stringa_pura = f"https://tradingview.com/chart/sqBvK6ky/?symbol={ticker_pulito}"
                            dec = 4 if is_crypto_mode else 2
                            
                            messaggio_alert = (
                                f"🚨 <b>STRATEGIA QUANT BILANCIATA (DASHBOARD)</b>\n\n"
                                f"🎯 <b>Ticker:</b> #{ticker_pulito} ({p_selezionato_alert})\n"
                                f"🗂️ <b>Profilo Volume:</b> {nome_profilo}\n"
                                f"⚡ <b>Setup Operativo:</b> {direzione}\n\n"
                                f"📊 <b>Prezzo Attuale:</b> {round(p_attuale, dec)} USD\n"
                                f"🟠 <b>Stop Loss (1.5 ATR):</b> {round(stop_l, dec)}\n"
                                f"🔵 <b>Take Profit (3.0 ATR):</b> {round(take_p, dec)}\n\n"
                                f"🔗 <a href='{url_stringa_pura}'>APRI IL GRAFICO SU TRADINGVIEW</a>"
                            )
                            invia_messaggio_telegram_sbloccato(T_ID, messaggio_alert)
                            
            st.success(f"Scansione terminata! Inviati {segnali_trovati} segnali bilanciati.")
