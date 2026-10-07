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
# ==============================================================================
# 1. CONFIGURAZIONI E DATABASE PANIERI (VERSIONE ESTESA MID/SMALL CAP + CRYPTO)
# ==============================================================================

T_ID = "2072895073"
TESTA_INTERNET = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
}

SP500_FULL = (
    "MMM,AOS,ABT,ABBV,ACN,ADBE,AMD,AES,AFL,A,APD,ABNB,AKAM,ALB,ARE,ALGN,ALLE,LNT,ALL,GOOGL,GOOG,MO,AMZN,AMCR,AEE,"
    "AEP,AXP,AIG,AMT,AWK,AMP,AME,AMGN,APH,ADI,AON,APA,APO,AAPL,AMAT,APP,APTV,ACGL,ADM,ARES,ANET,AJG,AIZ,T,ATO,ADSK,"
    "ADP,AZO,AVY,AXON,BKR,BALL,BAC,BAX,BDX,BRK.B,BBY,TECH,BIIB,BLK,BX,BE,BNY,BA,BKNG,BSX,BMY,AVGO,BR,BRO,BF.B,BG,"
    "BXP,CHRW,CDNS,CPT,COF,CAH,CCL,CARR,CVNA,CASY,CAT,CBOE,CBRE,CDW,COR,CNC,CNP,CF,CRL,SCHW,CHTR,CVX,CMG,CB,CHD,"
    "CIEN,CI,CINF,CTAS,CSCO,C,CFG,CLX,CME,CMS,KO,CTSH,COHR,COIN,CL,CMCSA,FIX,COP,ED,STZ,CEG,COO,CPRT,GLW,CPAY,CTVA,"
    "CSGP,COST,CRH,CRWD,CCI,CSX,CMI,CVS,DHR,DRI,DDOG,DVA,DECK,DE,DELL,DAL,DVN,DXCM,FANG,DLR,DG,DLTR,D,DPZ,DASH,DOV,"
    "DOW,DHI,DTE,DUK,DD,ETN,EBAY,ECHO,ECL,EIX,EW,ELV,EME,EMR,ETR,EOG,EQT,EFX,EQIX,ERIE,ESS,EL,EG,EVRG,ES,EXC,EXPE,"
    "EXPD,EXR,XOM,FFIV,FDS,FICO,FAST,FRT,FDX,FERG,FIS,FITB,FSLR,FE,FI,FLEX,F,FTNT,FTV,FOXA,FOX,BEN,FCX,"
    "GRMN,IT,GE,GEHC,GEV,GEN,GNRC,GD,GIS,GM,GPC,GILD,GPN,GL,GDDY,GS,HAL,HIG,HAS,HCA,DOC,HSIC,HSY,HPE,HLT,HD,HON,HRL,"
    "HST,HWM,HUBB,HUM,HBAN,HII,IBM,IEX,IDXX,ITW,ILMN,INCY,IR,PODD,INTC,IBKR,ICE,IFF,IP,INTU,ISRG,IVZ,INVH,IQV,"
    "IRM,JBHT,JBL,JKHY,J,JNJ,JCI,JPM,KVUE,KDP,KEY,KEYS,KMB,KIM,KMI,KKR,KLAC,KHC,KR,LHX,LH,LRCX,LVS,LDOS,LEN,LII,LLY,"
    "LIN,LYV,LMT,L,LOW,LULU,LITE,LYB,MTB,MPC,MAR,MRSH,MLM,MRVL,MAS,MA,MKC,MCD,MCK,MDT,MRK,META,MET,MTD,MGM,MCHP,MU,"
    "MSFT,MAA,MRNA,MDLZ,MPWR,MNST,MCO,MS,MOS,MSI,MSCI,NDAQ,NTAP,NFLX,NEM,NWSA,NWS,NEE,NKE,NI,NDSN,NSC,NTRS,NOC,NCLH,"
    "NRG,NUE,NVDA,NVR,NXPI,ORLY,OXY,ODFL,OMC,ON,OKE,ORCL,OTIS,PCAR,PKG,PLTR,PANW,PSKY,PH,PAYX,PYPL,PNR,PEP,PFE,PCG,"
    "PM,PSX,PNW,PNC,PPG,PPL,PFG,PG,PGR,PLD,PRU,PEG,PTC,PSA,PHM,PWR,QCOM,DGX,RL,RJF,RDDT,RTX,O,REG,REGN,RF,RSG,"
    "RMD,RVTY,HOOD,ROK,ROL,ROP,ROST,RCL,SPGI,CRM,SBAC,SLB,STX,SRE,NOW,SHW,SPG,SWKS,SJM,SW,SNA,SOLV,SO,LUV,SWK,SBUX,"
    "STT,STLD,STE,SYK,SMCI,SYF,SNPS,SYY,TMUS,TROW,TTWO,TPR,TRGP,TGT,TEL,TDY,TER,TSLA,TXN,TPL,TXT,TMO,TJX,TKO,TSCO,"
    "TT,TDG,TRV,TRMB,TFC,TYL,TSN,USB,UBER,UDR,ULTA,UNP,UAL,UPS,URI,UNH,UHS,VLO,VEEV,VTR,VLTO,VRSN,VRSK,VZ,VRTX,VRT,"
    "VTRS,VICI,V,VST,VMC,WRB,GWW,WAB,WMT,DIS,WBD,WM,WAT,WEC,WFC,WELL,WST,WDC,WY,WSM,WMB,WTW,WDAY,WYNN,XEL,XYL,YUM,"
    "ZBRA,ZBH,ZTS"
)

