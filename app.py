import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as grp
from plotly.subplots import make_subplots
import requests
import json

# 1. Impostazione della pagina web a tutto schermo e tema premium
st.set_page_config(layout="wide", page_title="VolNodes Pro", page_icon="📐")

# --- INIEZIONE CSS PER DESIGN PREMIUM E MODERNO (Glassmorphism & SaaS) ---
st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    .stApp {
        background: radial-gradient(circle at top right, #1a1f36 0%, #0d0f18 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc;
    }
    
    h1 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 15px;
        text-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
    }
    
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
        border-radius: 14px !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 10px 30px -5px rgba(56, 189, 248, 0.15) !important;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2.2rem !important;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px 0 rgba(59, 130, 246, 0.45) !important;
    }
    
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        padding: 12px 24px !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.3s ease;
    }
    button[aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
        text-shadow: 0 0 10px rgba(0, 206, 209, 0.3);
    }
    
    div[data-baseweb="select"], input, textarea {
        background-color: #0f172a !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📐 VolNodes Pro — Dashboard Multitasking")

# Inizializzazione degli stati della sessione
if "asset_type_index" not in st.session_state:
    st.session_state.asset_type_index = 0

# --- CREDENZIALI E CONFIGURAZIONI NATIVE ---
T_ID = "2072895073"
TESTA_INTERNET = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
}

# --- DATABASE INTERNO DEI PANIERI ---
SP500_FULL = (
    "MMM,AOS,ABT,ABBV,ACN,ADBE,AMD,AES,AFL,A,APD,ABNB,AKAM,ALB,ARE,ALGN,ALLE,LNT,ALL,GOOGL,GOOG,MO,AMZN,AMCR,AEE,"
    "AEP,AXP,AIG,AMT,AWK,AMP,AME,AMGN,APH,ADI,AON,APA,APO,AAPL,AMAT,APP,APTV,ACGL,ADM,ARES,ANET,AJG,AIZ,T,ATO,ADSK,"
    "ADP,AZO,AVY,AXON,BKR,BALL,BAC,BAX,BDX,BRK-B,BBY,TECH,BIIB,BLK,BX,BE,BNY,BA,BKNG,BSX,BMY,AVGO,BR,BRO,BF-B,BG,"
    "BXP,CHRW,CDNS,CPT,COF,CAH,CCL,CARR,CVNA,CASY,CAT,CBOE,CBRE,CDW,COR,CNC,CNP,CF,CRL,SCHW,CHTR,CVX,CMG,CB,CHD,"
    "CIEN,CI,CINF,CTAS,CSCO,C,CFG,CLX,CME,CMS,KO,CTSH,COHR,COIN,CL,CMCSA,FIX,COP,ED,STZ,CEG,COO,CPRT,GLW,CPAY,CTVA,"
    "CSGP,COST,CRH,CRWD,CCI,CSX,CMI,CVS,DHR,DRI,DRI,DVA,DECK,DE,DELL,DAL,DVN,DXCM,FANG,DLR,DG,DLTR,D,DPZ,DASH,DOV,"
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
    "ZBRA,ZBH,ZTS"
)

NASDAQ_FULL = (
    "MDLZ,ADI,ADP,ADSK,AAL,ALGN,AMAT,AMD,AMGN,AMZN,ANSS,ASML,TEAM,ADBE,BIIB,BMRN,BKNG,AVGO,CDNS,CDW,CERN,CHTR,"
    "CHKP,CTAS,CSCO,CTSH,CMCSA,CPRT,COST,CRWD,DLTR,DXCM,EBAY,EA,EXPE,FAST,FB,FISV,FOXA,FOX,GILD,GOOGL,GOOG,"
    "IDXX,ILMN,INCY,INTC,INTU,ISRG,JBHT,JD,KDP,KLAC,KHC,LRCX,LULU,MELI,MAR,MTCH,MCHP,MU,MSFT,MRNA,MDLO,MNST,"
    "NTES,NFLX,NVDA,NXPI,ORLY,OKTA,ODFL,PCAR,PAYX,PYPL,PEP,PDD,REGN,ROST,SIRI,SWKS,SPLK,SBUX,SNPS,TMUS,TSLA,"
    "TXN,TCOM,VRSN,VRTX,WBA,WDAY,XEL,XLNX,ZM"
)

