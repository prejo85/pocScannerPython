import os
import multiprocessing
import pandas as pd
import plotly.graph_objects as grp
from plotly.subplots import make_subplots
import yfinance as yf
from ipywidgets import Button, Dropdown, HBox, Output, Textarea, VBox
from google.colab import drive
from tqdm.notebook import tqdm
import requests
from io import StringIO

# --- Global Variable ---
G_HTML_FILES = []

# --- Helper Functions (Top-Level for Multiprocessing) ---

def calc_vp(df, div=40):
    if df.empty: return None, None, None, [], []

    p_min, p_max = float(df['Low'].min()), float(df['High'].max())
    if p_max - p_min == 0: # Handle cases where min and max price are the same
        return p_min, p_min, p_min, [], []

    step = (p_max - p_min) / div
    gr = [p_min + (i * step) for i in range(div + 1)]
    vols = [0.0] * div

    for _, r in df.iterrows():
        # Access values directly, as r is a Series representing a row
        low_val = float(r['Low'])
        high_val = float(r['High'])
        volume_val = float(r['Volume'])

        for i in range(div):
            if low_val <= gr[i+1] and high_val >= gr[i]:
                vols[i] += volume_val

    if not vols or max(vols) == 0: # Handle case with no volume or all zero volume
        # Return default values or values indicating no meaningful POC
        return p_min + step/2, p_max, p_min, [(gr[i] + gr[i+1])/2 for i in range(div)], vols

    poc_idx = vols.index(max(vols))
    poc = gr[poc_idx] + (step / 2)
    v_tot, v_tgt, idx_b, idx_a, v_curr = sum(vols), sum(vols) * 0.7, poc_idx, poc_idx, max(vols)

    # Calculate Value Area
    while v_curr < v_tgt:
        v_s = vols[idx_b - 1] if idx_b > 0 else 0
        v_p = vols[idx_a + 1] if idx_a < div - 1 else 0
        if v_s == 0 and v_p == 0: break # No more volume to add
        if v_s >= v_p:
            idx_b -= 1
            v_curr += v_s
        else:
            idx_a += 1
            v_curr += v_p

    # Ensure idx_a and idx_b are within bounds
    vah = gr[min(idx_a + 1, len(gr) - 1)]
    val = gr[max(idx_b, 0)]

    return poc, vah, val, [(gr[i] + gr[i + 1]) / 2 for i in range(len(vols))], vols