NASDAQ_FULL = (
    "MDLZ,ADI,ADP,adsk,AAL,ALGN,AMAT,AMD,AMGN,AMZN,ANSS,ASML,TEAM,ADBE,BIIB,BMRN,BKNG,AVGO,CDNS,CDW,CERN,CHTR,"
    "CHKP,CTAS,CSCO,CTSH,CMCSA,CPRT,COST,CRWD,DLTR,DXCM,EBAY,EA,EXPE,FAST,FB,FI,FOXA,FOX,GILD,GOOGL,GOOG,"
    "IDXX,ILMN,INCY,INTC,INTU,ISRG,JBHT,JD,KDP,KLAC,KHC,LRCX,LULU,MELI,MAR,MTCH,MCHP,MU,MSFT,MRNA,MDLO,MNST,"
    "NTES,NFLX,NVDA,NXPI,ORLY,OKTA,ODFL,PCAR,PAYX,PYPL,PEP,PDD,REGN,ROST,SIRI,SWKS,SPLK,SBUX,SNPS,TMUS,TSLA,"
    "TXN,TCOM,VRSN,VRTX,WBA,WDAY,XEL,XLNX,ZM"
)

# IL LISTINO COMPLETO DI MILANO: 40 FTSE MIB + 35 MID CAP + 25 SMALL CAP AD ALTI VOLUMI
FTSEMIB_FULL = (
    # --- FTSE MIB (40 Blue Chip) ---
    "A2A.MI,AMP.MI,AZM.MI,BAMI.MI,BGN.MI,BMED.MI,BMPS.MI,BPER.MI,BPSO.MI,CPR.MI,"
    "DIA.MI,ENEL.MI,ENI.MI,ERG.MI,EVO.MI,FBK.MI,G.MI,HER.MI,INW.MI,INTERPUMP.MI,"
    "ISP.MI,IVG.MI,LDO.MI,MB.MI,MONC.MI,NEXI.MI,PIRC.MI,PRY.MI,PST.MI,RACE.MI,"
    "REC.MI,SGO.MI,SRG.MI,STLAM.MI,STM.MI,TEN.MI,TIT.MI,TPRO.MI,TRN.MI,UCG.MI,UNI.MI,"
    # --- FTSE ITALIA MID CAP (Migliori Mid-Cap per Liquidità) ---
    "ANIM.MI,JUVE.MI,OVS.MI,CE.MI,BC.MI,SAB.MI,MFEA.MI,MFEB.MI,INX.MI,DTR.MI,"
    "MT.MI,LIN.MI,ELN.MI,IPH.MI,FILA.MI,GVS.MI,SFI.MI,ZV.MI,WDF.MI,ARR.MI,"
    "AGL.MI,ASCO.MI,BIF.MI,BDB.MI,ALR.MI,SO.MI,TXT.MI,BF.MI,セ.MI,SL.MI,"
    "Sesa.MI,TINE.MI,LUVE.MI,IF.MI,セ.MI,"
    # --- SMALL CAP ELEVATA LIQUIDITA (Selezionate per operatività Quant) ---
    "FNC.MI,RWAY.MI,GEO.MI,BCN.MI,DIS.MI,BFE.MI,SNG.MI,CSP.MI,FIE.MI,AIFI.MI,"
    "TRI.MI,EXP.MI,CIA.MI,TES.MI,CKR.MI,PRT.MI,PIN.MI,EAV.MI,EMS.MI,RET.MI,"
    "MS.MI,CLE.MI,DAN.MI,DANI.MI,CVAL.MI"
)

TOTAL1_LEADERS = "BTC-USD,ETH-USD"
TOTAL2_MAJORS = "SOL-USD,BNB-USD,XRP-USD,ADA-USD,TRX-USD,DOT-USD,LINK-USD,AVAX-USD,TON-USD,SHIB-USD"

# COMPARTO CRYPTO VERIFICATO 2026: AGGIORNATE MIGRAZIONI TOKEN (POL, RENDER), TOP L1, AI E DEPIN
TOTAL3_ALTS = (
    "POL-USD,LTC-USD,UNI-USD,NEAR-USD,APT-USD,ICP-USD,STX-USD,FIL-USD,ATOM-USD,"
    "IMX-USD,RENDER-USD,GRT-USD,FTM-USD,SUI-USD,OP-USD,ARB-USD,INJ-USD,LDO-USD,"
    "TIA-USD,SEI-USD,AAVE-USD,MKR-USD,RUNE-USD,EGLD-USD,THETA-USD,ALGO-USD,XLM-USD,"
    "VET-USD,FLOW-USD,AXS-USD,SAND-USD,MANA-USD,GALA-USD,CHZ-USD,DYDX-USD,CRV-USD,"
    "ENS-USD,LRC-USD,ANKR-USD,WOO-USD,GMX-USD,JUP-USD,FET-USD,TAO-USD,PEPE-USD,WIF-USD,"
    "BONK-USD,FLOKI-USD,OP-USD,LDO-USD,PENDLE-USD,TIA-USD,ENA-USD,JTO-USD"
)

CRYPTO_FULL = f"{TOTAL1_LEADERS},{TOTAL2_MAJORS},{TOTAL3_ALTS}"

