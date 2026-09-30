def avvia_scansione():
    print("Inizio scansione giornaliera...")
    
    # --- TEST DI CONNESSIONE TELEGRAM ---
    # Questo messaggio DEVE arrivare. Se non arriva, il problema è il Token o la Chat ID.
    test_invio = invia_messaggio_telegram(T_ID, "🚀 <b>POC Scanner avviato su GitHub!</b> Test di connessione in corso...")
    if test_invio:
        print("✅ Messaggio di test inviato correttamente su Telegram.")
    else:
        print("❌ ERRORE: Impossibile inviare il messaggio su Telegram. Verifica il Token Bot o la Chat ID.")
    
    lista_ticker = [t.strip() for t in SP500_FULL.split(",") if t.strip()]
    segnali_rilevati = 0
    
    for ticker in lista_ticker:
        try:
            df_live = yf.download(tickers=ticker, period="max", interval="1d", auto_adjust=False, multi_level_index=False, progress=False, timeout=10)
            if df_live is None or df_live.empty: 
                continue
            
            df_live.columns = [str(c).strip().lower() for c in df_live.columns]
            
            colonne_necessarie = ['close', 'high', 'low', 'open', 'volume']
            if not all(col in df_live.columns for col in colonne_necessarie):
                continue
                
            p_attuale = float(df_live['close'].iloc[-1])
            d_ath = df_live['high'].idxmax()
            
            profili = {
                "GENERALE": df_live.copy(),
                "ATH": df_live.loc[d_ath:].copy(),
                "RECENTE": df_live.tail(GIORNI_RECENTI).copy()
            }
            
            for nome_profilo, df_singolo in profili.items():
                if df_singolo.empty: continue
                
                df_input_vp = pd.DataFrame(index=df_singolo.index)
                df_input_vp['Open'] = df_singolo['open'].astype(float)
                df_input_vp['High'] = df_singolo['high'].astype(float)
                df_input_vp['Low'] = df_singolo['low'].astype(float)
                df_input_vp['Close'] = df_singolo['close'].astype(float)
                df_input_vp['Volume'] = df_singolo['volume'].astype(float)
                
                p_poc, p_vh, p_vl, _, _ = calc_vp(df_input_vp)
                if p_poc is None: continue
                
                distanza_percentuale = ((p_attuale - p_poc) / p_poc) * 100
                
                # Monitoriamo i calcoli stampando i primi 10 ticker estratti
                if segnali_rilevati < 5:
                     print(f"Ticker: {ticker} | Prezzo: {round(p_attuale,2)} | POC {nome_profilo}: {round(p_poc,2)} | Distanza: {round(distanza_percentuale,2)}%")
                
                if abs(distanza_percentuale) <= SOGLIA_DISTANZA:
                    segnali_rilevati += 1
                    setup_tipo = "LONG 🟢" if p_attuale >= p_poc else "SHORT 🔴"
                    stop_l = p_vl * 0.985 if p_attuale >= p_poc else p_vh * 1.015
                    take_p = p_vh if p_attuale >= p_poc else p_vl
                    
                    borsa = "NASDAQ" if PANIERE_SELEZIONATO == "NASDAQ 100" else "NYSE"
                    url_tv = f"https://tradingview.com{borsa}-{ticker}/"
                    
                    messaggio = (
                        f"📐 <b>AUTOMAZIONE: TRIPLE-POC RILEVATO</b>\n\n"
                        f"🎯 <b>Ticker:</b> #{ticker}\n"
                        f"🗂️ <b>Profilo Volume:</b> {nome_profilo}\n"
                        f"⚡ <b>Setup Operativo:</b> {setup_tipo}\n\n"
                        f"📊 <b>Prezzo Attuale:</b> {round(p_attuale, 2)} USD\n"
                        f"🔴 <b>Entry POC Esatto:</b> {round(p_poc, 2)}\n"
                        f"🟠 <b>Stop Loss (VAL/VAH):</b> {round(stop_l, 2)}\n"
                        f"🔵 <b>Take Profit (VAH/VAL):</b> {round(take_p, 2)}\n\n"
                        f"🔗 <a href='{url_tv}'>APRI IL GRAFICO SU TRADINGVIEW</a>"
                    )
                    invia_messaggio_telegram(T_ID, messaggio)
        except Exception as e:
            pass
            
    print(f"Scansione terminata. Segnali inviati: {segnali_rilevati}")
