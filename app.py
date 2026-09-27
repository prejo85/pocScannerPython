import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as grp
from plotly.subplots import make_subplots
import requests
from io import StringIO

# Impostazione della pagina web a tutto schermo e tema scuro nativo
st.set_page_config(layout="wide", page_title="Dashboard Finanziaria Triple-POC")

st.title("📐 Dashboard Finanziaria — Analisi Triple-POC")

# Creazione delle schede interattive web
tab1, tab2, tab3 = st.tabs(["Analisi Triple-POC", "Backtesting", "Alert Telegram"])

# --- FUNZIONI DI RECUPERO AUTOMATICO DEI PANIERI DA WIKIPEDIA ---

@st.cache_data(ttl=86400)  # Memorizza i dati per 24 ore per velocizzare il sito
def carica_paniere_automatico(indice_scelto):
    """Preleva i ticker aggiornati da Wikipedia senza inserirli a mano."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    if indice_scelto == "S&P 500":
        url = "https://wikipedia.org"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            df = pd.read_html(StringIO(r.text))[0]
            # Sostituisce i punti con i trattini richiesti da yFinance (es. BRK.B -> BRK-B)
            lista = [t.replace('.', '-') for t in df['Symbol'].tolist()]
            return ",".join(lista)
        except:
            return "AAPL,MSFT,GOOGL"

    elif indice_scelto == "NASDAQ 100":
        url = "https://wikipedia.org"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            # Cerca la tabella corretta dei componenti nella pagina del Nasdaq-100
            tabelle = pd.read_html(StringIO(r.text))
            for tab in tabelle:
                if 'Ticker' in tab.columns:
                    return ",".join(tab['Ticker'].tolist())
        except:
            return "AAPL,MSFT,NVDA"

    elif indice_scelto == "FTSE MIB (FIB)":
        url = "https://wikipedia.org"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            df = pd.read_html(StringIO(r.text))[1] # Generalmente la seconda tabella
            # Aggiunge il suffisso .MI richiesto da yFinance per la borsa di Milano (es. ENI -> ENI.MI)
            lista = [f"{t.strip()}.MI" for t in df['Ticker'].tolist()]
            return ",".join(lista)
        except:
            return "ENI.MI,RACE.MI,UCG.MI"
            
    return ""

# --- Funzione helper per il calcolo del Volume Profile e del POC ---
def calc_vp(df, div=40):
    if df.empty: return None, None, None, [], []
    p_min, p_max = float(df['Low'].min()), float(df['High'].max())
    if p_max - p_min == 0: return p_min, p_min, p_min, [], []
    
    step = (p_max - p_min) / div
    gr = [p_min + (i * step) for i in range(div + 1)]
    vols = [0.0] * div

    for _, r in df.iterrows():
        low_val, high_val, volume_val = float(r['Low']), float(r['High']), float(r['Volume'])
        for i in range(div):
            if low_val <= gr[i+1] and high_val >= gr[i]:
                vols[i] += volume_val

    if not vols or max(vols) == 0:
        return p_min + step/2, p_max, p_min, [(gr[i] + gr[i+1])/2 for i in range(div)], vols

    poc_idx = vols.index(max(vols))
    poc = gr[poc_idx] + (step / 2)
    v_tot, v_tgt, idx_b, idx_a, v_curr = sum(vols), sum(vols) * 0.7, poc_idx, poc_idx, max(vols)

    while v_curr < v_tgt:
        v_s = vols[idx_b - 1] if idx_b > 0 else 0
        v_p = vols[idx_a + 1] if idx_a < div - 1 else 0
        if v_s == 0 and v_p == 0: break
        if v_s >= v_p: idx_b -= 1; v_curr += v_s
        else: idx_a += 1; v_curr += v_p

    return poc, gr[min(idx_a + 1, len(gr) - 1)], gr[max(idx_b, 0)], [(gr[i] + gr[i + 1]) / 2 for i in range(len(vols))], vols
# --- TAB 1: ANALISI TRIPLE-POC ---
with tab1:
    st.subheader("Configurazione Parametri di Scansione")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Selettore dinamico del paniere di mercato
        paniere_selezionato = st.selectbox("Seleziona Indice/Paniere:", ["S&P 500", "NASDAQ 100", "FTSE MIB (FIB)"])
        # Scarica i dati in background basandosi sulla selezione
        ticker_caricati = carica_paniere_automatico(paniere_selezionato)
        
    with col2:
        asset_type = st.selectbox("Tipo Asset:", ["Azione", "Criptovaluta"])
        
    with col3:
        period_label = st.selectbox("Periodo Analisi Recente:", ["1 Mese", "3 Mesi", "6 Mesi"])
        period_map = {"1 Mese": "1mo", "3 Mesi": "3mo", "6 Mesi": "6mo"}
        period_value = period_map[period_label]

    # Il box di testo mostra l'elenco estratto e permette modifiche manuali prima dell'invio
    tickers_input = st.text_area("Modifica o verifica i Tickers estratti (separati da virgola):", value=ticker_caricati, height=150)

    if st.button("🔍 Avvia Analisi Grafica Nodes", type="primary"):
        tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
        
        if not tickers:
            st.warning("Inserisci almeno un ticker valido.")
        else:
            st.success(f"Analisi avviata per {len(tickers)} elementi. I grafici appariranno in sequenza qui sotto.")
            
            for ticker in tickers:
                tk_yf = ticker + "-USD" if asset_type == "Criptovaluta" and not ticker.endswith("-USD") else ticker
                st.write(f"🔄 Download dati storici in corso per: **{tk_yf}**...")
                
                df_c = yf.download(tickers=tk_yf, period="max", interval="1d", auto_adjust=True, progress=False)
                
                if df_c is not None and not df_c.empty:
                    if isinstance(df_c.columns, pd.MultiIndex):
                        df_c.columns = df_c.columns.get_level_values(0)
                        
                    close_series = df_c["Close"]
                    p_att = float(close_series.values[-1] if hasattr(close_series, 'values') else close_series.iloc[-1])
                    g3 = {"1mo": 30, "3mo": 90, "6mo": 180}.get(period_value, 90)
                    
                    df1 = df_c.copy()
                    d_ath = df_c["High"].idxmax()
                    df2 = df_c.loc[d_ath:].copy()
                    df3 = df_c.tail(g3).copy()
                    
                    p1, vh1, vl1, prz1, vl_v1 = calc_vp(df1)
                    p2, vh2, vl2, prz2, vl_v2 = calc_vp(df2)
                    p3, vh3, vl3, prz3, vl_v3 = calc_vp(df3)
                    
                    if None in [p1, vh1, vl1, p2, vh2, vl2, p3, vh3, vl3]:
                        continue
                    
                    fig = make_subplots(rows=3, cols=1, subplot_titles=(f"1. STORICO COMPLETO ({ticker})", f"2. DALL'ATH ({d_ath.strftime('%d/%m/%Y')})", f"3. ULTIMI {g3} GIORNI"), vertical_spacing=0.06)
                    cfg = [(1, df1, prz1, vl_v1, p1, vh1, vl1, "Generale"), (2, df2, prz2, vl_v2, p2, vh2, vl2, "ATH"), (3, df3, prz3, vl_v3, p3, vh3, vl3, f"{g3}D")]
                    
                    for r_idx, df_s, p_vp, v_vp, p_poc, p_vh, p_vl, nm in cfg:
                        if df_s.empty: continue
                        
                        fig.add_trace(grp.Candlestick(x=df_s.index, open=df_s["Open"].astype(float), high=df_s["High"].astype(float), low=df_s["Low"].astype(float), close=df_s["Close"].astype(float), name=nm), row=r_idx, col=1)
                        
                        if v_vp and max(v_vp) > 0:
                            m_v, d_i, d_f = max(v_vp), df_s.index.min(), df_s.index.max()
                            ext = (d_f - d_i).days
                            for i in range(len(v_vp)):
                                w = (float(v_vp[i]) / m_v) * (ext * 0.12) if m_v > 0 else 0
                                x1_date = d_i + pd.Timedelta(days=int(w) if w > 0 else 1)
                                fig.add_shape(type="rect", x0=d_i, x1=x1_date, y0=float(p_vp[i])*0.997, y1=float(p_vp[i])*1.003, fillcolor="rgba(0,165,181,0.1)", line=dict(width=0), row=r_idx, col=1)
                        
                        dir_s, ic, sl, tp, col_z = ("LONG", "🟢", p_vl*0.985, p_vh, "rgba(40,167,69,0.12)") if p_att >= p_poc else ("SHORT", "🔴", p_vh*1.015, p_vl, "rgba(220,53,69,0.12)")
                        rr = round(abs(tp - p_poc) / abs(p_poc - sl), 2) if abs(p_poc - sl) > 0 else 0
                        
                        fig.add_shape(type="rect", x0=df_s.index.min(), x1=df_s.index.max(), y0=min(p_poc, tp), y1=max(p_poc, tp), fillcolor=col_z, line=dict(width=0), row=r_idx, col=1)
                        fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index.max(), y0=p_poc, y1=p_poc, line=dict(color="red", width=2, dash="dash"), row=r_idx, col=1)
                        fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index.max(), y0=sl, y1=sl, line=dict(color="orange", width=1.5, dash="dot"), row=r_idx, col=1)
                        fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index.max(), y0=tp, y1=tp, line=dict(color="cyan", width=1.5), row=r_idx, col=1)
                        
                        fig.add_annotation(x=df_s.index.max(), y=p_poc, text=f"ENTRY: {round(p_poc,2)}", showarrow=False, bgcolor="red", font=dict(color="white", size=8), row=r_idx, col=1)
                        fig.add_annotation(x=df_s.index.max(), y=sl, text=f"STOP: {round(sl,2)}", showarrow=False, bgcolor="orange", font=dict(color="white", size=8), row=r_idx, col=1)
                        fig.add_annotation(x=df_s.index.max(), y=tp, text=f"TARGET: {round(tp,2)}", showarrow=False, bgcolor="cyan", font=dict(color="black", size=8), row=r_idx, col=1)
                        
                        txt_leg = f"<b>📊 {nm.upper()}</b><br>Dir: {ic} {dir_s}<br>R/R: 1:{rr}<br>🔴 ENTRY: {round(p_poc,2)}<br>🟠 STOP: {round(sl,2)}<br>🔵 TARGET: {round(tp,2)}"
                        fig.add_annotation(xref="paper", yref="paper", x=0.01, y=0.93 if r_idx==1 else (0.59 if r_idx==2 else 0.26), text=txt_leg, showarrow=False, align="left", bgcolor="rgba(15,18,24,0.93)", bordercolor="rgba(0,165,181,0.6)", borderwidth=1.5, borderpad=8, font=dict(color="white", size=10))
                    
                    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False, xaxis3_rangeslider_visible=False, height=1300, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"❌ Impossibile scaricare o elaborare i dati per {ticker}.")

# --- TAB 2 & 3: SEZIONI WIP ---
with tab2:
    st.info("📊 Sezione Backtesting: Lo sviluppo dell'algoritmo è attualmente in corso (WIP).")

with tab3:
    st.info("🔔 Sezione Telegram Bot: Configurazione dei canali di alert automatici in corso (WIP).")