def ottieni_paniere(nome_paniere):
    if nome_paniere == "S&P 500": return SP500_FULL
    elif nome_paniere == "NASDAQ 100": return NASDAQ_FULL
    elif nome_paniere == "FTSE MIB (FIB)": return FTSEMIB_FULL
    elif nome_paniere == "Crypto (TOTAL 1-2-3)": return CRYPTO_FULL
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

# Algoritmo vettoriale a 200 cassetti (Bins)
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
    with t_col2: mostra_va = st.checkbox("Mostra Value Area & Istogrammi (VAH/VAL)", value=True, key="chk_va")
    with t_col3: mostra_rr = st.checkbox("Mostra Zone Target / Stop Loss Strategici (ATR 1:2)", value=True, key="chk_rr")
    with t_col4: mostra_bb = st.checkbox("Mostra Bande di Bollinger (Volatilità Price)", value=True, key="chk_bb")
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        paniere_selezionato = st.selectbox("Seleziona Indice/Paniere:", ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)", "Crypto"], key="an_paniere")
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
                        
                        # Calcolo EMA 200, RSI, ATR strategici
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
                        
                        fig = make_subplots(
                            rows=5, cols=1, vertical_spacing=0.06, row_heights=[0.24, 0.24, 0.24, 0.14, 0.14], 
                            subplot_titles=(
                                f"1. STORICO COMPLETO ({ticker}) — POC: {round(p1,2)} | EMA200: {round(ema200_att,2)}", 
                                f"2. DALL'ATH ({d_ath.strftime('%d/%m/%Y')}) — POC: {round(p2,2)}", 
                                f"3. PROFILO RECENTE {period_label.upper()} — POC: {round(p3,2)}", 
                                "📊 RSI (14) — Momentum di Filtro (Validazione Iperestensione)", 
                                "📈 ATR (14) — Volatilità Dinamica di Canale (Dimensionamento Rischio)"
                            )
                        )
                        
                        cfg = [(1, df1, prz1, vl_v1, p1, vh1, vl1, "Generale"), (2, df2, prz2, vl_v2, p2, vh2, vl2, "ATH"), (3, df3, prz3, vl_v3, p3, vh3, vl3, f"{g3}D")]
                        
                        for r_idx, df_s, p_vp, v_vp, p_poc, p_vh, p_vl, nm in cfg:
                            if df_s.empty: continue
                            fig.add_trace(grp.Candlestick(x=df_s.index, open=df_s["Open"].astype(float), high=df_s["High"].astype(float), low=df_s["Low"].astype(float), close=df_s["Close"].astype(float), name=nm), row=r_idx, col=1)
                            fig.add_trace(grp.Scatter(x=df_s.index, y=df_s["EMA200"], mode="lines", name="EMA 200", line=dict(color="#f43f5e", width=1.5)), row=r_idx, col=1)
                            
                            if mostra_bb and len(df_s) > 20:
                                b_m = df_s["Close"].rolling(20).mean(); b_s = df_s["Close"].rolling(20).std()
                                fig.add_trace(grp.Scatter(x=df_s.index, y=b_m+(b_s*2), mode="lines", name="BB Upper", line=dict(color="rgba(56,189,248,0.25)", width=1, dash="dash")), row=r_idx, col=1)
                                fig.add_trace(grp.Scatter(x=df_s.index, y=b_m-(b_s*2), mode="lines", name="BB Lower", line=dict(color="rgba(56,189,248,0.25)", width=1, dash="dash")), row=r_idx, col=1)
                            
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
                                fig.add_annotation(x=d_lf, y=sl, text=f" SL: {round(sl,2)}", showarrow=False, align="left", bgcolor="#f59e0b", font=dict(color="black", size=9), row=r_idx, col=1)
                                fig.add_annotation(x=d_lf, y=tp, text=f" TP: {round(tp,2)}", showarrow=False, align="left", bgcolor="#06b6d4", font=dict(color="white", size=9), row=r_idx, col=1)
                            
                            if mostra_poc:
                                fig.add_shape(type="line", x0=df_s.index.min(), x1=d_lf, y0=p_poc, y1=p_poc, line=dict(color="#ef4444", width=2.5), row=r_idx, col=1)
                                fig.add_annotation(x=d_lf, y=p_poc, text=f" POC: {round(p_poc,2)}", showarrow=False, align="left", bgcolor="#ef4444", font=dict(color="white", size=9, family="Arial Black"), row=r_idx, col=1)
                            
                            txt_leg = f"<b>📊 PROFILO {nm.upper()}</b><br>Setup Ideale: {ic} {dir_n}<br>R/R Strutturale: 1:2.0<br><br>🔴 POC: {round(p_poc,2)}<br>🟠 VAH: {round(p_vh,2)}<br>🔵 VAL: {round(p_vl,2)}"
                            fig.add_annotation(xref="paper", yref="paper", x=0.01, y={1:0.98, 2:0.72, 3:0.44}[r_idx], text=txt_leg, showarrow=False, align="left", bgcolor="rgba(20,24,33,0.95)", bordercolor="rgba(242,142,43,0.4)", borderwidth=1.5, borderpad=8, font=dict(color="white", size=10))
                        
                        df_recent_ind = df_c.tail(180 if tf_attivo == "1wk" else 365)
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["RSI"], mode="lines", name="RSI", line=dict(color="#a855f7", width=2)), row=4, col=1)
                        fig.add_shape(type="line", x0=df_recent_ind.index.min(), x1=df_recent_ind.index[-1], y0=75, y1=75, line=dict(color="rgba(239, 68, 68, 0.4)", width=1.5, dash="dot"), row=4, col=1)
                        fig.add_shape(type="line", x0=df_recent_ind.index.min(), x1=df_recent_ind.index[-1], y0=25, y1=25, line=dict(color="rgba(34, 197, 94, 0.4)", width=1.5, dash="dot"), row=4, col=1)
                        fig.update_yaxes(range=[0, 100], row=4, col=1)
                        
                        fig.add_trace(grp.Scatter(x=df_recent_ind.index, y=df_recent_ind["ATR"], mode="lines", name="ATR", line=dict(color="#10b981", width=2)), row=5, col=1)
                        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False, xaxis3_rangeslider_visible=False, xaxis4_rangeslider_visible=False, xaxis5_rangeslider_visible=False, height=2000, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{ticker}")
                    else: st.warning(f"Dati storici insufficienti (<200 righe) per il calcolo strategico su {ticker}.")

