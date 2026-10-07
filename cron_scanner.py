import pandas as pd
import numpy as np
import yfinance as yf
import requests
import json
import os

# CREDENZIALI E CONFIGURAZIONI NATIVE
T_ID = "2072895073"
TESTA_INTERNET = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
}

# --- 1. SEZIONE DATABASE PANIERI AGGIORNATO 2026 ---

SP500_FULL = (
    "MMM,AOS,ABT,ABBV,ACN,ADBE,AMD,AES,AFL,A,APD,ABNB,AKAM,ALB,ARE,ALGN,ALLE,LNT,ALL,GOOGL,GOOG,MO,AMZN,AMCR,AEE,"
    "AEP,AXP,AIG,AMT,AWK,AMP,AME,AMGN,APH,ADI,AON,APA,APO,AAPL,AMAT,APP,APTV,ACGL,ADM,ARES,ANET,AJG,AIZ,T,ATO,ADSK,"
    "ADP,AZO,AVY,AXON,BKR,BALL,BAC,BAX,BDX,BRK-B,BBY,TECH,BIIB,BLK,BX,BE,BNY,BA,BKNG,BSX,BMY,AVGO,BR,BRO,BF-B,BG,"
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
    "MDLZ,ADI,ADP,ADSK,AAL,ALGN,AMAT,AMD,AMGN,AMZN,ANSS,ASML,TEAM,ADBE,BIIB,BMRN,BKNG,AVGO,CDNS,CDW,CHTR,"
    "CHKP,CTAS,CSCO,CTSH,CMCSA,CPRT,COST,CRWD,DLTR,DXCM,EBAY,EA,EXPE,FAST,META,FI,FOXA,FOX,GILD,GOOGL,GOOG,"
    "IDXX,ILMN,INCY,INTC,INTU,ISRG,JBHT,JD,KDP,KLAC,KHC,LRCX,LULU,MELI,MAR,MTCH,MCHP,MU,MSFT,MRNA,MNST,"
    "NTES,NFLX,NVDA,NXPI,ORLY,OKTA,ODFL,PCAR,PAYX,PYPL,PEP,PDD,REGN,ROST,SIRI,SWKS,SBUX,SNPS,TMUS,TSLA,"
    "TXN,TCOM,VRSN,VRTX,WBA,WDAY,XEL,ZM"
)

USA_MID_SMALL = (
    "MSTR,GME,PLTR,COIN,HOOD,NET,RBLX,SOFI,AFRM,PATH,AMC,RIVN,LCID,DKNG,PENN,RIOT,MARA,CLSK,"
    "U,SNOW,AI,PLUG,FCEL,BLNK,NIO,XPEV,LI,BABA,PDD,JD,FUTU,LUNR,SPCE,IONQ,ASTS,GTLB,TOST"
)

FTSEMIB_FULL = (
    "A2A.MI,AMP.MI,AZM.MI,BAMI.MI,BGN.MI,BMED.MI,BMPS.MI,BPER.MI,BPSO.MI,CPR.MI,"
    "DIA.MI,ENEL.MI,ENI.MI,ERG.MI,EVO.MI,FBK.MI,G.MI,HER.MI,INW.MI,INTERPUMP.MI,"
    "ISP.MI,IVG.MI,LDO.MI,MB.MI,MONC.MI,NEXI.MI,PIRC.MI,PRY.MI,PST.MI,RACE.MI,"
    "REC.MI,SGO.MI,SRG.MI,STLAM.MI,STM.MI,TEN.MI,TIT.MI,TPRO.MI,TRN.MI,UCG.MI,UNI.MI,"
    "ANIM.MI,JUVE.MI,OVS.MI,CE.MI,BC.MI,SAB.MI,MFEA.MI,MFEB.MI,INX.MI,DTR.MI,"
    "MT.MI,LIN.MI,ELN.MI,IPH.MI,FILA.MI,GVS.MI,SFI.MI,ZV.MI,WDF.MI,ARR.MI,"
    "AGL.MI,ASCO.MI,BIF.MI,BDB.MI,ALR.MI,SO.MI,TXT.MI,BF.MI,SL.MI,"
    "Sesa.MI,TINE.MI,LUVE.MI,IF.MI,FNC.MI,RWAY.MI,GEO.MI,BCN.MI,DIS.MI,BFE.MI,"
    "SNG.MI,CSP.MI,FIE.MI,AIFI.MI,TRI.MI,EXP.MI,CIA.MI,TES.MI,CKR.MI,PRT.MI,"
    "PIN.MI,EAV.MI,EMS.MI,RET.MI,MS.MI,CLE.MI,DAN.MI,DANI.MI,CVAL.MI"
)