def process_single_ticker(args):
    ticker, asset_type, period_value = args

    tk_yf = ticker + "-USD" if asset_type == "Criptovaluta" and not ticker.endswith("-USD") else ticker

    try:
        df_c = yf.download(tickers=tk_yf, period="max", interval="1d", auto_adjust=True, multi_level_index=False, progress=False)
        if df_c is None or df_c.empty:
            print(f"❌ Errore nello scaricamento dei dati per {tk_yf}.")
            return None

        p_att = float(df_c["Close"].iloc[-1])
        g3 = {"1mo": 30, "3mo": 90, "6mo": 180}.get(period_value, 90)

        df1 = df_c.copy()
        d_ath = df_c["High"].idxmax()
        df2 = df_c.loc[d_ath:].copy()
        df3 = df_c.tail(g3).copy()

        p1, vh1, vl1, prz1, vl_v1 = calc_vp(df1)
        p2, vh2, vl2, prz2, vl_v2 = calc_vp(df2)
        p3, vh3, vl3, prz3, vl_v3 = calc_vp(df3)

        # Skip if any calc_vp returned None (e.g., empty dataframe for a period)
        if None in [p1, vh1, vl1, p2, vh2, vl2, p3, vh3, vl3]:
            print(f"⚠️ Skipped {tk_yf} due to insufficient data for POC calculation in one or more periods.")
            return None

        fig = make_subplots(rows=3, cols=1, subplot_titles=("1. STORICO COMPLETO", f"2. DALL'ATH ({d_ath.strftime('%d/%m/%Y')})", f"3. ULTIMI {g3} GIORNI"), vertical_spacing=0.06)
        cfg = [(1, df1, prz1, vl_v1, p1, vh1, vl1, "Generale"), (2, df2, prz2, vl_v2, p2, vh2, vl2, "ATH"), (3, df3, prz3, vl_v3, p3, vh3, vl3, f"{g3}D")]

        for r_idx, df_s, p_vp, v_vp, p_poc, p_vh, p_vl, nm in cfg:
            if df_s.empty: continue # Skip if dataframe for this period is empty

            fig.add_trace(grp.Candlestick(x=df_s.index, open=df_s["Open"].astype(float), high=df_s["High"].astype(float), low=df_s["Low"].astype(float), close=df_s["Close"].astype(float), name=nm), row=r_idx, col=1)

            if v_vp and max(v_vp) > 0: # Only draw volume profile if there's actual volume data
                m_v, d_i, d_f = max(v_vp), df_s.index.min(), df_s.index.max()
                # Ensure d_i and d_f are datetime objects for subtraction
                if isinstance(d_i, pd.Timestamp): d_i = d_i.to_pydatetime()
                if isinstance(d_f, pd.Timestamp): d_f = d_f.to_pydatetime()
                ext = (d_f - d_i).days

                for i in range(len(v_vp)):
                    # Avoid division by zero if m_v is 0
                    w = (float(v_vp[i]) / m_v) * (ext * 0.12) if m_v > 0 else 0
                    x1_date = d_i + pd.Timedelta(days=int(w) if w > 0 else 1)
                    # Ensure x0 and x1 are within the df_s index range
                    fig.add_shape(type="rect", x0=d_i, x1=x1_date, y0=float(p_vp[i])*0.997, y1=float(p_vp[i])*1.003, fillcolor="rgba(0,165,181,0.1)", line=dict(width=0), row=r_idx, col=1)

            dir_s, ic, sl, tp, col_z = ("LONG", "🟢", p_vl*0.985, p_vh, "rgba(40,167,69,0.12)") if p_att >= p_poc else ("SHORT", "🔴", p_vh*1.015, p_vl, "rgba(220,53,69,0.12)")
            rr = round(abs(tp - p_poc) / abs(p_poc - sl), 2) if abs(p_poc - sl) > 0 else 0

            fig.add_shape(type="rect", x0=df_s.index.min(), x1=df_s.index.max(), y0=min(p_poc, tp), y1=max(p_poc, tp), fillcolor=col_z, line=dict(width=0), row=r_idx, col=1)
            fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index.max(), y0=p_poc, y1=p_poc, line=dict(color="red", width=2, dash="dash"), row=r_idx, col=1)
            fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index.max(), y0=sl, y1=sl, line=dict(color="orange", width=1.5, dash="dot"), row=r_idx, col=1)
            fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index.max(), y0=tp, y1=tp, line=dict(color="cyan", width=1.5), row=r_idx, col=1)
            fig.add_shape(type="line", x0=df_s.index.min(), x1=df_s.index.max(), y0=p_att, y1=p_att, line=dict(color="#28a745", width=1.5), row=r_idx, col=1)
            fig.add_annotation(x=df_s.index.max(), y=p_poc, text=f"ENTRY: {round(p_poc,2)}", showarrow=False, bgcolor="red", font=dict(color="white", size=8), row=r_idx, col=1)
            fig.add_annotation(x=df_s.index.max(), y=sl, text=f"STOP: {round(sl,2)}", showarrow=False, bgcolor="orange", font=dict(color="white", size=8), row=r_idx, col=1)
            fig.add_annotation(x=df_s.index.max(), y=tp, text=f"TARGET: {round(tp,2)}", showarrow=False, bgcolor="cyan", font=dict(color="black", size=8), row=r_idx, col=1)
            txt_leg = f"<b>📊 {nm.upper()}</b><br>Dir: {ic} {dir_s}<br>R/R: 1:{rr}<br>🔴 ENTRY: {round(p_poc,2)}<br>🟠 STOP: {round(sl,2)}<br>🔵 TARGET: {round(tp,2)}"
            fig.add_annotation(xref="paper", yref="paper", x=0.01, y=0.93 if r_idx==1 else (0.59 if r_idx==2 else 0.26), text=txt_leg, showarrow=False, align="left", bgcolor="rgba(15,18,24,0.93)", bordercolor="rgba(0,165,181,0.6)", borderwidth=1.5, borderpad=8, font=dict(color="white", size=10))

        fig.update_layout(title=f"📐 ANALISI TRIPLE-POC — {ticker}", template="plotly_dark", xaxis_rangeslider_visible=False, xaxis2_rangeslider_visible=False, xaxis3_rangeslider_visible=False, height=1400, showlegend=False)

        html_filename = f"setup_operativo_completo_{ticker}.html"
        fig.write_html(html_filename)
        return html_filename
    except Exception as e:
        print(f"❌ Errore durante l'elaborazione di {tk_yf}: {e}")
        return None

def save_dr(b):
    global A_gr
    # Re-initialize A_gr if it's not present (e.g., if this cell is run out of order)
    if 'A_gr' not in globals():
        A_gr = Output()

    with A_gr:
        if not G_HTML_FILES:
            print("❌ Nessun grafico generato da salvare. Esegui prima l'analisi!")
            return
        try:
            print("Mounting Google Drive...")
            drive.mount("/content/drive", force_remount=True)
            for filename in G_HTML_FILES:
                print(f"Copying {filename} to Google Drive...")
                os.system(f"cp {filename} '/content/drive/MyDrive/'")
                print(f"🎉 '{filename}' SALVATO SU DRIVE!")
        except Exception as e:
            print(f"❌ Errore Drive: {e}")