# ==========================================
# --- TAB 2: GESTIONE INPUT E SCENARI 1R ---
# ==========================================
with tab2:    
    st.subheader("📐 Motore Quant Swing Trading: Algoritmo 3-Setup POC")
    st.markdown("---")
    
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        bt_ticker = st.text_input("Inserisci Ticker da analizzare (es. CRSR, AAPL, BTC-USD):", value="CRSR", key="quant_tick_in")
        capitale_iniziale = st.number_input("Capitale iniziale ($):", min_value=100, value=10000, step=500, key="quant_cap_in")
        tf_bt_label = st.selectbox("Seleziona Timeframe (Swing Trading):", ["Giornaliero (Daily)", "Settimanale (Weekly)", "Mensile (Monthly)"], key="quant_tf_in")
        tf_bt_attivo = {"Giornaliero (Daily)": "1d", "Settimanale (Weekly)": "1wk", "Mensile (Monthly)": "1mo"}[tf_bt_label]
    with b_col2:
        bt_periodo = st.selectbox("Orizzonte temporale dei dati:", ["1 Anno", "3 Anni", "5 Anni", "Storico Massimo"], index=2, key="quant_per_in")
        mappa_periodi = {"1 Anno": "1y", "3 Anni": "3y", "5 Anni": "5y", "Storico Massimo": "max"}
        rischio_trade = st.slider("Rischio percentuale massimo tollerato (Fisso 1R):", min_value=0.5, max_value=2.0, value=1.0, step=0.5, key="quant_risk_in")
    with b_col3:
        comun_fee = st.number_input("Commissioni per singolo eseguito ($):", min_value=0.0, value=1.99, step=0.5, key="quant_fee_in")
        scenario_rr = st.selectbox(
            "Seleziona Configurazione Money Management (Tabella Foto):",
            [
                "1. Stop Uguale (Peso 50/50) -> R/R Totale: 0.70",
                "2. Stop 1/3 più corto (Peso 50/50) -> R/R Totale: 0.81",
                "3. Target Fisso 1:1.4 (Peso 50/50) -> RR2 Richiesto: 1.867",
                "4. Target Fisso 1:1.4 (Peso 60/40) -> RR2 Richiesto: 2.10"
            ],
            key="quant_mm_in"
        )
    if st.button("🚀 Avvia Backtest Multi-Setup", type="primary", key="quant_run_btn"):
        st.info(f"Scarico dati storici ed elaborazione dei livelli di volume per {bt_ticker}...")
        df_bt = yf.download(tickers=bt_ticker, period=mappa_periodi[bt_periodo], interval=tf_bt_attivo, auto_adjust=False, multi_level_index=False, progress=False)
        
        if df_bt is not None and len(df_bt) > 40:
            df_bt.columns = [str(c).strip() for c in df_bt.columns]
            
            # Media mobile veloce a 20 periodi per calcolare i cambi di momentum macro
            df_bt["EMA_Momentum"] = df_bt["Close"].astype(float).ewm(span=20, adjust=False).mean()
            
            capitale = capitale_iniziale
            equity_curve = [capitale_iniziale]
            date_curve = [df_bt.index[0]]
            trade_history = []
            segmenti_grafici = []
            
            in_posizione = False
            pocs_istituzionali_storici = []
            indice_ancoraggio_vp = 0
            ultimo_poc_valido = None

            # Assegnazione proporzioni esatte del rischio matematico 1R (Foto)
            if "1." in scenario_rr:
                w1, w2, rr_op1_parziali, rr_op2, modificatore_stop_op2 = 0.50, 0.50, [0.462, 0.933, 1.40], 0.462, 1.0
            elif "2." in scenario_rr:
                w1, w2, rr_op1_parziali, rr_op2, modificatore_stop_op2 = 0.50, 0.50, [0.462, 0.933, 1.40], 0.693, 2/3
            elif "3." in scenario_rr:
                w1, w2, rr_op1_parziali, rr_op2, modificatore_stop_op2 = 0.50, 0.50, [0.462, 0.933, 1.40], 1.867, 1.0
            else:
                w1, w2, rr_op1_parziali, rr_op2, modificatore_stop_op2 = 0.60, 0.40, [0.462, 0.933, 1.40], 2.10, 1.0

            # Calcolo preventivo di tutti i POC permanenti generati ad ogni incrocio del momentum
            for idx in range(20, len(df_bt)):
                r_prec = df_bt.iloc[idx-1]
                r_att = df_bt.iloc[idx]
                cross_rialzo = (r_prec["Close"] <= r_prec["EMA_Momentum"]) and (r_att["Close"] > r_att["EMA_Momentum"])
                cross_ribasso = (r_prec["Close"] >= r_prec["EMA_Momentum"]) and (r_att["Close"] < r_att["EMA_Momentum"])
                
                if cross_rialzo or cross_ribasso or len(pocs_istituzionali_storici) == 0:
                    df_blocco = df_bt.iloc[indice_ancoraggio_vp:idx]
                    if len(df_blocco) >= 5:
                        p_poc_nuovo, _, _, _, _ = calc_vp(df_blocco, div=150)
                        if p_poc_nuovo is not None:
                            pocs_istituzionali_storici.append({"livello": p_poc_nuovo, "data_generazione": df_bt.index[idx]})
                            ultimo_poc_valido = p_poc_nuovo
                            indice_ancoraggio_vp = idx
            # Loop per il backtesting dei 3 moduli operativi richiesti
            for i in range(25, len(df_bt)):
                if ultimo_poc_valido is None:
                    continue
                riga_attuale = df_bt.iloc[i]
                p_chiusura = float(riga_attuale["Close"])
                p_apertura = float(riga_attuale["Open"])
                p_massimo = float(riga_attuale["High"])
                p_minimo = float(riga_attuale["Low"])
                data_corrente = df_bt.index[i]

                if not in_posizione:
                    # Estrazione delle ultime 8 candele per valutare i livelli di Supporto e Resistenza vicino al POC
                    finestra_intorno = df_bt.iloc[max(0, i-8):i]
                    resistenza_intorno = float(finestra_pattern["High"].max()) if 'finestra_pattern' in locals() else float(finestra_intorno["High"].max())
                    supporto_intorno = float(finestra_pattern["Low"].min()) if 'finestra_pattern' in locals() else float(finestra_intorno["Low"].min())
                    
                    # ---------------------------------------------------------
                    # SETUP 1: PRIMO TOCCO DI UN POC PERMANENTE (PUNTO 2)
                    # ---------------------------------------------------------
                    tocco_da_sopra = (p_apertura > ultimo_poc_valido) and (p_minimo <= ultimo_poc_valido)
                    tocco_da_sotto = (p_apertura < ultimo_poc_valido) and (p_massimo >= ultimo_poc_valido)
                    
                    if tocco_da_sopra or tocco_da_sotto:
                        in_posizione = True
                        posizione_tipo = "LONG" if tocco_da_sopra else "SHORT"
                        prezzo_ingresso = ultimo_poc_valido
                        nome_setup = "Primo Tocco POC"
                        
                        ampiezza_r = abs(prezzo_ingresso - supporto_intorno) if posizione_tipo == "LONG" else abs(resistenza_intorno - prezzo_ingresso)
                        sl_op1 = supporto_intorno if posizione_tipo == "LONG" else resistenza_intorno
                        ha_incrementato_retest = False
                        
                    # ---------------------------------------------------------
                    # SETUP 2: BREAKOUT DI RESISTENZA/SUPPORTO CON CANDELA PIENA (PUNTI 3 E 4)
                    # ---------------------------------------------------------
                    elif (p_minimo <= ultimo_poc_valido <= p_massimo) or (supporto_intorno <= p_chiusura <= resistenza_intorno):
                        breakout_long_struttura = (p_chiusura > resistenza_intorno) and (p_chiusura > p_apertura)
                        breakout_short_struttura = (p_chiusura < supporto_intorno) and (p_chiusura < p_apertura)
                        
                        if breakout_long_struttura:
                            in_posizione = True
                            posizione_tipo = "LONG"
                            prezzo_ingresso = p_chiusura
                            sl_op1 = supporto_intorno
                            ampiezza_r = abs(prezzo_ingresso - sl_op1)
                            nome_setup = "Breakout Resistenza POC"
                            ha_incrementato_retest = False
                        elif breakout_short_struttura:
                            in_posizione = True
                            posizione_tipo = "SHORT"
                            prezzo_ingresso = p_chiusura
                            sl_op1 = resistenza_intorno
                            ampiezza_r = abs(sl_op1 - prezzo_ingresso)
                            nome_setup = "Breakout Supporto POC"
                            ha_incrementato_retest = False

                    # ---------------------------------------------------------
                    # SETUP 3: COMPRESSIONE CON MASSIMI DECRESCENTI (TRENDLINE RIBASSISTA - PUNTO 5)
                    # ---------------------------------------------------------
                    elif (supporto_intorno <= p_minimo <= ultimo_poc_valido):
                        # Analisi dei massimi decrescenti (Trendline Ribassista) nelle ultime 5 candele
                        m_5 = df_bt.iloc[i-5:i]["High"].values
                        compresso_massimi_decrescenti = (m_5[0] > m_5[1] > m_5[2]) or (m_5[1] > m_5[2] > m_5[3])
                        tenuta_supporto_statico = p_minimo >= supporto_intorno * 0.99
                        
                        if compresso_massimi_decrescenti and tenuta_supporto_statico and (p_chiusura > p_apertura):
                            # Rottura della linea di compressione alta
                            in_posizione = True
                            posizione_tipo = "LONG"
                            prezzo_ingresso = p_chiusura
                            sl_op1 = supporto_intorno
                            ampiezza_r = abs(prezzo_ingresso - sl_op1)
                            nome_setup = "Rottura Trendline Compressione"
                            ha_incrementato_retest = False

                    # Configurazione Monetaria Rigida all'innesco valido del trade (Protezione 1R)
                    if in_posizione:
                        if ampiezza_r <= 0:
                            in_posizione = False
                            continue
                        data_inizio_trade = data_corrente
                        poc_centrale_trade = ultimo_poc_valido
                        
                        if posizione_tipo == "LONG":
                            sl_op2 = prezzo_ingresso - (ampiezza_r * modificatore_stop_op2)
                            tp_op1_fasi = [prezzo_ingresso + (ampiezza_r * r) for r in rr_op1_parziali]
                            tp_op2 = prezzo_ingresso + (ampiezza_r * rr_op2)
                        else:
                            sl_op2 = prezzo_ingresso + (ampiezza_r * modificatore_stop_op2)
                            tp_op1_fasi = [prezzo_ingresso - (ampiezza_r * r) for r in rr_op1_parziali]
                            tp_op2 = prezzo_ingresso - (ampiezza_r * rr_op2)

                        rischio_monetario_totale = capitale * (rischio_trade / 100)
                        size_op1 = (rischio_monetario_totale * w1) / ampiezza_r
                        size_op2 = (rischio_monetario_totale * w2) / (ampiezza_r * modificatore_stop_op2)
                        
                        stato_op1_fasi = [True, True, True]
                        dim_quota_op1 = size_op1 / 3.0
                        stato_op2_attiva = True
                        pnl_accumulato_trade = 0.0
                else:
                    # Se in posizione, monitora l'evoluzione e le uscite
                    # MODULO INCREMENTO: Se fa Retest del POC incrementa la posizione caricando +20% contratti a protezione
                    if not ha_incrementato_retest and (nome_setup in ["Breakout Resistenza POC", "Breakout Supporto POC"]):
                        if (posizione_tipo == "LONG" and p_minimo <= poc_centrale_trade) or (posizione_tipo == "SHORT" and p_massimo >= poc_centrale_trade):
                            size_op2 *= 1.20  # Incremento strutturale controllato della tranche aggressiva
                            ha_incrementato_retest = True

                    if i_tipo_long := (posizione_tipo == "LONG"):
                        if p_minimo <= sl_op2 and stato_op2_attiva:
                            pnl_accumulato_trade += (sl_op2 - prezzo_ingresso) * size_op2 - comun_fee
                            stato_op2_attiva = False
                        if p_minimo <= sl_op1:
                            if stato_op2_attiva:
                                pnl_accumulato_trade += (sl_op1 - prezzo_ingresso) * size_op2 - comun_fee
                                stato_op2_attiva = False
                            for f in range(3):
                                if stato_op1_fasi[f]:
                                    pnl_accumulato_trade += (sl_op1 - prezzo_ingresso) * dim_quota_op1 - comun_fee
                                    stato_op1_fasi[f] = False
                        if stato_op2_attiva and p_massimo >= tp_op2:
                            pnl_accumulato_trade += (tp_op2 - prezzo_ingresso) * size_op2 - comun_fee
                            stato_op2_attiva = False
                        for f in range(3):
                            if stato_op1_fasi[f] and p_massimo >= tp_op1_fasi[f]:
                                pnl_accumulato_trade += (tp_op1_fasi[f] - prezzo_ingresso) * dim_quota_op1 - comun_fee
                                stato_op1_fasi[f] = False
                    else: # SHORT
                        if p_massimo >= sl_op2 and stato_op2_attiva:
                            pnl_accumulato_trade += (prezzo_ingresso - sl_op2) * size_op2 - comun_fee
                            stato_op2_attiva = False
                        if p_massimo >= sl_op1:
                            if stato_op2_attiva:
                                pnl_accumulato_trade += (prezzo_ingresso - sl_op1) * size_op2 - comun_fee
                                stato_op2_attiva = False
                            for f in range(3):
                                if stato_op1_fasi[f]:
                                    pnl_accumulato_trade += (prezzo_ingresso - sl_op1) * dim_quota_op1 - comun_fee
                                    stato_op1_fasi[f] = False
                        if stato_op2_attiva and p_minimo <= tp_op2:
                            pnl_accumulato_trade += (prezzo_ingresso - tp_op2) * size_op2 - comun_fee
                            stato_op2_attiva = False
                        for f in range(3):
                            if stato_op1_fasi[f] and p_minimo <= tp_op1_fasi[f]:
                                pnl_accumulato_trade += (prezzo_ingresso - tp_op1_fasi[f]) * dim_quota_op1 - comun_fee
                                stato_op1_fasi[f] = False

                    # Consolidamento a chiusura totale delle Tranche
                    if not stato_op2_attiva and not any(stato_op1_fasi):
                        capitale += pnl_accumulato_trade
                        esito_lbl = "PROFIT 🟢" if pnl_accumulato_trade > 0 else "LOSS 🛑"
                        
                        trade_history.append({
                            "Data": data_corrente.strftime("%d/%m/%Y"),
                            "Setup Utilizzato": nome_setup,
                            "Tipo": posizione_tipo,
                            "Ingresso": round(prezzo_ingresso, 2),
                            "Esito": esito_lbl,
                            "Incrementato Retest": "Sì (+20%)" if ha_incrementato_retest else "No",
                            "PnL Netto ($)": round(pnl_accumulato_trade, 2),
                            "Capitale Liquido ($)": round(capitale, 2)
                        })
                        
                        segmenti_grafici.append({
                            "x": [data_inizio_trade, data_corrente],
                            "poc": [poc_centrale_trade, poc_centrale_trade],
                            "sl_op1": [sl_op1, sl_op1],
                            "sl_op2": [sl_op2, sl_op2],
                            "tp_op2": [tp_op2, tp_op2]
                        })
                        equity_curve.append(capitale)
                        date_curve.append(data_corrente)
                        in_posizione = False
            # Calcolo metriche di riepilogo
            st.subheader("📊 Analisi delle Performance dei 3 Setup Quant")
            if trade_history:
                df_trades = pd.DataFrame(trade_history)
                profitti = df_trades[df_trades["PnL Netto ($)"] > 0]["PnL Netto ($)"].sum()
                perdite = abs(df_trades[df_trades["PnL Netto ($)"] < 0]["PnL Netto ($)"].sum())
                win_rate = round((len(df_trades[df_trades["PnL Netto ($)"] > 0]) / len(df_trades)) * 100, 2)
                profit_factor = round(profitti / max(0.01, perdite), 2)
                
                arr_eq = np.array(equity_curve)
                peaks = np.maximum.accumulate(arr_eq)
                max_dd = round(abs(((arr_eq - peaks) / peaks).min()) * 100, 2) if len(peaks) > 0 else 0.0
                
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Capitale Finale", f"$ {round(capitale,2)}")
                m_col2.metric("Win Rate Globale", f"{win_rate} %")
                m_col3.metric("Profit Factor", f"{profit_factor}")
                m_col4.metric("Massimo Drawdown", f"-{max_dd} %")

                st.plotly_chart(grp.Figure().add_trace(grp.Scatter(x=date_curve, y=equity_curve, mode='lines+markers', name='Equity Line', line=dict(color='#818cf8', width=2.5))).update_layout(title="📈 Evoluzione del Capitale Intero (Matrice 1R)", template="plotly_dark", height=280), use_container_width=True)
                st.dataframe(df_trades, use_container_width=True)

                # Renderizzazione Visiva dei Canali sui Grafici
                st.markdown("##### 🔍 Verifica dei Pattern Grafici Rilevati dal Motore")
                fig_strat = grp.Figure()
                fig_strat.add_trace(grp.Candlestick(x=df_bt.index, open=df_bt["Open"], high=df_bt["High"], low=df_bt["Low"], close=df_bt["Close"], name="Prezzo"))
                
                for idx, seg in enumerate(segmenti_grafici):
                    s_leg = True if idx == 0 else False
                    fig_strat.add_trace(grp.Scatter(x=seg["x"], y=seg["poc"], mode="lines", name="🔴 POC di Riferimento", line=dict(color="#ef4444", width=2), showlegend=s_leg))
                    fig_strat.add_trace(grp.Scatter(x=seg["x"], y=seg["sl_op1"], mode="lines", name="🔵 SL Strutturale (Op1)", line=dict(color="#3b82f6", width=1.5, dash="dash"), showlegend=s_leg))
                    fig_strat.add_trace(grp.Scatter(x=seg["x"], y=seg["sl_op2"], mode="lines", name="🟠 SL Op2 (Stretto)", line=dict(color="#f97316", width=1.5, dash="dot"), showlegend=s_leg))
                    fig_strat.add_trace(grp.Scatter(x=seg["x"], y=seg["tp_op2"], mode="lines", name="🟢 Target Matrice (Op2)", line=dict(color="#22c55e", width=1.5, dash="dash"), showlegend=s_leg))

                st.plotly_chart(fig_strat.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=550), use_container_width=True, key="bt_final_multi")
            else:
                st.warning("Nessun setup ha completato la configurazione tecnica 'Innesco + Retest' nel periodo storico scelto.")
        else:
            st.error("Dati storici insufficienti caricati per il Ticker specificato.")