ETF_FULL = (
    "SPY,QQQ,IWM,EEM,VGK,GLD,SLV,XLK,XLF,XLV,XLE,XLY,XLI,XLP,XLB,XLU,XLRE,"
    "ARKK,SMH,BOTZ,TAN,QLD,TQQQ,SQQQ,SOXL,SOXS,UPRO,SPXU,UCO,SCO"
)

FUTURES_FULL = (
    "ES=F,NQ=F,RTY=F,YM=F,STXE=F,CL=F,BZ=F,NG=F,GC=F,SI=F,HG=F,ZC=F,ZS=F,"
    "KC=F,CC=F,ZN=F,ZB=F,DX=F,6E=F,6J=F"
)

TOTAL1_LEADERS = "BTC-USD,ETH-USD"
TOTAL2_MAJORS = "SOL-USD,BNB-USD,XRP-USD,ADA-USD,TRX-USD,DOT-USD,LINK-USD,AVAX-USD,TON-USD,SHIB-USD"
TOTAL3_ALTS = (
    "POL-USD,LTC-USD,UNI-USD,NEAR-USD,APT-USD,ICP-USD,STX-USD,FIL-USD,ATOM-USD,"
    "IMX-USD,RENDER-USD,GRT-USD,FTM-USD,SUI-USD,OP-USD,ARB-USD,INJ-USD,LDO-USD,"
    "TIA-USD,SEI-USD,AAVE-USD,MKR-USD,RUNE-USD,EGLD-USD,THETA-USD,ALGO-USD,XLM-USD,"
    "VET-USD,FLOW-USD,AXS-USD,SAND-USD,MANA-USD,GALA-USD,CHZ-USD,DYDX-USD,CRV-USD,"
    "ENS-USD,LRC-USD,ANKR-USD,WOO-USD,GMX-USD,JUP-USD,FET-USD,TAO-USD,PEPE-USD,WIF-USD,"
    "BONK-USD,FLOKI-USD,PENDLE-USD,ENA-USD,JTO-USD,HBAR-USD,POPCAT-USD,BRETT-USD,"
    "BOME-USD,MEW-USD,ONDO-USD,OM-USD,RAY-USD,AERO-USD,ASTR-USD"
)
CRYPTO_FULL = f"{TOTAL1_LEADERS},{TOTAL2_MAJORS},{TOTAL3_ALTS}"

def ottieni_paniere(nome_paniere):
    if nome_paniere == "S&P 500": return SP500_FULL
    elif nome_paniere == "NASDAQ 100": return NASDAQ_FULL
    elif nome_paniere == "USA Mid/Small Cap": return USA_MID_SMALL
    elif nome_paniere == "FTSE MIB (FIB)": return FTSEMIB_FULL
    elif nome_paniere == "ETF Globali": return ETF_FULL
    elif nome_paniere == "Futures di Mercato": return FUTURES_FULL
    elif nome_paniere == "Crypto": return CRYPTO_FULL
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

# --- 2. MOTORE VETTORIALE VOLUME PROFILE ---
def calc_vp(df, div=200):
    if df.empty: return None, None, None, [], []
    
    col_volume = next((c for c in df.columns if c.lower() == 'volume'), 'Volume')
    col_low = next((c for c in df.columns if c.lower() == 'low'), 'Low')
    col_high = next((c for c in df.columns if c.lower() == 'high'), 'High')
    
    p_min, p_max = float(df[col_low].min()), float(df[col_high].max())
    if p_max - p_min <= 0: return p_min, p_min, p_min, [], []
    
    bins = np.linspace(p_min, p_max, div + 1)
    vols = np.zeros(div)
    highs, lows, volumes = df[col_high].values, df[col_low].values, df[col_volume].values
    
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

