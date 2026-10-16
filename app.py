import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as grp
from plotly.subplots import make_subplots
import requests
import json
import matplotlib.pyplot as plt
from arch import arch_model


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

ELENCO_PANIERI = [
    "S&P 500", 
    "NASDAQ 100", 
    "FTSE MIB (FIB)", 
    "Crypto", 
    "US Mid-Caps", 
    "Crypto & AI Stocks", 
    "Euro Stoxx 50"
]
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Analisi Triple-POC", 
    "Analisi Geometrica POC", 
    "Breakout Trend-Following", 
    "Alert Telegram", 
    "Analisi GARCH"
])

# ==========================================
# --- TAB 1: TRE POC SCANNER ---
# ==========================================
with tab1:
    st.subheader("📊 Analisi Grafica Avanzata Volume Profile & Indicatori")
    st.markdown("##### ⚙️ Personalizzazione Livelli Grafici")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1: mostra_poc = st.checkbox("Mostra Linea POC Entry (Rosso)", value=True, key="chk_poc")
    with t_col2: mostra_va = st.checkbox("Mostra Value Area & Istogrammi (VAH/VAL)", value=True, key="chk_va")
    with t_col3: mostra_rr = st.checkbox("Mostra Zone Target / Stop Loss Strategici (ATR 1:2)", value=True, key="chk_rr")
    with t_col4: mostra_bb = st.checkbox("Mostra Bande di Bollinger (Volatilità Price)", value=True, key="chk_bb")
    
    c_col1, c_col2 = st.columns(2)
    with c_col1: mostra_trend = st.checkbox("📐 Mostra Trendline Dinamica sui Massimi (Linea Bianca)", value=True, key="chk_trend")
    with c_col2: mostra_sl_tp = st.checkbox("🎯 Mostra Linee Orizzontali SL / TP (Gialla e Azzurra)", value=True, key="chk_sltp")
    
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

    tickers_input = st.text_area("Modifica o verifica i Tickers estratti:", value="", height=100, key=f"an_area_{paniere_selezionato}")
    if st.button("🔍 Avvia Analisi Grafica Nodes", type="primary"):
        if tickers_input.strip() == "":
            tickers = [t.strip().upper() for t in ticker_caricati.split(',') if t.strip()]
        else:
            tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
            
        if not tickers: 
            st.warning("Inserisci almeno un ticker valido.")
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
                        
                        is_long_1 = p_att >= p1
                        is_long_2 = p_att >= p2
                        is_long_3 = p_att >= p3
                        
                        sl_1 = p_att - (1.5 * atr_att) if is_long_1 else p_att + (1.5 * atr_att)
                        tp_1 = p_att + (3.0 * atr_att) if is_long_1 else p_att - (3.0 * atr_att)
                        sl_2 = p_att - (1.5 * atr_att) if is_long_2 else p_att + (1.5 * atr_att)
                        tp_2 = p_att + (3.0 * atr_att) if is_long_2 else p_att - (3.0 * atr_att)
                        sl_3 = p_att - (1.5 * atr_att) if is_long_3 else p_att + (1.5 * atr_att)
                        tp_3 = p_att + (3.0 * atr_att) if is_long_3 else p_att - (3.0 * atr_att)
                        
                        dec_f = 4 if asset_type == "Criptovaluta" else 2
                        st.markdown(f"""
                        <div style='background: rgba(15, 23, 42, 0.6); padding: 15px; border-radius: 14px; margin-bottom: 25px; border: 1px solid rgba(56, 189, 248, 0.2);'>
                            <h4 style='margin-top:0; color:#38bdf8; font-family: "Plus Jakarta Sans", sans-serif;'>🎯 Riepilogo Ingressi Operativi & Risk Management</h4>
                            <p style='margin-bottom:6px; font-size:15px;'>📈 <b>1. Profilo Generale (Storico):</b> <span style='color:{"#22c55e" if is_long_1 else "#ef4444"}; font-weight:bold;'>{'LONG 🟢' if is_long_1 else 'SHORT 🔴'}</span> | Entry: <b>{round(p_att, dec_f)}</b> | POC: <b>{round(p1, dec_f)}</b> | <span style='color:#f59e0b;'>SL: {round(sl_1, dec_f)}</span> | <span style='color:#06b6d4;'>TP: {round(tp_1, dec_f)}</span></p>
                            <p style='margin-bottom:6px; font-size:15px;'>🏛️ <b>2. Profilo Dall'ATH:</b> <span style='color:{"#22c55e" if is_long_2 else "#ef4444"}; font-weight:bold;'>{'LONG 🟢' if is_long_2 else 'SHORT 🔴'}</span> | Entry: <b>{round(p_att, dec_f)}</b> | POC: <b>{round(p2, dec_f)}</b> | <span style='color:#f59e0b;'>SL: {round(sl_2, dec_f)}</span> | <span style='color:#06b6d4;'>TP: {round(tp_2, dec_f)}</span></p>
                            <p style='margin-bottom:0; font-size:15px;'>⚡ <b>3. Profilo Recente ({period_label}):</b> <span style='color:{"#22c55e" if is_long_3 else "#ef4444"}; font-weight:bold;'>{'LONG 🟢' if is_long_3 else 'SHORT 🔴'}</span> | Entry: <b>{round(p_att, dec_f)}</b> | POC: <b>{round(p3, dec_f)}</b> | <span style='color:#f59e0b;'>SL: {round(sl_3, dec_f)}</span> | <span style='color:#06b6d4;'>TP: {round(tp_3, dec_f)}</span></p>
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
                            
                            d_lf = df_s.index[-1]
                            
                            if len(df_s) > 8:
                                d_li_rischio = df_s.index[-8]
                            else:
                                d_li_rischio = df_s.index
                                
                            if mostra_rr and not np.isnan(atr_att):
                                fig.add_shape(type="rect", x0=d_li_rischio, x1=d_lf, y0=min(p_att, tp), y1=max(p_att, tp), fillcolor=col_z, line=dict(width=0), row=r_idx, col=1)
                            
                            if mostra_poc:
                                fig.add_shape(type="line", x0=df_s.index.min(), x1=d_lf, y0=p_poc, y1=p_poc, line=dict(color="#ef4444", width=2.5), row=r_idx, col=1)
                            
                            fig.add_shape(type="line", x0=df_s.index.min(), x1=d_lf, y0=p_att, y1=p_att, line=dict(color="#a855f7", width=2, dash="dot"), row=r_idx, col=1)
                            
                            if mostra_sl_tp and not np.isnan(atr_att):
                                fig.add_shape(type="line", x0=d_li_rischio, x1=d_lf, y0=sl, y1=sl, line=dict(color="#f59e0b", width=2, dash="dash"), row=r_idx, col=1)
                                fig.add_shape(type="line", x0=d_li_rischio, x1=d_lf, y0=tp, y1=tp, line=dict(color="#06b6d4", width=2, dash="solid"), row=r_idx, col=1)
                                
                            if mostra_trend and r_idx == 3 and len(df_s) > 20:
                                idx_max_assoluto = df_s["High"].idxmax()
                                val_max_assoluto = float(df_s["High"].max())
                                date_max_assoluto = pd.to_datetime(idx_max_assoluto)
                                df_successivo = df_s.loc[date_max_assoluto:]
                                
                                if len(df_successivo) > 5:
                                    punti_swing_lh = []
                                    k_finestra = 3  
                                    
                                    for i in range(k_finestra, len(df_successivo) - k_finestra):
                                        data_corrente = df_successivo.index[i]
                                        val_corrente = float(df_successivo["High"].iloc[i])
                                        max_sinistro = df_successivo["High"].iloc[i - k_finestra : i].max()
                                        max_destro = df_successivo["High"].iloc[i + 1 : i + k_finestra + 1].max()
                                        
                                        if val_corrente >= max_sinistro and val_corrente >= max_destro:
                                            if val_corrente < val_max_assoluto:
                                                punti_swing_lh.append((data_corrente, val_corrente))
                                                
                                    if not punti_swing_lh:
                                        for d_c, r_c in df_successivo.iloc[2:].iterrows():
                                            if float(r_c["High"]) < val_max_assoluto:
                                                punti_swing_lh.append((d_c, float(r_c["High"])))
                                                
                                    miglior_data_swing = None
                                    pendenza_ottimale = -999999.0
                                    
                                    for data_sw, val_sw in punti_swing_lh:
                                        dist_giorni = (data_sw - date_max_assoluto).days
                                        if dist_giorni > 0:
                                            m_trend = (val_sw - val_max_assoluto) / dist_giorni
                                            intersezione_rilevata = False
                                            for verif_idx in range(1, len(df_successivo)):
                                                data_check = df_successivo.index[verif_idx]
                                                giorni_check = (data_check - date_max_assoluto).days
                                                prezzo_teorico_linea = val_max_assoluto + (m_trend * giorni_check)
                                                if float(df_successivo["High"].iloc[verif_idx]) > prezzo_teorico_linea + 0.01:
                                                    intersezione_rilevata = True
                                                    break
                                            if not intersezione_rilevata and m_trend > pendenza_ottimale:
                                                pendenza_ottimale = m_trend
                                                miglior_data_swing = data_sw
                                                
                                    if miglior_data_swing is None and punti_swing_lh:
                                        punti_swing_lh.sort(key=lambda x: x, reverse=True)
                                        miglior_data_swing, miglior_val_swing = punti_swing_lh
                                        dist_giorni = (miglior_data_swing - date_max_assoluto).days
                                        if dist_giorni > 0:
                                            pendenza_ottimale = (miglior_val_swing - val_max_assoluto) / dist_giorni
                                            
                                    if miglior_data_swing is not None:
                                        giorni_totali_grafico = (df_s.index[-1] - date_max_assoluto).days
                                        val_proiezione_destra = val_max_assoluto + (pendenza_ottimale * giorni_totali_grafico)
                                        
                                        fig.add_trace(
                                            grp.Scatter(
                                                x=[date_max_assoluto, df_s.index[-1]], 
                                                y=[val_max_assoluto, val_proiezione_destra],
                                                mode="lines",
                                                line=dict(color="#ffffff", width=2.5, dash="solid"),
                                                name="Trendline Strutturale LH",
                                                showlegend=False
                                            ),
                                            row=r_idx, col=1
                                        )
                            
                            txt_label_grafico = f"📊 ENTRY {dir_n} {round(p_att, 2)}<br>🔸 SL: {round(sl, 2)}<br>🔹 TP: {round(tp, 2)}"
                            fig.add_annotation(
                                x=d_lf, y=p_att,
                                text=txt_label_grafico,
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor="#22c55e" if is_long else "#ef4444",
                                ax=-65,
                                ay=-45 if is_long else 45,
                                align="left",
                                font=dict(color="white", size=9, family="Plus Jakarta Sans"),
                                bgcolor="#22c55e" if is_long else "#ef4444",
                                bordercolor="white",
                                borderwidth=1,
                                borderpad=5,
                                row=r_idx, col=1
                            )
                            
                            txt_leg = f"<b>📊 PROFILO {nm.upper()}</b><br>Setup: {ic} {dir_n}<br>🟣 ENTRY: {round(p_att,2)}<br>🔴 POC: {round(p_poc,2)}<br>🟠 VAH: {round(p_vh,2)}<br>🔵 VAL: {round(p_vl,2)}"
                            fig.add_annotation(xref="paper", yref="paper", x=0.01, y={1:0.98, 2:0.72, 3:0.44}[r_idx], text=txt_leg, showarrow=False, align="left", bgcolor="rgba(20,24,33,0.95)", bordercolor="rgba(242,142,43,0.4)", borderwidth=1.5, borderpad=8, font=dict(color="white         ", size=10))
                        
                        df_recent_ind = df_c.tail(180 if tf_attivo == "1wk" else 365)
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["RSI"], mode="lines", name="RSI", line=dict(color="#a855f7", width=2)), row=4, col=1)
                        fig.add_shape(type="line", x0=df_recent_ind.index.min(), x1=df_recent_ind.index[-1], y0=75, y1=75, line=dict(color="rgba(239, 68, 68, 0.4)", width=1.5, dash="dot"), row=4, col=1)
                        fig.add_shape(type="line", x0=df_recent_ind.index.min(), x1=df_recent_ind.index[-1], y0=25, y1=25, line=dict(color="rgba(34, 197, 94, 0.4)", width=1.5, dash="dot"), row=4, col=1)
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["ATR"], mode="lines", name="ATR", line=dict(color="#10b981", width=2)), row=5, col=1)
                        
                        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False, xaxis3_rangeslider_visible=False, xaxis4_rangeslider_visible=False, xaxis5_rangeslider_visible=False, height=2000, showlegend=False)
                        st.plotly_chart(fig, width="stretch", key=f"chart_{ticker}")
                    else: 
                        st.warning(f"Dati storici insufficienti per {ticker}.")
# ==============================================================================
# --- TAB 2: PARTE 1 - INTERFACCIA UTENTE VERTICALE ORDINATA PER SCOPO ---
# ==============================================================================
with tab2:
    st.subheader("📐 Laboratorio Geometrico: Tracciamento e Backtest Quantitativo")
    st.markdown("Rileva il cambio di momentum tramite lo Z-Score, identifica le strutture di accumulazione e simula gli ingressi operativi sui breakout delle candele Marubozu.")
    
    # Creiamo 3 colonne verticali principali ben distinte per raggruppare i menu per scopo
    col_scopo1, col_scopo2, col_scopo3 = st.columns(3)
    
    # --------------------------------------------------------------------------
    # PANNELLO 1: CONFIGURAZIONE DATI & TIMEFRAME (VERTICALE)
    # --------------------------------------------------------------------------
    with col_scopo1:
        st.markdown("#### 🗂️ 1. Dati & Timeframe")
        geo_ticker = st.text_input("Asset Ticker da analizzare:", value="AAPL", key="geo_tk_input")
        
        geo_periodo = st.selectbox("Orizzonte storico dati:", ["1 Anno", "3 Anni", "5 Anni", "Storico Massimo"], index=0, key="geo_per_sel")
        mappa_periodi_geo = {"1 Anno": "1y", "3 Anni": "3y", "5 Anni": "5y", "Storico Massimo": "max"}
        
        geo_tf_label = st.selectbox("Timeframe delle Candele:", ["Giornaliero (Daily)", "Settimanale (Weekly)", "Mensile (Monthly)"], key="geo_tf_sel")
        geo_tf_attivo = {"Giornaliero (Daily)": "1d", "Settimanale (Weekly)": "1wk", "Mensile (Monthly)": "1mo"}[geo_tf_label]
    
    # --------------------------------------------------------------------------
    # PANNELLO 2: PARAMETRI ALGORITMO GEOMETRICO (VERTICALE)
    # --------------------------------------------------------------------------
    with col_scopo2:
        st.markdown("#### 📐 2. Algoritmo Z-Score")
        geo_finestra = st.slider("Finestra Regressione (Candele base):", min_value=20, max_value=100, value=50, step=5, key="geo_win_sl")
        geo_soglia = st.slider("Soglia Breakout Z-Score:", min_value=1.5, max_value=3.5, value=2.0, step=0.1, key="geo_z_sl")
        st.caption("Determina il distacco balistico dal trend centrale per l'innesco dei GEO-POC.")
    
    # --------------------------------------------------------------------------
    # PANNELLO 3: RISK MANAGEMENT & POSITION SIZING (VERTICALE)
    # --------------------------------------------------------------------------
    with col_scopo3:
        st.markdown("#### 🎯 3. Risk Management & Size")
        geo_capitale = st.number_input("Capitale Operativo ($):", min_value=100, value=10000, step=500, key="geo_cap_input")
        geo_rischio_pct = st.slider("Rischio per Trade (%):", min_value=0.2, max_value=5.0, value=1.0, step=0.1, key="geo_risk_sl")
        
        modello_size = st.radio(
            "Modello di Gestione Taglia:",
            ["Rischio Fisso Frazionario (Consigliato)", "Percentuale Fissa del Capitale", "Leva Finanziaria Costante"],
            index=0, key="geo_modello_size"
        )
        quota_o_leva = st.number_input(
            "Valore quota / Leva moltiplicatore:",
            min_value=0.5, value=25.0 if "Percentuale" in modello_size else 1.0, step=1.0, key="geo_quota_leva"
        )
    
    st.markdown("---")


# ==============================================================================
# --- TAB 2: PARTE 2A - CORE ENGINE QUANTITATIVO MULTI-TIMEFRAME ---
# ==============================================================================
    if st.button("📐 Genera Struttura Geometrica & Avvia Backtest", type="primary", key="geo_btn_start"):
        st.info(f"Elaborazione matriciale e simulazione storica degli ordini per {geo_ticker} in timeframe {geo_tf_label}...")
        
        df_g = yf.download(tickers=geo_ticker, period=mappa_periodi_geo[geo_periodo], interval=geo_tf_attivo, auto_adjust=False, multi_level_index=False, progress=False)
        
        if df_g is not None and len(df_g) > geo_finestra:
            df_g.columns = [str(c).strip() for c in df_g.columns]
            close_series = pd.Series(df_g["Close"].values.flatten(), index=df_g.index).astype(float)
            n_punti = len(df_g)
            
            # Algoritmo Vettorizzato per la Regressione e lo Z-Score dei Residui
            n = geo_finestra
            x = np.arange(n)
            sum_x, sum_x2 = x.sum(), (x**2).sum()
            denominatore = n * sum_x2 - (sum_x**2)
            
            sum_y = close_series.rolling(window=n).sum()
            sum_y2 = (close_series**2).rolling(window=n).sum()
            
            xy_conv = np.convolve(close_series.values, x[::-1], mode='valid')
            sum_xy = pd.Series(np.nan, index=close_series.index)
            sum_xy.iloc[n-1:] = xy_conv
            
            m_series = (n * sum_xy - sum_x * sum_y) / denominatore
            q_series = (sum_x2 * sum_y - sum_x * sum_xy) / denominatore
            prezzi_teorici_series = m_series * n + q_series
            
            mean_x, var_x = sum_x / n, sum_x2 / n - ((sum_x / n)**2)
            mean_y, var_y = sum_y / n, sum_y2 / n - ((sum_y / n)**2)
            cov_xy = sum_xy / n - (mean_x * mean_y)
            
            var_residui = var_y - (2 * m_series * cov_xy) + (m_series**2 * var_x)
            std_residui_series = np.sqrt(np.clip(var_residui, 0.00001, None))
            
            df_g["Z_Score"] = ((close_series - prezzi_teorici_series) / std_residui_series).fillna(0)
            df_g["Accelerazione_Geometrica"] = np.where(df_g["Z_Score"] >= geo_soglia, 1, 0)
            
            # Calcolo dell'ATR utilizzato esclusivamente come stop protettivo dinamico
            tr = pd.concat([df_g["High"] - df_g["Low"], (df_g["High"] - df_g["Close"].shift(1)).abs(), (df_g["Low"] - df_g["Close"].shift(1)).abs()], axis=1).max(axis=1)
            df_g["ATR"] = tr.rolling(window=14).mean().fillna(tr.mean())

            
# ==============================================================================
# --- TAB 2: PARTE 2B - SCANNER STRUTTURALE CON ANCHOR PROFILE SULL'IMPULSO ---
# ==============================================================================
            # Calcolo dei parametri rolling dinamici per identificare la Marubozu
            corpi = (df_g["Close"].astype(float) - df_g["Open"].astype(float)).abs()
            range_totale = df_g["High"].astype(float) - df_g["Low"].astype(float)
            corpo_medio = corpi.rolling(window=20).mean().fillna(range_totale.mean())
            
            df_g["Linea_Protezione_ATR"] = np.nan
            poc_grezzi = []
            linee_bianche_proiettate = [] 
            segnali_di_breakout_storici = {} 
            stato_precedente = 0
            ultimo_index_innesco = -999
            minimo_giorni_distanza = 15 
            
            for i in range(geo_finestra, n_punti):
                stato_attuale = df_g["Accelerazione_Geometrica"].iloc[i]
                
                if stato_attuale == 1 and stato_precedente == 0:
                    start_idx = i
                    data_innesco = df_g.index[start_idx]
                    atr_attuale = float(df_g["ATR"].iloc[start_idx])
                    
                    # --------------------------------------------------------------------------
                    # CORREZIONE BUG: ISOLAMENTO VOLUMETRICO DELL'IMPULSO (FINESTRA 35 CANDELÈ)
                    # --------------------------------------------------------------------------
                    fine_finestra_impulso = min(n_punti, start_idx + 35)
                    df_puro_impulso = df_g.iloc[start_idx : fine_finestra_impulso]
                    df_da_mom_a_oggi = df_g.iloc[start_idx:]
                    
                    # Calcoliamo il POC ancorato solo sulla durata della spinta balistica
                    p_poc, _, _, _, _ = calc_vp(df_puro_impulso)
                    
                    # --------------------------------------------------------------------------
                    # LIVELLO 1: DISÈGNO DELLE LINEE BIANCHE DI RESISTENZA (SEMPRE ATTIVO)
                    # --------------------------------------------------------------------------
                    finestra_lookback = max(0, start_idx - 65)
                    df_periodo_precedente = df_g.iloc[finestra_lookback : start_idx + 1]
                    val_massimo_riferimento = float(df_periodo_precedente["High"].max())
                    idx_data_massimo = df_periodo_precedente["High"].idxmax()
                    
                    data_fine_linea = df_g.index[-1]
                    trovato_breakout = False
                    data_breakout_marubozu = None
                    val_fondo_rounding = float(df_periodo_precedente["Low"].min()) 
                    
                    for j in range(start_idx, n_punti):
                        c_open = float(df_g["Open"].iloc[j])
                        c_close = float(df_g["Close"].iloc[j])
                        c_high = float(df_g["High"].iloc[j])
                        c_low = float(df_g["Low"].iloc[j])
                        
                        if range_candela := (c_high - c_low) > 0 and (dimensione_corpo := (c_close - c_open)) > 0:
                            is_corpo_ampio = dimensione_corpo > (corpo_medio.iloc[j] * 1.05)
                            senza_ombra_sup = (c_high - c_close) / (c_high - c_low) <= 0.22
                            senza_ombra_inf = (c_open - c_low) / (c_high - c_low) <= 0.22
                            is_marubozu = is_corpo_ampio and senza_ombra_sup and senza_ombra_inf
                            
                            if is_marubozu and c_close > val_massimo_riferimento:
                                trovato_breakout = True
                                data_fine_linea = df_g.index[j]
                                data_breakout_marubozu = df_g.index[j]
                                segnali_di_breakout_storici[j] = {
                                    "tipo": "LONG",
                                    "linea_resistenza": val_massimo_riferimento,
                                    "stop_loss_base": val_fondo_rounding
                                }
                                break
                                
                    linee_bianche_proiettate.append({
                        "data_inizio": idx_data_massimo,
                        "data_innesco_z": data_innesco,
                        "data_fine": data_fine_linea,
                        "valore": val_massimo_riferimento,
                        "breakout": trovato_breakout,
                        "data_breakout": data_breakout_marubozu
                    })
                    
                    # --------------------------------------------------------------------------
                    # LIVELLO 2: FILTRO DI PROSSIMITÀ SUI GEO-POC ANCORATI
                    # --------------------------------------------------------------------------
                    if (start_idx - ultimo_index_innesco) >= minimo_giorni_distanza:
                        if p_poc is not None:
                            val_poc_attuale = float(p_poc)
                            accetta_nuovo_poc = True
                            
                            for dt_saved, val_saved in poc_grezzi:
                                if abs(val_poc_attuale - val_saved) <= (1.2 * atr_attuale):
                                    accetta_nuovo_poc = False
                                    break
                            
                            if accetta_nuovo_poc:
                                poc_grezzi.append((data_innesco, val_poc_attuale))
                                ultimo_index_innesco = start_idx
                    
                stato_precedente = stato_attuale
            linee_poc_geometriche = poc_grezzi

# ==============================================================================
# --- TAB 2: PARTE 2C - ENGINE STRATEGICO TRADE SIMULATOR (CANDELA t+1) ---
# ==============================================================================
            capitale_corrente = float(geo_capitale)
            in_posizione = False
            trade_log = []
            
            for idx_c in range(geo_finestra, n_punti):
                data_corrente = df_g.index[idx_c]
                prezzo_apertura = float(df_g["Open"].iloc[idx_c])
                prezzo_high = float(df_g["High"].iloc[idx_c])
                prezzo_low = float(df_g["Low"].iloc[idx_c])
                prezzo_chiusura = float(df_g["Close"].iloc[idx_c])
                atr_corrente = float(df_g["ATR"].iloc[idx_c])
                
                if in_posizione:
                    if trade_corrente["tipo"] == "LONG":
                        livello_trailing_atr = max(livello_trailing_atr, prezzo_chiusura - (2.0 * atr_corrente))
                        df_g.loc[data_corrente, "Linea_Protezione_ATR"] = livello_trailing_atr
                        
                        if prezzo_high >= trade_corrente["tp"]:
                            pnl_lordo = (trade_corrente["tp"] - trade_corrente["prezzo_ingresso"]) * trade_corrente["taglia"]
                            capitale_corrente += pnl_lordo
                            trade_log.append({"Data Ingress": trade_corrente["data"], "Data Uscita": data_corrente.strftime("%d/%m/%Y"), "Tipo": "LONG", "Esito": "TARGET GAIN COMPLETATO", "PnL ($)": round(pnl_lordo, 2), "Capitale ($)": round(capitale_corrente, 2)})
                            in_posizione = False
                        elif prezzo_low <= trade_corrente["sl"]:
                            pnl_lordo = (trade_corrente["sl"] - trade_corrente["prezzo_ingresso"]) * trade_corrente["taglia"]
                            capitale_corrente += pnl_lordo
                            trade_log.append({"Data Ingress": trade_corrente["data"], "Data Uscita": data_corrente.strftime("%d/%m/%Y"), "Tipo": "LONG", "Esito": "STOP LOSS BASE", "PnL ($)": round(pnl_lordo, 2), "Capitale ($)": round(capitale_corrente, 2)})
                            in_posizione = False
                        elif prezzo_low <= livello_trailing_atr:
                            pnl_lordo = (livello_trailing_atr - trade_corrente["prezzo_ingresso"]) * trade_corrente["taglia"]
                            capitale_corrente += pnl_lordo
                            trade_log.append({"Data Ingress": trade_corrente["data"], "Data Uscita": data_corrente.strftime("%d/%m/%Y"), "Tipo": "LONG", "Esito": "PROTEZIONE ATR", "PnL ($)": round(pnl_lordo, 2), "Capitale ($)": round(capitale_corrente, 2)})
                            in_posizione = False
                
                if not in_posizione and (idx_c - 1) in segnali_di_breakout_storici:
                    dati_breakout = segnali_di_breakout_storici[idx_c - 1]
                    
                    if dati_breakout["tipo"] == "LONG":
                        distanza_stop = prezzo_apertura - dati_breakout["stop_loss_base"]
                        
                        if distanza_stop > 0:
                            if modello_size == "Rischio Fisso Frazionario (Consigliato)":
                                rischio_monetario = capitale_corrente * (geo_rischio_pct / 100)
                                taglia_contratti = rischio_monetario / distanza_stop
                            elif modello_size == "Percentuale Fissa del Capitale":
                                controvalore_destinato = capitale_corrente * (quota_o_leva / 100)
                                taglia_contratti = controvalore_destinato / prezzo_apertura
                            elif modello_size == "Leva Finanziaria Costante":
                                controvalore_esposizione = capitale_corrente * quota_o_leva
                                taglia_contratti = controvalore_esposizione / prezzo_apertura
                            
                            if taglia_contratti > 0:
                                livello_take_profit = prezzo_apertura + (3.0 * distanza_stop)
                                trade_corrente = {
                                    "data": data_corrente.strftime("%d/%m/%Y"), "tipo": "LONG", "prezzo_ingresso": prezzo_apertura,
                                    "sl": dati_breakout["stop_loss_base"], "tp": livello_take_profit, "taglia": taglia_contratti
                                }
                                livello_trailing_atr = prezzo_apertura - (2.0 * atr_corrente)
                                df_g.loc[data_corrente, "Linea_Protezione_ATR"] = livello_trailing_atr
                                in_posizione = True

# ==============================================================================
# --- TAB 2: PARTE 3A - GRAPHIC RENDERING A ASSI X CONDIVISI (SHARED ZOOM) ---
# ==============================================================================
            st.markdown(f"##### 📊 Dashboard Grafica Integrata con Assi Temporali Sincronizzati (Zoom Linkato)")
            
            fig_geo = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.08, 
                row_heights=[0.70, 0.30]
            )
            
            data_oggi = df_g.index[-1]
            p_attuale = float(close_series.iloc[-1])
            
            fig_geo.add_trace(grp.Candlestick(
                x=df_g.index, open=df_g["Open"].astype(float), high=df_g["High"].astype(float),
                low=df_g["Low"].astype(float), close=df_g["Close"].astype(float), name=geo_ticker
            ), row=1, col=1)
            
            if "Linea_Protezione_ATR" in df_g.columns and not df_g["Linea_Protezione_ATR"].isna().all():
                fig_geo.add_trace(grp.Scatter(
                    x=df_g.index, y=df_g["Linea_Protezione_ATR"], mode="lines",
                    line=dict(color="#d946ef", width=2, dash="dot"), name="Protezione Trailing ATR"
                ), row=1, col=1)
            
            for idx, linea in enumerate(linee_bianche_proiettate):
                mostra_in_legenda = True if idx == 0 else False
                fig_geo.add_trace(grp.Scatter(
                    x=[linea["data_inizio"], linea["data_fine"]], y=[linea["valore"], linea["valore"]],
                    mode="lines", line=dict(color="#ffffff", width=2.5, dash="dash"),
                    name="Resistenza Massimo Periodo", showlegend=mostra_in_legenda
                ), row=1, col=1)
                
                if linea["breakout"]:
                    fig_geo.add_trace(grp.Scatter(
                        x=[linea["data_breakout"]], y=[linea["valore"]], mode="markers",
                        marker=dict(color="#d946ef", size=12, symbol="circle-open", line=dict(width=3)),
                        name="Breakout Marubozu Rilevato", showlegend=mostra_in_legenda
                    ), row=1, col=1)
            
            for idx, (data_start, valore_poc) in enumerate(linee_poc_geometriche):
                fig_geo.add_trace(grp.Scatter(
                    x=[data_start, data_oggi], y=[valore_poc, valore_poc], mode="lines",
                    showlegend=False, line=dict(color="#f29e1f", width=2.5, dash="solid")
                ), row=1, col=1)
                fig_geo.add_annotation(
                    x=data_start, y=valore_poc, text=f"GEO-POC {round(valore_poc, 2)}",
                    showarrow=False, yshift=8, xanchor="left",
                    font=dict(color="#f29e1f", size=10, family="Plus Jakarta Sans", weight="bold"),
                    bgcolor="rgba(15, 23, 42, 0.85)", row=1, col=1
                )

# ==============================================================================
# --- TAB 2: PARTE 3B - GRAPHIC SÈTUP Z-SCORE, TABELLA TRADE & NOTE ---
# ==============================================================================
            # 2. Agganciamo l'oscillatore dello Z-Score dei residui sulla riga 2
            fig_geo.add_trace(grp.Scatter(
                x=df_g.index, y=df_g["Z_Score"], mode="lines", name="Z-Score Momentum", line=dict(color="#38bdf8", width=1.5)
            ), row=2, col=1)
            
            # --- PROTEZIONE ANCORAGGIO ASSI (yref="y2"): Mantiene visibili le linee tratteggiate ---
            # Linea della soglia utente dinamica
            fig_geo.add_shape(type="line", x0=df_g.index[0], x1=data_oggi, y0=geo_soglia, y1=geo_soglia, 
                              line=dict(color="#ef4444", width=1.5, dash="dash"), row=2, col=1, yref="y2")
            
            # Linea tratteggiata sottile VERDE a +2
            fig_geo.add_shape(type="line", x0=df_g.index[0], x1=data_oggi, y0=2.0, y1=2.0, 
                              line=dict(color="#22c55e", width=1.2, dash="dash"), row=2, col=1, yref="y2")
            
            # Linea centrale dello zero
            fig_geo.add_shape(type="line", x0=df_g.index[0], x1=data_oggi, y0=0, y1=0, 
                              line=dict(color="rgba(255,255,255,0.2)", width=1, dash="solid"), row=2, col=1, yref="y2")
            
            # Linea tratteggiata sottile ROSSA a -2
            fig_geo.add_shape(type="line", x0=df_g.index[0], x1=data_oggi, y0=-2.0, y1=-2.0, 
                              line=dict(color="#ef4444", width=1.2, dash="dash"), row=2, col=1, yref="y2")
            
            # Configurazione del layout unico: disattiviamo i range slider nativi che creerebbero conflitti sullo zoom
            fig_geo.update_layout(
                template="plotly_dark", 
                height=700, 
                margin=dict(l=20, r=20, t=10, b=10),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # Applichiamo i limiti e le etichette per asse y1 e y2 in modo coordinato
            fig_geo.update_yaxes(title_text=f"Prezzo {geo_ticker} ($)", row=1, col=1)
            fig_geo.update_yaxes(title_text="Deviazioni Std (Z)", range=[-5.5, 5.5], row=2, col=1)
            fig_geo.update_xaxes(rangeslider_visible=False, row=1, col=1)
            fig_geo.update_xaxes(rangeslider_visible=False, row=2, col=1)
            
            # Inviamo l'unico grafico combinato a Streamlit
            st.plotly_chart(fig_geo, use_container_width=True, key="geo_combined_shared_chart")
            
            # --- REPORT PRESTAZIONI FINANZIARIE ---
            st.markdown("### 📊 Performance Ledger: Backtest Strategia Marubozu Breakout")
            st.info(f"⚙️ **Modello di Taglia Attivo nel Simulatore:** {modello_size}")
            if trade_log:
                df_report = pd.DataFrame(trade_log)
                operazioni_vincenti = df_report[df_report["PnL ($)"] > 0]
                win_rate = (len(operazioni_vincenti) / len(df_report)) * 100
                ritorno_percentuale = ((capitale_corrente - geo_capitale) / geo_capitale) * 100
                
                perf_col1, perf_col2, perf_col3 = st.columns(3)
                with perf_col1:
                    st.metric("Capitale Finale Bilancio", f"$ {round(capitale_corrente, 2)}", f"{round(ritorno_percentuale, 2)} % Ritorno Netto")
                with perf_col2:
                    st.metric("Affidabilità (Win Rate)", f"{round(win_rate, 2)} %", f"{len(operazioni_vincenti)} su {len(df_report)} Trades")
                with perf_col3:
                    st.metric("Uscita Media Trailing ATR", f"Fattore 2.0x ATR", "Incrocio Volatilità")
                st.dataframe(df_report, use_container_width=True)
            else:
                st.warning("⚠️ Nessun trade registrato nel periodo storico selezionato.")
                
            # Tabella di riepilogo dello stato strutturale dei nodi
            if linee_poc_geometriche:
                st.markdown("##### 📋 Stato dei Livelli di Supporto/Resistenza Geometrici Rilevati")
                dati_tabella_geo = []
                for dt_p, val_p in linee_poc_geometriche:
                    dist_pct = ((p_attuale - val_p) / val_p) * 100
                    stato_nodo = "🟢 SOPRA (Supporto)" if dist_pct >= 0 else "🔴 SOTTO (Resistenza)"
                    dati_tabella_geo.append({
                        "Data Rilevazione Segnale": dt_p.strftime("%d/%m/%Y"), "Prezzo del GEO-POC": f"$ {round(val_p, 2)}",
                        "Distanza Percentuale Corrente": f"{round(dist_pct, 2)} %", "Stato Strutturale": stato_nodo
                    })
                st.dataframe(pd.DataFrame(dati_tabella_geo), use_container_width=True)
                
            # --- NOTA METODOLOGICA DIDATTICA COPIABILE ---
            st.markdown("---")
            st.markdown("### 🔏 Note Metodologiche sulla Gestione del Rischio e Position Sizing")
            st.markdown(f"""
            La dashboard implementa un motore matematico di **Risk Management frazionario avanzato**. Quando si avvia un trade, l'esposizione non è mai casuale ma risponde a regole quantitative precise dipendenti dal modello scelto:
            
            1. 📊 **Modello Rischio Fisso Frazionario (Consigliato):**
               Il capitale allocato sul mercato è inversamente proporzionale all'ampiezza della struttura geometrica. 
               * **Formula:** $\\text{{Contratti}} = \\frac{{\\text{{Capitale}} \\times \\text{{Rischio \\%}}}}{{\\text{{Prezzo Ingresso}} - \\text{{Stop Loss (Base Rounding)}}}}$
               * *Effetto:* Se il rounding/scodella è stretto, il sistema compra più contratti; se è molto largo, ne compra pochissimi. In questo modo, l'eventuale perdita sul conto sarà sempre **esattamente pari al {geo_rischio_pct}\\% del capitale**, bloccando la varianza statistica del portafoglio.
            
            2. 💰 **Modello Percentuale Fissa del Capitale:**
               Il sistema investe una frazione costante del portafoglio (es. il **{quota_o_leva if "Percentuale" in modello_size else 25.0}\\%**) sul valore nozionale del trade, indipendentemente da dove sia posizionato lo Stop Loss. La perdita monetaria varierà a seconda della volatilità dell'asset.
            
            3. ⚡ **Modello Leva Finanziaria Costante:**
               Il controvalore totale del trade viene impostato como moltiplicatore lineare del capitale operativo disponibile (es. Leva **{quota_o_leva if "Leva" in modello_size else 1.0}x**). Permette di simulare l'esposizione costante tipica dei contratti Future o dei derivati marginati.
            """)
            st.success("📐 Mappatura e report del dimensionamento completati con successo con assi X sincronizzati.")


# ==============================================================================
# --- TAB 3: BREAKOUT TREND-FOLLOWING (MOTORE DI BACKTEST STRATEGICO CON GEO-Z) ---
# ==============================================================================
with tab3:
    st.subheader("⚙️ Simulatore Quantitativo: Breakout Trend-Following")
    st.markdown("Esegue il backtest della strategia algoritmica entrando sui breakout balistici dello Z-Score ed uscendo sui target o all'esaurimento della spinta.")
    
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        bt_ticker = st.text_input("Inserisci un singolo Ticker da testare:", value="AAPL", key="bt_tk_in")
        capitale_iniziale = st.number_input("Capitale iniziale ($):", min_value=100, value=10000, step=500, key="bt_cap_in")
    with b_col2:
        bt_periodo = st.selectbox("Orizzonte temporale dei dati:", ["1 Anno", "3 Anni", "5 Anni", "Storico Massimo"], key="bt_per_in")
        mappa_periodi = {"1 Anno": "1y", "3 Anni": "3y", "5 Anni": "5y", "Storico Massimo": "max"}
        finestra_regressione = st.slider("Finestra della Regressione Lineare (Giorni di base):", min_value=20, max_value=100, value=50, step=5, key="bt_win_sl")
    with b_col3:
        soglia_zscore = st.slider("Soglia Z-Score per Accelerazione (Distacco Balistico):", min_value=1.5, max_value=3.5, value=2.0, step=0.1, key="bt_z_sl")
        comun_fee = st.number_input("Commissioni per singolo eseguito ($):", min_value=0.0, value=1.99, step=0.5, key="bt_fee_in")
        rischio_trade = 1.0  # Rischio fisso percentuale per trade

    if st.button("🚀 Avvia Backtest Algoritmico", type="primary", key="bt_btn_start"):
        st.info(f"Calcolo vettoriale veloce ed esecuzione ordini storici per {bt_ticker}...")
        df_bt = yf.download(tickers=bt_ticker, period=mappa_periodi[bt_periodo], interval="1d", auto_adjust=False, multi_level_index=False, progress=False)
        
        if df_bt is not None and len(df_bt) > finestra_regressione:
            df_bt.columns = [str(c).strip() for c in df_bt.columns]
            close_series = pd.Series(df_bt["Close"].values.flatten(), index=df_bt.index).astype(float)
            n_punti = len(df_bt)
            
            # Formula vettorizzata veloce per lo Z-Score
            n = finestra_regressione
            x = np.arange(n)
            sum_x, sum_x2 = x.sum(), (x**2).sum()
            denominatore = n * sum_x2 - (sum_x**2)
            
            sum_y = close_series.rolling(window=n).sum()
            sum_y2 = (close_series**2).rolling(window=n).sum()
            
            xy_conv = np.convolve(close_series.values, x[::-1], mode='valid')
            sum_xy = pd.Series(np.nan, index=close_series.index)
            sum_xy.iloc[n-1:] = xy_conv
            
            m_series = (n * sum_xy - sum_x * sum_y) / denominatore
            q_series = (sum_x2 * sum_y - sum_x * sum_xy) / denominatore
            prezzi_teorici_series = m_series * n + q_series
            
            mean_x, var_x = sum_x / n, sum_x2 / n - ((sum_x / n)**2)
            mean_y, var_y = sum_y / n, sum_y2 / n - ((sum_y / n)**2)
            cov_xy = sum_xy / n - (mean_x * mean_y)
            
            var_residui = var_y - (2 * m_series * cov_xy) + (m_series**2 * var_x)
            std_residui_series = np.sqrt(np.clip(var_residui, 0.00001, None))
            
            df_bt["Z_Score"] = ((close_series - prezzi_teorici_series) / std_residui_series).fillna(0)
            df_bt["Accelerazione_Geometrica"] = np.where(df_bt["Z_Score"] >= soglia_zscore, 1, 0)
            
            # Calcolo dei POC estratti da ogni segnale fino a oggi
            linee_poc_momentum = []
            stato_precedente = 0
            for i in range(finestra_regressione, n_punti):
                stato_attuale = df_bt["Accelerazione_Geometrica"].iloc[i]
                if stato_attuale == 1 and stato_precedente == 0:
                    start_idx = i
                    df_da_momentum_a_oggi = df_bt.iloc[start_idx:]
                    p_poc, _, _, _, _ = calc_vp(df_da_momentum_a_oggi)
                    if p_poc is not None:
                        linee_poc_momentum.append((df_bt.index[start_idx], p_poc))
                stato_precedente = stato_attuale

            # Simulatore dei Trade Storici
            capitale = capitale_iniziale
            in_posizione = False
            prezzo_ingresso = 0
            trade_history = []

            for i in range(finestra_regressione, n_punti):
                riga_attuale = df_bt.iloc[i]
                prezzo_corrente = float(riga_attuale["Close"])
                data_corrente = df_bt.index[i]
                trigger_mom = df_bt["Accelerazione_Geometrica"].iloc[i] == 1

                if not in_posizione and trigger_mom:
                    df_storico_finora = df_bt.iloc[:i]
                    p_poc, p_vh, p_vl, _, _ = calc_vp(df_storico_finora)
                    if p_poc is None: continue
                    
                    prezzo_ingresso = prezzo_corrente
                    intervallo_prezzo = float(riga_attuale.get("High", prezzo_corrente) - riga_attuale.get("Low", prezzo_corrente))
                    if intervallo_prezzo == 0: intervallo_prezzo = prezzo_corrente * 0.01
                    livello_sl = prezzo_ingresso - (1.5 * intervallo_prezzo)
                    livello_tp = prezzo_ingresso + (3.0 * abs(prezzo_ingresso - livello_sl))

                    if livello_sl > 0 and prezzo_ingresso > livello_sl:
                        in_posizione = True
                        size_contratti = (capitale * (rischio_trade / 100)) / (prezzo_ingresso - livello_sl)
                
                elif in_posizione:
                    high_g, low_g = float(riga_attuale["High"]), float(riga_attuale["Low"])
                    uscito, p_chiusura = False, 0
                    z_attuale = df_bt["Z_Score"].iloc[i]
                    
                    if low_g <= livello_sl: uscito, p_chiusura = True, livello_sl
                    elif high_g >= livello_tp: uscito, p_chiusura = True, livello_tp
                    elif z_attuale < 0: uscito, p_chiusura = True, prezzo_corrente

                    if uscito:
                        pnl = (p_chiusura - prezzo_ingresso) * size_contratti - (comun_fee * 2)
                        capitale += pnl
                        trade_history.append({"Data": data_corrente.strftime("%d/%m/%Y"), "Tipo": "GEO LONG", "PnL ($)": round(pnl, 2), "Capitale": round(capitale, 2)})
                        in_posizione = False

            # Rendering del Grafico di Backtest
            st.markdown(f"##### 📊 Grafico di Backtest & Livelli POC Semplificati")
            fig_bt = grp.Figure()
            fig_bt.add_trace(grp.Candlestick(
                x=df_bt.index, open=df_bt["Open"].astype(float), high=df_bt["High"].astype(float),
                low=df_bt["Low"].astype(float), close=df_bt["Close"].astype(float), name=bt_ticker
            ))
            
            data_oggi = df_bt.index[-1]
            for idx, (data_start, valore_poc) in enumerate(linee_poc_momentum):
                fig_bt.add_trace(grp.Scatter(
                    x=[data_start, data_oggi], y=[valore_poc, valore_poc], mode="lines",
                    showlegend=False, line=dict(color="#f29e1f", width=2.5, dash="solid")
                ))
                fig_bt.add_annotation(
                    x=data_start, y=valore_poc, text=f"POC {round(valore_poc, 2)}",
                    showarrow=False, yshift=8, xanchor="left",
                    font=dict(color="#f29e1f", size=10, family="Plus Jakarta Sans", weight="bold"),
                    bgcolor="rgba(15, 23, 42, 0.85)"
                )
            fig_bt.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=550)
            st.plotly_chart(fig_bt, use_container_width=True, key="bt_strat_chart")
            
            # Statistiche e log finale delle performance
            st.subheader("📊 Performance Engine Geometrico")
            if trade_history:
                df_trades = pd.DataFrame(trade_history)
                win_rate = round((len(df_trades[df_trades["PnL ($)"] > 0]) / len(df_trades)) * 100, 2)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Ritorno Totale", f"{round(((capitale - capitale_iniziale) / capitale_iniziale) * 100, 2)} %")
                c2.metric("Win Rate", f"{win_rate} %")
                c3.metric("Capitale Finale", f"$ {round(capitale, 2)}")
                st.dataframe(df_trades, use_container_width=True)
            else:
                st.warning("Nessun trade registrato. Modifica la tolleranza dello Z-Score.")
        else:
            st.error("Dati storici insufficienti.")

# ==========================================
# --- TAB 4: LIVE ALERTS STRATEGICI ---
# ==========================================
with tab4:
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

# ==========================================
# TAB 5: ANALISI GARCH ---
# ==========================================
with tab5:
    st.subheader("📈 Studio ed Analisi Quantitativa della Volatilità (GARCH)")
    st.markdown("Configura i parametri sottostanti per modellare i cluster di volatilità sui rendimenti finanziari logaritmici.")
    
    g_col1, g_col2, g_col3 = st.columns(3)
    with g_col1:
        garch_ticker = st.text_input("Inserisci Ticker da analizzare (es. AAPL, BTC-USD, ^GSPC):", value="AAPL", key="garch_tk_input")
        garch_periodo = st.selectbox("Orizzonte storico dati:", ["1 Anno", "3 Anni", "5 Anni", "10 Anni", "Storico Massimo"], index=1, key="garch_per_sel")
        mappa_periodi_garch = {"1 Anno": "1y", "3 Anni": "3y", "5 Anni": "5y", "10 Anni": "10y", "Storico Massimo": "max"}
    with g_col2:
        param_p = st.slider("Ordine Autoregressivo - Residui Quadrati (p):", min_value=1, max_value=5, value=1, key="garch_p")
        param_q = st.slider("Ordine Media Mobile - Volatilità Storica (q):", min_value=1, max_value=5, value=1, key="garch_q")
    with g_col3:
        mod_type = st.selectbox("Variante Modello GARCH:", ["Standard GARCH", "GJR-GARCH (Asimmetrico)", "EGARCH"], index=0, key="garch_type")
    # --- BLOCCO INFORMATIVO DINAMICO IN BASE ALLA VARIANTE SELEZIONATA ---
    st.markdown("---")
    if mod_type == "Standard GARCH":
        st.info(f"""
        ℹ️ **Significato del Modello: Standard GARCH ({param_p}, {param_q}) [Simmetrico]**
        * **Natura:** È il modello base simmetrico. Assume che la volatilità futura dipenda solo dall'*intensità* degli shock passati e non dal loro segno (+ o -).
        * **A cosa servono i parametri scelti:**
            * **p = {param_p} (Residui Quadrati):** Il modello analizza gli ultimi {param_p} giorni di shock/notizie di mercato per calcolare la reattività immediata della volatilità.
            * **q = {param_q} (Volatilità Storica):** Il modello analizza gli ultimi {param_q} giorni di volatilità passata per determinare la persistenza a lungo termine della stessa.
        * **Funzionamento:** Un rialzo del +5% e un crollo del -5% hanno lo stesso identico impatto sulla volatilità di domani.
        """)
    elif mod_type == "GJR-GARCH (Asimmetrico)":
        st.info(f"""
        ℹ️ **Significato del Modello: GJR-GARCH ({param_p}, {param_q}) [Asimmetrico a Soglia]**
        * **Natura:** È un modello asimmetrico che cattura l'**effetto leva** (*leverage effect*). Nei mercati finanziari, i crolli generano molto più panico e volatilità rispetto ai rialzi.
        * **A cosa servono i parametri scelti:**
            * **p = {param_p} (Residui Quadrati):** Determina per quanti giorni di borsa passati ({param_p}) gli shock di prezzo continuano a influenzare la varianza.
            * **q = {param_q} (Volatilità Storica):** Gestisce la memoria storica della volatilità per {param_q} periodi, modellando la tendenza dei mercati a raggruppare i periodi di forte turbolenza.
        * **Funzionamento:** Attiva un parametro aggiuntivo (*Gamma*) *solo* quando i rendimenti passati sono negativi. Se il mercato crolla, l'impatto si somma rendendo il picco di volatilità molto più ripido.
        """)
    elif mod_type == "EGARCH":
        st.info(f"""
        ℹ️ **Significato del Modello: EGARCH ({param_p}, {param_q}) [Exponential GARCH]**
        * **Natura:** Modella il *logaritmo naturale* della volatilità condizionale. È una variante asimmetrica esponenziale altamente flessibile.
        * **A cosa servono i parametri scelti:**
            * **p = {param_p} (Residui Quadrati):** Definisce l'ampiezza della finestra temporale ({param_p} giorni) in cui l'asimmetria delle notizie (buone o cattive) modella la curva logaritmica.
            * **q = {param_q} (Volatilità Storica):** Regola la velocità di decadimento o persistenza della memoria della volatilità passata per gli ultimi {param_q} giorni.
        * **Funzionamento:** Esprime l'asimmetria senza soglie rigide e, grazie alla forma logaritmica, garantisce matematicamente che la volatilità stimata sia sempre positiva, evitando fallimenti di calcolo su asset estremi.
        """)
    st.markdown("---")
    if st.button("📊 Elabora Modello Volatilità", type="primary", key="garch_btn_start"):
        st.info(f"Recupero dati storici in corso per {garch_ticker}...")
        df_g = yf.download(tickers=garch_ticker, period=mappa_periodi_garch[garch_periodo], interval="1d", auto_adjust=False, multi_level_index=False, progress=False)
        
        if df_g is not None and len(df_g) > 100:
            df_g.columns = [str(c).strip() for c in df_g.columns]
            
            # Calcolo dei rendimenti logaritmici percentuali
            df_g['Returns'] = 100 * np.log(df_g['Close'].astype(float) / df_g['Close'].astype(float).shift(1))
            df_g = df_g.dropna()
            
            with st.spinner("Calcolo dei coefficienti di eteroschedasticità..."):
                try:
                    # CONFIGURAZIONE STRUTTURALE ESATTA PER LA LIBRERIA ARCH
                    if mod_type == "Standard GARCH":
                        mod = arch_model(df_g['Returns'], p=param_p, q=param_q, vol='GARCH', dist='normal')
                    elif mod_type == "GJR-GARCH (Asimmetrico)":
                        # Imposta la componente asimmetrica o=1 richiesta dal GJR
                        mod = arch_model(df_g['Returns'], p=param_p, o=1, q=param_q, vol='GARCH', dist='normal')
                    elif mod_type == "EGARCH":
                        mod = arch_model(df_g['Returns'], p=param_p, q=param_q, vol='EGARCH', dist='normal')
                        
                    res_garch = mod.fit(disp='off')
                    
                    # Estrazione e annualizzazione della volatilità condizionale (base 252 giorni trading)
                    cond_vol_annualizzata = res_garch.conditional_volatility * np.sqrt(252)
                    
                    # --- GRAFICO 1: SOVRAPPOSIZIONE PREZZO AZIONE + VOLATILITÀ GARCH (DUE ASSI Y) ---
                    st.markdown(f"##### 📊 Analisi di Correlazione: Prezzo di Chiusura vs Volatilità Condizionale GARCH")
                    
                    fig_combined = grp.Figure()
                    fig_combined.add_trace(grp.Scatter(
                        x=df_g.index, 
                        y=df_g['Close'].astype(float), 
                        mode='lines', 
                        name=f'Prezzo Chiusura ({garch_ticker})', 
                        line=dict(color='#38bdf8', width=2)
                    ))
                    fig_combined.add_trace(grp.Scatter(
                        x=df_g.index, 
                        y=cond_vol_annualizzata, 
                        mode='lines', 
                        name=f'Volatilità Annualizzata {mod_type} (%)', 
                        line=dict(color='#f43f5e', width=1.75),
                        yaxis='y2'
                    ))
                    
                    fig_combined.update_layout(
                        template="plotly_dark",
                        height=450,
                        margin=dict(l=20, r=20, t=10, b=20),
                        xaxis_rangeslider_visible=False,
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        xaxis=dict(gridcolor='rgba(51, 65, 85, 0.25)'),
                        yaxis=dict(
                            title=dict(text=f"Prezzo {garch_ticker} (USD)", font=dict(color="#38bdf8")),
                            tickfont=dict(color="#38bdf8"),
                            gridcolor='rgba(51, 65, 85, 0.25)'
                        ),
                        yaxis2=dict(
                            title=dict(text="Volatilità Condizionale GARCH (%)", font=dict(color="#f43f5e")),
                            tickfont=dict(color="#f43f5e"),
                            anchor="x",
                            overlaying="y",
                            side="right",
                            gridcolor='rgba(0, 0, 0, 0)'
                        )
                    )
                    st.plotly_chart(fig_combined, use_container_width=True, key="garch_combined_chart")
                    
                    st.markdown("---")
                    # --- GRAFICO 2: RENDIMENTI LOGARITMICI A TOTALE ESTENSIONE ORIZZONTALE ---
                    st.markdown("##### 📉 Rendimenti Logaritmici Giornalieri (%)")
                    
                    fig_returns = grp.Figure()
                    fig_returns.add_trace(grp.Scatter(
                        x=df_g.index, 
                        y=df_g['Returns'], 
                        mode='lines', 
                        name='Rendimenti %', 
                        line=dict(color='#818cf8', width=1)
                    ))
                    
                    fig_returns.update_layout(
                        template="plotly_dark",
                        height=280,
                        margin=dict(l=20, r=20, t=10, b=20),
                        xaxis_rangeslider_visible=False,
                        showlegend=False,
                        xaxis=dict(gridcolor='rgba(51, 65, 85, 0.25)'),
                        yaxis=dict(
                            title="Variazione (%)",
                            gridcolor='rgba(51, 65, 85, 0.25)'
                        )
                    )
                    st.plotly_chart(fig_returns, use_container_width=True, key="garch_returns_chart")
                    
                    st.markdown("---")
                    
                    # --- GUIDA ALL'INTERPRETAZIONE DEI GRAFICI E DEI RENDIMENTI (DINAMICA PER TICKER) ---
                    st.markdown(f"### 📋 Funzione dei Rendimenti Logaritmici su {garch_ticker}")
                    st.markdown(f"""
                    Avere il grafico dei **Rendimenti Logaritmici Giornalieri (%)** posizionato sotto quello della volatilità condizionale è fondamentale. Questo grafico serve a **isolare e misurare la pura variazione percentuale giornaliera del prezzo**, depurandola dall'effetto della crescita di lungo periodo (trend).
                    
                    Analizzando il grafico generato sul titolo **{garch_ticker}**, la sua funzione si esprime in tre concetti operativi e statistici chiave:
                    
                    1. 🔍 **Visualizzazione immediata dei "Cluster di Volatilità"**
                       Se guardi l'asse temporale in modo verticale, noterai una corrispondenza millimetrica: ogni volta che nel grafico inferiore i rendimenti logaritmici subiscono delle oscillazioni violentissime verso l'alto o verso il basso, nel grafico superiore la linea rossa del GARCH schizza istantaneamente verso l'alto. Il grafico dei rendimenti mostra visivamente il phenomenon per cui *la forte volatilità tende a seguire altra forte volatilità*, mentre i periodi di calma tendono a raggrupparsi insieme.
                    
                    2. ⚡ **Identificazione visiva delle Anomalie (Shock di Mercato)**
                       Il prezzo di un asset non si muove in modo lineare. Il grafico dei rendimenti logaritmici stabilisce una *"linea dello zero"* ideale:
                       * I movimenti ordinari oscillano costantemente in una fascia stretta (solitamente tra il -5% e il +5%).
                       * Le anomalie statistiche (i cosiddetti *"cigni neri"* o shock da trimestrali/crisi macroeconomiche) si muovono come fulmini isolati che tagliano bruscamente il grafico. Il modello GARCH utilizza esattamente l'ampiezza al quadrato di questi "fulmini" (i residui) per calcolare quanta energia e panico si stanno accumulando sul titolo.
                    
                    3. 📐 **Perché si usano i rendimenti "Logaritmici" invece di quelli semplici?**
                       In econometria finanziaria si preferisce calcolare il rendimento come $100 \\times \\ln(Prezzo_t / Prezzo_{{t-1}})$ per due motivi fondamentali:
                       * **Stazionarietà:** I prezzi nel lungo periodo possono passare da valori molto bassi a cifre importanti. Se analizzassimo le variazioni in dollari o in unità assolute, i movimenti recenti sembrerebbero enormi e quelli passati invisibili. Il rendimento logaritmico rende i dati confrontabili nel tempo: una variazione percentuale registrata all'inizio dello storico ha lo stesso peso e la stessa rilevanza statistica di una registrata oggi.
                       * **Simmetria e Additività:** Se un titolo perde il 50% e poi guadagna il 50%, con il calcolo semplice ti ritroveresti a -25% dal prezzo iniziale. Con i rendimenti logaritmici, le variazioni sono simmetriche e perfettamente sommabili nel tempo, il che permette al modello GARCH di non subire distorsioni matematiche durante il calcolo della varianza condizionale.
                    """)
                    
                except Exception as ex:
                    st.error(f"Errore durante la convergenza del modello GARCH: {ex}")
        else:
            st.warning("Dati storici insufficienti. Prova ad estendere l'orizzonte temporale o verifica il ticker.")