# ==========================================
# --- TAB 3: LIVE ALERTS STRATEGICI ---
# ==========================================
with tab3:
    st.subheader("🔔 Canale Notifiche Quantitative in Tempo Reale via Telegram")
    st.success("✅ Algoritmo di Strategia Bilanciata (EMA + RSI + ATR Volatility) Integrato.")
    
    st.markdown("---")
    st.subheader("📡 Configurazione Selettiva Parametri Scanner")
    
    fl1, fl2, fl3 = st.columns(3)
    with fl1:
        soglia_distanza = st.slider("Seleziona la distanza massima dal POC per l'alert (%):", min_value=0.5, max_value=4.0, value=2.0, step=0.1, key="tg_dist")
    with fl2:
        poc_scelti = st.multiselect("Seleziona quali profili analizzare:", options=["Generale", "ATH", "Recente (90D)"], default=["Generale", "ATH", "Recente (90D)"], key="tg_sel_p")
    with fl3:
        orizzonte_recente = st.selectbox("Imposta l'estensione del profilo Recente:", ["3 Mesi", "6 Mesi", "9 Mesi"], index=0, key="tg_oriz_t")
        mappa_giorni_tg = {"3 Mesi": 90, "6 Mesi": 180, "9 Mesi": 270}
        g_recenti_scelti = mappa_giorni_tg[orizzonte_recente]

    p_selezionato_alert = st.selectbox("Seleziona il paniere completo da scansionare:", ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)", "Crypto"], key="tg_paniere")
    lista_ticker_alert = [t.strip() for t in ottieni_paniere(p_selezionato_alert).split(",") if t.strip()]
    
    if st.button("🚀 Attiva Scansione Strategica", type="primary"):
        if not poc_scelti:
            st.error("❌ Seleziona almeno una tipologia di POC nei filtri.")
        else:
            st.info(f"Avvio scansione quantitativa bilanciata su {p_selezionato_alert}...")
            segnali_trovati = 0
            barra_progresso = st.progress(0.0)
            totale_titoli = len(lista_ticker_alert)
            
            for idx, ticker in enumerate(lista_ticker_alert):
                barra_progresso.progress((idx + 1) / totale_titoli)
                tk_yf = ticker + "-USD" if p_selezionato_alert == "Crypto" and not ticker.endswith("-USD") else ticker
                df_live = yf.download(tickers=tk_yf, period="max", interval="1d", auto_adjust=False, multi_level_index=False, progress=False, timeout=8)
                if df_live is None or len(df_live) < 200: continue
                
                df_live.columns = [str(c).strip() for c in df_live.columns]
                mappa_colonne = {c.lower(): c for c in df_live.columns}
                close_series = df_live[mappa_colonne['close']].astype(float)
                high_series = df_live[mappa_colonne['high']].astype(float)
                low_series = df_live[mappa_colonne['low']].astype(float)
                p_attuale = float(close_series.iloc[-1])
                d_ath = high_series.idxmax()
                
                # Indicatori di Trend e Volatilità
                ema200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1]
                delta = close_series.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rsi_attuale = (100 - (100 / (1 + (gain / np.where(loss == 0, 0.00001, loss))))).iloc[-1]
                tr = pd.concat([high_series - low_series, (high_series - close_series.shift(1)).abs(), (low_series - close_series.shift(1)).abs()], axis=1).max(axis=1)
                atr_attuale = tr.rolling(window=14).mean().iloc[-1]
                
                df_generale = df_live.copy()
                df_ath_data = df_live.loc[d_ath:].copy()
                df_recente = df_live.tail(g_recenti_scelti).copy()
                
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
                        if "RECENTE" in nome_profilo:
                            passa_trend_long = p_attuale > ema200
                            passa_trend_short = p_attuale < ema200
                        else:
                            passa_trend_long, passa_trend_short = True, True
                        
                        setup_valido = False
                        if p_attuale >= p_poc and passa_trend_long and is_rsi_ok_long:
                            direzione = "LONG 🟢"
                            stop_l = p_attuale - (1.5 * atr_attuale)
                            take_p = p_attuale + (3.0 * atr_attuale)
                            setup_valido = True
                        elif p_attuale < p_poc and passa_trend_short and is_rsi_ok_short:
                            direzione = "SHORT 🔴"
                            stop_l = p_attuale + (1.5 * atr_attuale)
                            take_p = p_attuale - (3.0 * atr_attuale)
                            setup_valido = True
                        
                        if setup_valido:
                            segnali_trovati += 1
                            ticker_pulito = str(ticker).replace(".MI", "").replace("-USD", "").strip()
                            if str(ticker).endswith(".MI"): borsa_codice = "MILAN"
                            elif "-USD" in str(ticker) or p_selezionato_alert == "Crypto": borsa_codice = "BINANCE"
                            else: borsa_codice = "NASDAQ" if p_selezionato_alert == "NASDAQ 100" else "NYSE"
                            
                            url_stringa_pura = f"https://tradingview.com/chart/sqBvK6ky/?symbol={ticker_pulito}"
                            dec = 4 if p_selezionato_alert == 'Crypto' else 2
                            
                            messaggio_alert = (
                                f"🚨 <b>STRATEGIA QUANT BILANCIATA (DASHBOARD)</b>\n\n"
                                f"🎯 <b>Ticker:</b> #{ticker_pulito} ({p_selezionato_alert})\n"
                                f"🗂️ <b>Profilo Volume:</b> {nome_profilo}\n"
                                f"⚡ <b>Setup Operativo:</b> {direzione}\n\n"
                                f"📊 <b>Prezzo Attuale:</b> {round(p_attuale, dec)} USD\n"
                                f"🔴 <b>Entry Prezzo:</b> {round(p_attuale, dec)}\n"
                                f"🟠 <b>Stop Loss (1.5 ATR):</b> {round(stop_l, dec)}\n"
                                f"🔵 <b>Take Profit (3.0 ATR):</b> {round(take_p, dec)}\n\n"
                                f"🔍 <b>Metriche di Controllo:</b>\n"
                                f"|— <i>Rapporto R/R:</i> 1:2.0 (Fisso)\n"
                                f"|— <i>RSI (14):</i> {round(rsi_attuale, 1)}\n"
                                f"|— <i>EMA200 Filtro:</i> {'SOPRA' if p_attuale > ema200 else 'SOTTO'}\n\n"
                                f"🔗 <a href='{url_stringa_pura}'>APRI IL GRAFICO SU TRADINGVIEW</a>"
                            )
                            invia_messaggio_telegram_sbloccato(T_ID, messaggio_alert)
                            
            st.success(f"Scansione terminata! Inviati {segnali_trovati} segnali bilanciati ad alta probabilità.")
