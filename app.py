import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Financial Volatility Studio", layout="wide")

st.title("📈 Financial Analysis & Volatility Studio")
st.markdown("""
Questa applicazione consente di analizzare i mercati finanziari scaricando i dati storici 
da **Yahoo Finance** ed esplorando i rendimenti, le distribuzioni e la volatilità tramite il modello **GARCH**.
""")

# --- SIDEBAR: Input Utente ---
st.sidebar.header("🔧 Impostazioni dei Dati")
ticker = st.sidebar.text_input("Ticker Yahoo Finance (es. AAPL, ^GSPC, BTC-USD)", value="^GSPC")
start_date = st.sidebar.date_input("Data di Inizio", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("Data di Fine", value=pd.to_datetime("today"))

st.sidebar.header("📊 Parametri GARCH(p, q)")
p = st.sidebar.slider("Ordine Autoregressivo (p)", min_value=1, max_value=5, value=1)
q = st.sidebar.slider("Ordine Media Mobile (q)", min_value=1, max_value=5, value=1)

# --- Caricamento Dati ---
@st.cache_data
def load_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end)
    return data

try:
    data = load_data(ticker, start_date, end_date)
    
    if data.empty:
        st.error("Nessun dato trovato per il ticker inserito. Verifica il simbolo.")
    else:
        # Calcolo dei rendimenti logaritmici percentuali
        close_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
        data['Returns'] = 100 * np.log(data[close_col] / data[close_col].shift(1))
        data = data.dropna()

        # --- CREAZIONE DEI TAB ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Prezzi di Chiusura", 
            "📊 Rendimenti Logaritmici", 
            "📉 Distribuzione Rendimenti", 
            "🔮 Modello GARCH"
        ])

        # TAB 1: Prezzi di Chiusura
        with tab1:
            st.subheader(f"Andamento Storico dei Prezzi - {ticker}")
            fig_p, ax_p = plt.subplots(figsize=(12, 5))
            ax_p.plot(data.index, data[close_col], color='blue', label=ticker)
            ax_p.set_ylabel("Prezzo")
            ax_p.grid(True)
            st.pyplot(fig_p)

        # TAB 2: Rendimenti Logaritmici
        with tab2:
            st.subheader("Rendimenti Logaritmici Giornalieri (%)")
            fig_r, ax_r = plt.subplots(figsize=(12, 5))
            ax_r.plot(data.index, data['Returns'], color='orange', label='Rendimenti %')
            ax_r.set_ylabel("Rendimento (%)")
            ax_r.grid(True)
            st.pyplot(fig_r)

        # TAB 3: Distribuzione Rendimenti
        with tab3:
            st.subheader("Istogramma della Distribuzione dei Rendimenti")
            fig_d, ax_d = plt.subplots(figsize=(12, 5))
            ax_d.hist(data['Returns'], bins=50, density=True, alpha=0.6, color='purple', edgecolor='black')
            ax_d.set_xlabel("Rendimento (%)")
            ax_d.set_ylabel("Densità")
            ax_d.grid(True)
            st.pyplot(fig_d)

        # TAB 4: Modello GARCH
        with tab4:
            st.subheader(f"Analisi della Volatilità con il Modello GARCH({p},{q})")
            
            # Layout interno al Tab 4 per separare Grafico e Dati
            col_graph, col_coeff = st.columns([2, 1])
            
            # Stima del modello GARCH
            model = arch_model(data['Returns'], p=p, q=q, vol='Garch', dist='normal')
            res = model.fit(disp='off')
            
            # Volatilità condizionale annualizzata
            cond_vol = res.conditional_volatility * np.sqrt(252)

            with col_graph:
                st.markdown("**Volatilità Condizionale Annualizzata (%)**")
                fig_v, ax_v = plt.subplots(figsize=(10, 5))
                ax_v.plot(data.index, cond_vol, color='red', label='Volatilità GARCH')
                ax_v.set_ylabel("Volatilità (%)")
                ax_v.grid(True)
                st.pyplot(fig_v)

            with col_coeff:
                st.markdown("**Coefficienti Stimati**")
                st.dataframe(res.params.to_frame(name="Valore"), use_container_width=True)
            
            # Riepilogo statistico completo
            st.markdown("---")
            st.markdown("**Output Completo del Modello (Summary)**")
            st.text(str(res.summary()))

except Exception as e:
    st.info("Configura i parametri nella barra laterale o verifica la connessione a Yahoo Finance.")
    st.error(f"Dettaglio Errore: {e}")