# --- Main Functions ---

def run_an(b):
    global G_HTML_FILES
    G_HTML_FILES = [] # Reset the list at the beginning of each execution

    with A_gr:
        A_gr.clear_output()

        # Ensure I_tp is explicitly set to 'Azione' for S&P 500 stocks
        I_tp.value = "Azione"

        tickers_input = I_tk.value.upper().strip()
        tickers = [t.strip() for t in tickers_input.split(',') if t.strip()]
        if not tickers:
            print("❌ Nessun ticker inserito.")
            return

        print(f"🔄 Avvio analisi per {len(tickers)} ticker S&P 500. Questo processo potrebbe richiedere molto tempo...")

        # Prepare arguments for multiprocessing
        task_args = [(t, I_tp.value, I_pe.value) for t in tickers]

        # Use multiprocessing Pool
        num_processes = min(4, os.cpu_count() if os.cpu_count() else 1) # Limit to 4 for stability in Colab

        results = []
        with multiprocessing.Pool(processes=num_processes) as pool:
            # Use tqdm for a progress bar
            for filename in tqdm(pool.imap_unordered(process_single_ticker, task_args), total=len(tickers), desc="Analisi Ticker S&P 500"):
                if filename:
                    results.append(filename)

        G_HTML_FILES.extend(results)

        if G_HTML_FILES:
            print("🎉 Tutti i grafici sono stati generati! Ora salveremo su Google Drive.")
            # Call save_dr automatically after analysis
            save_dr(None) # Pass None as event argument since it's not a button click
        else:
            print("❌ Nessun grafico è stato generato con successo.")

def run_bt(b):
    with A_gr:
        A_gr.clear_output()
        print("Funzione run_bt chiamata. Implementazione in sospeso.")

def run_ex(b):
    with A_gr:
        A_gr.clear_output()
        print("Funzione run_ex chiamata. Implementazione in sospeso.")

def run_al(b):
    with A_gr:
        A_gr.clear_output()
        print("Funzione run_al chiamata. Implementazione in sospeso.")

def forza_test(b):
    with A_gr:
        A_gr.clear_output()
        print("Funzione forza_test chiamata. Implementazione in sospeso.")

# --- Widget Initialization ---

# Fallback for sp500_tickers_string if not globally available (e.g., kernel restart)
if 'sp500_tickers_string' not in globals():
    print("Warning: sp500_tickers_string not found. Attempting to re-fetch S&P 500 tickers.")
    wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(wiki_url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
        tables = pd.read_html(StringIO(html_content))
        sp500_table = None
        for table in tables:
            if 'Symbol' in table.columns:
                sp500_table = table
                break
        if sp500_table is not None:
            sp500_tickers_string = ",".join(sp500_table['Symbol'].tolist())
            print(f"Re-fetched {len(sp500_table['Symbol'])} ticker S&P 500.")
        else:
            sp500_tickers_string = "AAPL,MSFT" # Default if fetching fails
            print("Could not find S&P 500 tickers table. Using default tickers.")
    except Exception as e:
        sp500_tickers_string = "AAPL,MSFT" # Default if fetching fails
        print(f"Error re-fetching S&P 500 tickers: {e}. Using default tickers.")


I_tk = Textarea(value=sp500_tickers_string, description="Tickers (separati da virgola):")
I_tp = Dropdown(options=["Criptovaluta", "Azione"], value="Azione", description="Tipo:") # Set to 'Azione' by default
I_pe = Dropdown(options=[("1 Mese", "1mo"), ("3 Mesi", "3mo"), ("6 Mesi", "6mo")], value="3mo", description="Periodo:")
B_an = Button(description="🔍 Genera 3 Grafici", button_style="success")
B_dr = Button(description="💾 Salva su Drive", button_style="warning")
# Placeholder buttons for other functionalities
B_bt = Button(description="🔙 Backtest (WIP)", button_style="info")
B_ex = Button(description="📈 Esporta (WIP)", button_style="info")
B_al = Button(description="🔔 Crea Alert (WIP)", button_style="info")
B_ft = Button(description="🎯 Forza Test (WIP)", button_style="info")
A_gr = Output()

# --- Widget Event Handlers ---
B_an.on_click(run_an)
B_dr.on_click(save_dr)
B_bt.on_click(run_bt)
B_ex.on_click(run_ex)
B_al.on_click(run_al)
B_ft.on_click(forza_test)

# --- Display Widgets ---
display(VBox([
    HBox([I_tk, I_tp, I_pe]),
    HBox([B_an, B_dr, B_bt, B_ex, B_al, B_ft]),
    A_gr
]))

print("Environment setup complete. All functions and widgets are initialized.")