FTSEMIB_FULL = (
    "A2A.MI,AMP.MI,AZM.MI,BAMI.MI,BCA.MI,BMED.MI,BPER.MI,CPR.MI,DIA.MI,ENI.MI,ERG.MI,EVO.MI,FBK.MI,G.MI,"
    "HER.MI,INW.MI,ISP.MI,LDO.MI,MB.MI,MONC.MI,NEXI.MI,PIRC.MI,PRY.MI,PST.MI,RACE.MI,REC.MI,SGO.MI,SRG.MI,"
    "STLAM.MI,STMMI.MI,TEN.MI,TRN.MI,UCG.MI,UNI.MI,YSVP.MI"
)

CRYPTO_FULL = (
    "BTC-USD,ETH-USD,SOL-USD,BNB-USD,XRP-USD,ADA-USD,DOGE-USD,AVAX-USD,"
    "DOT-USD,LINK-USD,MATIC-USD,LTC-USD,UNI-USD,NEAR-USD,SUI-USD"
)

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

# Generazione dei Tab principali nell'interfaccia
tab1, tab2, tab3 = st.tabs(["Analisi Triple-POC", "Backtesting", "Alert Telegram"])

# --- TAB 1: ANALISI TRIPLE-POC ---
with tab1:
    st.subheader("📊 Analisi Grafica Avanzata Volume Profile & Indicatori")
    
    # --- TOGGLE DEI LIVELLI ---
    st.markdown("##### ⚙️ Personalizzazione Livelli Grafici")
    st.markdown(
        "Utilizza i controlli sottostanti per ottimizzare la pulizia visiva del grafico cartesiano, "
        "accendendo o spegnendo i nodi volumetrici e le proiezioni algoritmiche calcolate."
    )
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        mostra_poc = st.checkbox("Mostra Linea POC Entry (Rosso)", value=True, key="chk_poc")
    with t_col2:
        mostra_va = st.checkbox("Mostra Value Area & Istogrammi (VAH/VAL)", value=True, key="chk_va")
    with t_col3:
        mostra_rr = st.checkbox("Mostra Zone Target / Stop Loss (R/R)", value=True, key="chk_rr")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        paniere_selezionato = st.selectbox("Seleziona Indice/Paniere:", ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)", "Crypto"], key="an_paniere")
        ticker_caricati = ottieni_paniere(paniere_selezionato)
        if paniere_selezionato == "Crypto": st.session_state.asset_type_index = 1
        else: st.session_state.asset_type_index = 0
    with col2:
        asset_type = st.selectbox("Tipo Asset:", ["Azione", "Criptovaluta"], index=st.session_state.asset_type_index, key="an_type")
    with col3:
        period_label = st.selectbox("Seleziona Estensione Profilo Recente:", ["3 Mesi", "6 Mesi", "9 Mesi"], key="an_period")
        period_map = {"3 Mesi": 90, "6 Mesi": 180, "9 Mesi": 270}
        g3 = period_map[period_label]

    tickers_input = st.text_area("Modifica o verifica i Tickers estratti (separati da virgola):", value=ticker_caricati, height=150, key=f"an_area_{paniere_selezionato}")

    if st.button("🔍 Avvia Analisi Grafica Nodes", type="primary"):
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        if not tickers:
            st.warning("Inserisci almeno un ticker valido.")
        else:
            st.success(f"Analisi avviata per {len(tickers)} elementi. Generazione fogli ticker...")
            
            fogli_ticker = st.tabs(tickers)
            
            for ticker, foglio_attivo in zip(tickers, fogli_ticker):
                with foglio_attivo:
                    tk_yf = ticker + "-USD" if asset_type == "Criptovaluta" and not ticker.endswith("-USD") else ticker
                    df_c = yf.download(tickers=tk_yf, period="max", interval="1d", auto_adjust=False, multi_level_index=False, progress=False)
                    
                    if df_c is not None and not df_c.empty:
                        close_series = df_c["Close"]
                        p_att = float(close_series.values[-1] if hasattr(close_series, 'values') else close_series.iloc[-1])
                        df1, d_ath = df_c.copy(), df_c["High"].idxmax()
                        df2, df3 = df_c.loc[d_ath:].copy(), df_c.tail(g3).copy()
                        
                        p1, vh1, vl1, prz1, vl_v1 = calc_vp(df1)
                        p2, vh2, vl2, prz2, vl_v2 = calc_vp(df2)
                        p3, vh3, vl3, prz3, vl_v3 = calc_vp(df3)
                        if None in [p1, vh1, vl1, p2, vh2, vl2, p3, vh3, vl3]: continue
                        
                        # --- CALCOLO MATEMATICO DELL'RSI (14 Periodi) ---
                        delta = df_c["Close"].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / np.where(loss == 0, 0.00001, loss)
                        df_c["RSI"] = 100 - (100 / (1 + rs))
                        
                        # --- INSERIMENTO SPIEGAZIONE DEL MOMENTUM SOTTO IL NOME DELL'INDICATORE ---
                        st.markdown("#### 📊 Oscillatore Momentum RSI (14)")
                        st.markdown(
                            "**Analisi di Momentum Integrata:** La riga dell'RSI in fondo ti permette di verificare all'istante "
                            "se l'avvicinamento del prezzo al Point of Control (POC) sta avvenendo in una fase di esaurimento "
                            "del trend o se ha spazio per rimbalzare."
                        )
                        
                        fig = make_subplots(
                            rows=4, cols=1, 
                            subplot_titles=(
                                f"1. STORICO COMPLETO DALL'INIZIO ({ticker}) — POC: {round(p1,2)}", 
                                f"2. DALL'ATH ({d_ath.strftime('%d/%m/%Y')}) — POC: {round(p2,2)}", 
                                f"3. PROFILO RECENTE {period_label.upper()} — POC: {round(p3,2)}",
                                "Indicator Plot"
                            ), 
                            vertical_spacing=0.08,
                            row_heights=[0.28, 0.28, 0.28, 0.16]
                        )
                        
                        cfg = [(1, df1, prz1, vl_v1, p1, vh1, vl1, "Generale"), (2, df2, prz2, vl_v2, p2, vh2, vl2, "ATH"), (3, df3, prz3, vl_v3, p3, vh3, vl3, f"{g3}D")]
                        
                        for r_idx, df_s, p_vp, v_vp, p_poc, p_vh, p_vl, nm in cfg:
                            if df_s.empty: continue
                            fig.add_trace(grp.Candlestick(x=df_s.index, open=df_s["Open"].astype(float), high=df_s["High"].astype(float), low=df_s["Low"].astype(float), close=df_s["Close"].astype(float), name=nm), row=r_idx, col=1)
                            
                            if mostra_va and v_vp and max(v_vp) > 0:
                                m_v, d_i, d_f = max(v_vp), df_s.index.min(), df_s.index.max()
                                ext = (d_f - d_i).days
                                step_k = max(1, len(v_vp) // 60)
                                for i in range(0, len(v_vp), step_k):
                                    idx_fine = min(i + step_k, len(v_vp) - 1)
                                    y0_val, y1_val = float(p_vp[i]), float(p_vp[idx_fine])
                                    if y0_val == y1_val:
                                        sp_m = (max(p_vp) - min(p_vp)) * 0.005
                                        y0_val -= sp_m; y1_val += sp_m
                                    w = (float(v_vp[i]) / m_v) * (ext * 0.18) if m_v > 0 else 0
                                    x1_date = d_i + pd.Timedelta(days=int(w) if w > 0 else 1)
                                    col_b = "rgba(242,142,43,0.22)" if p_vl <= p_vp[i] <= p_vh else "rgba(0,165,181,0.08)"
                                    fig.add_shape(type="rect", x0=d_i, x1=x1_date, y0=y0_val, y1=y1_val, fillcolor=col_b, line=dict(width=0), row=r_idx, col=1)
                            
                            dir_s, ic, sl, tp, col_z = ("LONG", "🟢", p_vl*0.985, p_vh, "rgba(40,167,69,0.10)") if p_att >= p_poc else ("SHORT", "🔴", p_vh*1.015, p_vl, "rgba(220,53,69,0.10)")
                            rr = round(abs(tp - p_poc) / abs(p_poc - sl), 2) if abs(p_poc - sl) > 0 else 0
                            data_l_i, data_l_f = df_s.index[int(len(df_s)*0.65)], df_s.index[-1]
                            
                            if mostra_rr:
                                fig.add_shape(type="rect", x0=data_l_i, x1=data_l_f, y0=min(p_poc, tp), y1=max(p_poc, tp), fillcolor=col_z, line=dict(width=0), row=r_idx, col=1)
                                fig.add_shape(type="line", x0=data_l_i, x1=data_l_f, y0=sl, y1=sl, line=dict(color="#ffc107", width=1.5, dash="dash"), row=r_idx, col=1)
                                fig.add_shape(type="line", x0=data_l_i, x1=data_l_f, y0=tp, y1=tp, line=dict(color="#17a2b8", width=2), row=r_idx, col=1)
                                fig.add_annotation(x=data_l_f, y=sl, text=f" SL STOP: {round(sl,2)}", showarrow=False, align="left", bgcolor="#ffc107", font=dict(color="black", size=9), row=r_idx, col=1)
                                fig.add_annotation(x=data_l_f, y=tp, text=f" TP TARGET: {round(tp,2)}", showarrow=False, align="left", bgcolor="#17a2b8", font=dict(color="white", size=9), row=r_idx, col=1)
                            
                            if mostra_poc:
                                fig.add_shape(type="line", x0=df_s.index.min(), x1=data_l_f, y0=p_poc, y1=p_poc, line=dict(color="#dc3545", width=2.5), row=r_idx, col=1)
                                fig.add_annotation(x=data_l_f, y=p_poc, text=f" POC ENTRY: {round(p_poc,2)}", showarrow=False, align="left", bgcolor="#dc3545", font=dict(color="white", size=9, family="Arial Black"), row=r_idx, col=1)
                            
                            txt_leg = f"<b>📊 PROFILO {nm.upper()}</b><br>Direzione: {ic} {dir_s}<br>Rapporto R/R: 1:{rr}<br><br>🔴 POC: {round(p_poc,2)}<br>🟠 VAH: {round(p_vh,2)}<br>🔵 VAL: {round(p_vl,2)}"
                            y_pos_map = {1: 0.97, 2: 0.68, 3: 0.38}
                            fig.add_annotation(xref="paper", yref="paper", x=0.01, y=y_pos_map[r_idx], text=txt_leg, showarrow=False, align="left", bgcolor="rgba(20,24,33,0.95)", bordercolor="rgba(242,142,43,0.5)", borderwidth=1.5, borderpad=10, font=dict(color="white", size=10))
                        
                        # --- TRACCIAMENTO GRAFICO RSI (PANNELLO 4) ---
                        df_recent_rsi = df_c.tail(365)
                        fig.add_trace(grp.Scatter(x=df_recent_rsi.index, y=df_recent_rsi["RSI"], mode="lines", name="RSI", line=dict(color="#c084fc", width=2)), row=4, col=1)
                        
                        fig.add_shape(type="line", x0=df_recent_rsi.index.min(), x1=df_recent_rsi.index[-1], y0=70, y1=70, line=dict(color="rgba(239, 68, 68, 0.5)", width=1.5, dash="dot"), row=4, col=1)
                        fig.add_shape(type="line", x0=df_recent_rsi.index.min(), x1=df_recent_rsi.index[-1], y0=30, y1=30, line=dict(color="rgba(34, 197, 94, 0.5)", width=1.5, dash="dot"), row=4, col=1)
                        fig.update_yaxes(range=[0, 100], row=4, col=1)
                        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False, xaxis3_rangeslider_visible=False, xaxis4_rangeslider_visible=False, height=1800, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{ticker}")
                else:
                st.warning(f"Nessun dato scaricabile da Yahoo Finance per il ticker {ticker}.")


# --- TAB 2: BACKTESTING ---
with tab2:
    st.subheader("⚙️ Motore di Simulazione Storica (Backtest)")
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        bt_ticker = st.text_input("Inserisci un singolo Ticker da testare:", value="AAPL")
        capitale_iniziale = st.number_input("Capitale iniziale ($):", min_value=100, value=10000, step=500)
    with b_col2:
        bt_periodo = st.selectbox("Orizzonte temporale dei dati:", ["1 Anno", "3 Anni", "5 Anni", "Storico Massimo"])
        mappa_periodi = {"1 Anno": "1y", "3 Anni": "3y", "5 Anni": "5y", "Storico Massimo": "max"}
        rischio_trade = st.slider("Rischio percentuale per operazione (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    with b_col3:
        comun_fee = st.number_input("Commissioni per singolo eseguito ($):", min_value=0.0, value=1.99, step=0.5)

    if st.button("🚀 Esegui Backtest Strategia", type="primary"):
        st.info(f"Elaborazione della simulazione algoritmica per {bt_ticker}...")
        df_bt = yf.download(tickers=bt_ticker, period=mappa_periodi[bt_periodo], interval="1d", auto_adjust=False, multi_level_index=False, progress=False)
        if df_bt is not None and len(df_bt) > 60:
            capitale, in_posizione, prezzo_ingresso, livello_sl, livello_tp = capitale_iniziale, False, 0, 0, 0
            equity_curve, date_curve, trade_history = [capitale_iniziale], [df_bt.index], []

            for i in range(50, len(df_bt)):
                df_storico_finora = df_bt.iloc[:i]
                riga_attuale = df_bt.iloc[i]
                prezzo_corrente, data_corrente = float(riga_attuale["Close"]), df_bt.index[i]

                if not in_posizione:
                    p_poc, p_vh, p_vl, _, _ = calc_vp(df_storico_finora)
                    if p_poc is None: continue
                    posizione_tipo = "LONG" if prezzo_corrente >= p_poc else "SHORT"
                    prezzo_ingresso = prezzo_corrente
                    livello_sl, livello_tp = (p_vl * 0.985, p_vh) if posizione_tipo == "LONG" else (p_vh * 1.015, p_vl)

                    if livello_sl > 0 and abs(prezzo_ingresso - livello_sl) > 0:
                        in_posizione = True
                        size_contratti = (capitale * (rischio_trade / 100)) / abs(prezzo_ingresso - livello_sl)
                else:
                    high_g, low_g, uscito, p_chiusura = float(riga_attuale["High"]), float(riga_attuale["Low"]), False, 0
                    if posizione_tipo == "LONG":
                        if low_g <= livello_sl: uscito, p_chiusura = True, livello_sl
                        elif high_g >= livello_tp: uscito, p_chiusura = True, livello_tp
                    elif posizione_tipo == "SHORT":
                        if high_g >= livello_sl: uscito, p_chiusura = True, livello_sl
                        elif low_g >= livello_tp: uscito, p_chiusura = True, livello_tp

                    if uscito:
                        pnl = ((p_chiusura - prezzo_ingresso) if posizione_tipo == "LONG" else (prezzo_ingresso - p_chiusura)) * size_contratti - (comun_fee * 2)
                        capitale += pnl
                        trade_history.append({"Data": data_corrente.strftime("%d/%m/%Y"), "Tipo": posizione_tipo, "Ingresso": round(prezzo_ingresso, 2), "Uscita": round(p_chiusura, 2), "PnL ($)": round(pnl, 2), "Capitale": round(capitale, 2)})
                        equity_curve.append(capitale)
                        date_curve.append(data_corrente)
                        in_posizione = False

            st.subheader("📊 Statistiche di Performance Log")
            if trade_history:
                df_trades = pd.DataFrame(trade_history)
                profitti = df_trades[df_trades["PnL ($)"] > 0]["PnL ($)"].sum()
                perdite = abs(df_trades[df_trades["PnL ($)"] < 0]["PnL ($)"].sum())
                win_rate = round((len(df_trades[df_trades["PnL ($)"] > 0]) / len(df_trades)) * 100, 2)
                profit_factor = round(profitti / perdite, 2) if perdite > 0 else float('inf')
                max_dd = round(abs(((np.array(equity_curve) - np.maximum.accumulate(equity_curve)) / np.maximum.accumulate(equity_curve)).min()) * 100, 2)
                
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Ritorno Totale", f"{round(((capitale - capitale_iniziale) / capitale_iniziale) * 100, 2)} %")
                m_col2.metric("Percentuale Win Rate", f"{win_rate} %")
                m_col3.metric("Profit Factor", f"{profit_factor}")
                m_col4.metric("Massimo Drawdown", f"-{max_dd} %")

                fig_eq = grp.Figure()
                fig_eq.add_trace(grp.Scatter(x=date_curve, y=equity_curve, mode='lines', name='Equity', line=dict(color='#38bdf8', width=2)))
                fig_eq.update_layout(title=f"📈 Andamento dell'Equity Line — {bt_ticker}", template="plotly_dark", height=400)
                st.plotly_chart(fig_eq, use_container_width=True)
                
                # Visualizzazione della Tabella Dati
                st.dataframe(df_trades, use_container_width=True)
                
                # --- STRUTTURA DI ESPORTAZIONE IN CSV COMPATIBILE EXCEL ---
                csv_dati = df_trades.to_csv(index=False).encode('utf-8')
                
                st.markdown(" ") # Spaziatore visivo
                st.download_button(
                    label="📥 Esporta Storico Operazioni (CSV)",
                    data=csv_dati,
                    file_name=f"backtest_{bt_ticker}_{bt_periodo.replace(' ', '_').lower()}.csv",
                    mime="text/csv",
                    key="btn_download_csv"
                )
            else:
                st.warning("Nessuna operazione eseguita nel periodo selezionato con i parametri attuali.")

# --- TAB 3: LIVE ALERTS TELEGRAM BOT ---
with tab3:
    st.subheader("🔔 Canale Notifiche in Tempo Reale via Telegram")
    st.success("✅ Sincronizzazione completata. Algoritmo vettoriale Numpy ad altissima stabilità attivo.")
    
    st.markdown("---")
    st.subheader("📡 Configurazione Selettiva Parametri Scanner")
    
    fl1, fl2, fl3 = st.columns(3)
    with fl1:
        soglia_distanza = st.slider("Seleziona la distanza massima dal POC per inviare l'alert (%):", min_value=0.1, max_value=3.0, value=0.5, step=0.1, key="tg_dist")
    with fl2:
        poc_scelti = st.multiselect("Seleziona quali profili analizzare:", options=["Generale (Inizio)", "Dall'ATH", "Recente (Timeframe)"], default=["Generale (Inizio)", "Dall'ATH", "Recente (Timeframe)"], key="tg_sel_p")
    with fl3:
        orizzonte_recente = st.selectbox("Imposta l'estensione del profilo Recente:", ["3 Mesi", "6 Mesi", "9 Mesi"], index=1, key="tg_oriz_t")
        mappa_giorni_tg = {"3 Mesi": 90, "6 Mesi": 180, "9 Mesi": 270}
        g_recenti_scelti = mappa_giorni_tg[orizzonte_recente]

    p_selezionato_alert = st.selectbox("Seleziona il paniere completo da scansionare:", ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)", "Crypto"], key="tg_paniere")
    lista_ticker_alert = [t.strip() for t in ottieni_paniere(p_selezionato_alert).split(",") if t.strip()]
    
    if st.button("🚀 Attiva Scansione & Invia Alert su Telegram", type="primary"):
        if not poc_scelti:
            st.error("❌ Seleziona almeno una tipologia di POC nei filtri per far partire il monitoraggio.")
        else:
            st.info(f"Avvio scansione globale rapida. Analisi vettoriale di tutti i {len(lista_ticker_alert)} titoli del paniere {p_selezionato_alert}...")
            segnali_trovati = 0
            
            barra_progresso = st.progress(0.0)
            totale_titoli = len(lista_ticker_alert)
            
            for idx, ticker in enumerate(lista_ticker_alert):
                barra_progresso.progress((idx + 1) / totale_titoli)
                
                df_live = yf.download(tickers=ticker, period="max", interval="1d", auto_adjust=False, multi_level_index=False, progress=False, timeout=8)
                if df_live is None or df_live.empty: continue
                
                df_live.columns = [str(c).strip() for c in df_live.columns]
                mappa_colonne = {c.lower(): c for c in df_live.columns}
                
                if 'close' in mappa_colonne and 'high' in mappa_colonne and 'low' in mappa_colonne:
                    p_attuale = float(df_live[mappa_colonne['close']].iloc[-1])
                    
                    d_ath = df_live[mappa_colonne['high']].idxmax()
                    df_generale = df_live.copy()
                    df_ath = df_live.loc[d_ath:].copy()
                    df_recente = df_live.tail(g_recenti_scelti).copy()
                    
                    controlli_da_effettuare = []
                    if "Generale (Inizio)" in poc_scelti: 
                        controlli_da_effettuare.append(("GENERALE (Dall'Inizio)", df_generale))
                    if "Dall'ATH" in poc_scelti: 
                        controlli_da_effettuare.append(("DALL'ATH", df_ath))
                    if "Recente (Timeframe)" in poc_scelti: 
                        controlli_da_effettuare.append((f"RECENTE ({orizzonte_recente})", df_recente))
                        
                    for nome_profilo, df_singolo_profilo in controlli_da_effettuare:
                        if df_singolo_profilo.empty: continue
                        
                        df_input_vp = pd.DataFrame(index=df_singolo_profilo.index)
                        df_input_vp['Open'] = df_singolo_profilo[mappa_colonne.get('open', mappa_colonne['close'])].astype(float)
                        df_input_vp['High'] = df_singolo_profilo[mappa_colonne['high']].astype(float)
                        df_input_vp['Low'] = df_singolo_profilo[mappa_colonne['low']].astype(float)
                        df_input_vp['Close'] = df_singolo_profilo[mappa_colonne['close']].astype(float)
                        df_input_vp['Volume'] = df_singolo_profilo[mappa_colonne.get('volume', df_singolo_profilo.columns)].astype(float)
                        
                        p_poc, p_vh, p_vl, prz_v, vl_v = calc_vp(df_input_vp)
                        if p_poc is None: continue
                        
                        distanza_percentuale = ((p_attuale - p_poc) / p_poc) * 100
                        
                        if abs(distanza_percentuale) <= soglia_distanza:
                            segnali_trovati += 1
                            setup_tipo = "LONG 🟢" if p_attuale >= p_poc else "SHORT 🔴"
                            stop_l = p_vl * 0.985 if p_attuale >= p_poc else p_vh * 1.015
                            take_p = p_vh if p_attuale >= p_poc else p_vl
                            
                            ticker_pulito = str(ticker).replace(".MI", "").strip()
                            
                            if str(ticker).endswith(".MI"):
                                borsa_codice = "MIL"
                            elif "-USD" in str(ticker):
                                borsa_codice = "COINBASE"
                                ticker_pulito = ticker_pulito.replace("-", "")
                            else:
                                borsa_codice = "NASDAQ" if p_selezionato_alert == "NASDAQ 100" else "NYSE"
                            
                            url_stringa_pura = f"https://tradingview.com{borsa_codice}-{ticker_pulito}/"
                            
                            messaggio_alert = (
                                f"📐 <b>SEGNALE TRIPLE-POC RILEVATO</b>\n\n"
                                f"🎯 <b>Ticker:</b> #{ticker_pulito}\n"
                                f"🗂️ <b>Profilo Volume:</b> {nome_profilo}\n"
                                f"⚡ <b>Setup Operativo:</b> {setup_tipo}\n\n"
                                f"📊 <b>Prezzo Attuale:</b> {round(p_attuale, 2)} USD\n"
                                f"🔴 <b>Entry POC Esatto:</b> {round(p_poc, 2)}\n"
                                f"🟠 <b>Stop Loss (VAL/VAH):</b> {round(stop_l, 2)}\n"
                                f"🔵 <b>Take Profit (VAH/VAL):</b> {round(take_p, 2)}\n\n"
                                f"🔗 <b>APRI IL GRAFICO SU TRADINGVIEW:</b>\n{url_stringa_pura}"
                            )
                            invia_messaggio_telegram_sbloccato(T_ID, messaggio_alert)
                            
            st.success(f"Scansione terminata con successo! Inviati {segnali_trovati} segnali precisi su Telegram.")