# --- 3. ESECUZIONE SCANNER MULTI-ASSET ---
if __name__ == "__main__":
    print("Avvio scansione POC Estesa (Azioni USA/ITA, Crypto, ETF, Futures)...")
    invia_messaggio_telegram_sbloccato(T_ID, "🚀 <b>POC PRO Scanner:</b> Avvio ciclo globale esteso (Azioni, Crypto, ETF, Futures)...")
    
    soglia_distanza = 2.0  # Tolleranza 2%
    poc_scelti = ["Generale", "ATH", "Recente (90D)"]
    panieri_da_scansionare = ["S&P 500", "NASDAQ 100", "USA Mid/Small Cap", "FTSE MIB (FIB)", "ETF Globali", "Futures di Mercato", "Crypto"]
    segnali_trovati = 0

    for nome_paniere in panieri_da_scansionare:
        print(f"\n--- INIZIO SCANSIONE PANIERE: {nome_paniere} ---")
        lista_ticker_alert = ottieni_paniere(nome_paniere).split(",")
        totale_titoli = len(lista_ticker_alert)

        for idx, ticker in enumerate(lista_ticker_alert):
            ticker = ticker.strip()
            if not ticker: continue
        
            print(f"[{idx+1}/{totale_titoli}] Analisi quantitativa su {ticker}...")
            try:
                df_live = yf.download(tickers=ticker, period="max", interval="1d", auto_adjust=False, multi_level_index=False, progress=False, timeout=8)
                
                if df_live is not None and len(df_live) > 200:
                    df_live.columns = [str(c).strip() for c in df_live.columns]
                    
                    close_series = df_live["Close"].astype(float)
                    high_series = df_live["High"].astype(float)
                    low_series = df_live["Low"].astype(float)
                    open_series = df_live["Open"].astype(float)
                    volume_series = df_live["Volume"].astype(float)
                    
                    p_attuale = float(close_series.iloc[-1])
                    d_ath = high_series.idxmax()
                    
                    # Indicatori tecnici basilari
                    ema200 = close_series.ewm(span=200, adjust=False).mean().iloc[-1]
                    
                    delta = close_series.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rsi_series = 100 - (100 / (1 + (gain / np.where(loss == 0, 0.00001, loss))))
                    rsi_attuale = rsi_series.iloc[-1]
                    
                    tr = pd.concat([high_series - low_series, 
                                    (high_series - close_series.shift(1)).abs(), 
                                    (low_series - close_series.shift(1)).abs()], axis=1).max(axis=1)
                    atr_attuale = tr.rolling(window=14).mean().iloc[-1]
                    
                    df_generale = pd.DataFrame({"Open": open_series, "High": high_series, "Low": low_series, "Close": close_series, "Volume": volume_series}, index=df_live.index)
                    df_ath_data = df_generale.loc[d_ath:].copy()
                    df_recente = df_generale.tail(90).copy()
                    
                    controlli_da_effettuare = []
                    if "Generale" in poc_scelti: controlli_da_effettuare.append(("GENERALE", df_generale))
                    if "ATH" in poc_scelti: controlli_da_effettuare.append(("DALL'ATH", df_ath_data))
                    if "Recente (90D)" in poc_scelti: controlli_da_effettuare.append(("RECENTE (90D)", df_recente))
                    
                    for nome_profilo, df_singolo_profilo in controlli_da_effettuare:
                        if df_singolo_profilo.empty: continue
                        
                        p_poc, p_vh, p_vl, prz_v, vl_v = calc_vp(df_singolo_profilo)
                        if p_poc is None or atr_attuale is None or np.isnan(atr_attuale): continue
                        
                        distanza_percentuale = ((p_attuale - p_poc) / p_poc) * 100
                        
                        if abs(distanza_percentuale) <= soglia_distanza:
                            is_rsi_ok_long = rsi_attuale < 75
                            is_rsi_ok_short = rsi_attuale > 25
                            
                            if nome_profilo == "RECENTE (90D)":
                                passa_filtro_trend_long = p_attuale > ema200
                                passa_filtro_trend_short = p_attuale < ema200
                            else:
                                passa_filtro_trend_long, passa_trend_short = True, True
                            
                            setup_valido = False
                            
                            if p_attuale >= p_poc and passa_filtro_trend_long and is_rsi_ok_long:
                                direzione = "LONG 🟢"
                                stop_1 = p_attuale - (1.5 * atr_attuale)
                                take_p = p_attuale + (3.0 * atr_attuale)
                                setup_valido = True
                                
                            elif p_attuale < p_poc and passa_filtro_trend_short and is_rsi_ok_short:
                                direzione = "SHORT 🔴"
                                stop_1 = p_attuale + (1.5 * atr_attuale)
                                take_p = p_attuale - (3.0 * atr_attuale)
                                setup_valido = True
                            
                            if setup_valido:
                                segnali_trovati += 1
                                # Formattazione pulita per i ticker del report e di TradingView
                                ticker_pulito = str(ticker).replace(".MI", "").replace("-USD", "").replace("=F", "")
                                
                                if ".MI" in str(ticker): 
                                    borsa_code = "MILAN"
                                elif "-USD" in str(ticker) or nome_paniere == "Crypto": 
                                    borsa_code = "BINANCE"
                                elif str(ticker).endswith("=F") or nome_paniere == "Futures di Mercato":
                                    borsa_code = "CME"
                                else: 
                                    borsa_code = "NASDAQ" if nome_paniere == "NASDAQ 100" else "NYSE"
                                
                                url_stringa_pura = f"https://it.tradingview.com/symbols/{borsa_code}-{ticker_pulito}/"
                                dec = 4 if nome_paniere == "Crypto" else (4 if str(ticker).endswith("=F") else 2)
                                
                                messaggio_alert = (
                                    f"🚨 <b>STRATEGIA QUANT BILANCIATA</b>\n\n"
                                    f"📈 <b>Ticker:</b> #{ticker_pulito} ({nome_paniere})\n"
                                    f"📊 <b>Profilo Volume:</b> {nome_profilo}\n"
                                    f"⚡ <b>Setup Operativo:</b> {direzione}\n\n"
                                    f"💵 <b>Prezzo Attuale:</b> {round(p_attuale, dec)}\n"
                                    f"🎯 <b>Entry (Prezzo):</b> {round(p_attuale, dec)}\n"
                                    f"🔴 <b>Stop Loss (1.5 ATR):</b> {round(stop_1, dec)}\n"
                                    f"💰 <b>Take Profit (3.0 ATR):</b> {round(take_p, dec)}\n"
                                    f"🔍 <b>Metriche di Controllo:</b>\n"
                                    f"|— <i>Rapporto R/R:</i> 1:2.0 (Fisso)\n"
                                    f"|— <i>RSI (14):</i> {round(rsi_attuale, 1)}\n"
                                    f"|— <i>Filtro EMA200:</i> {'SOPRA' if p_attuale > ema200 else 'SOTTO'}\n"
                                    f"|— <i>ATR Volatilità:</i> {round(atr_attuale, dec)}\n\n"
                                    f"🔗 <a href='{url_stringa_pura}'>APRI GRAFICO SU TRADINGVIEW</a>"
                                )
                                invia_messaggio_telegram_sbloccato(T_ID, messaggio_alert)
                                print(f"--> [SEGNALE INVIATO] {ticker} ({nome_profilo})")
                                
            except Exception as single_err:
                print(f"Errore nell'analisi di {ticker}: {single_err}")
                        
    print(f"\nScansione completata. Trovati {segnali_trovati} segnali totali.")
    messaggio_fine = f"🏁 <b>POC PRO Scanner:</b> Ciclo terminato.\n📊 Inviati <b>{segnali_trovati}</b> segnali bilanciati."
    invia_messaggio_telegram_sbloccato(T_ID, messaggio_fine)
