import streamlit as st
import plotly.express as px
import pandas as pd

# --- 1. CONFIGURAZIONE & STILE ---
st.set_page_config(page_title="Asset Advisor Pro | Beta 0.1.3", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 2px; height: 3em; background-color: #1A3A5F; color: white; font-weight: bold; border: none;}
    
    /* Box Navy - Testo Bianco sempre leggibile */
    .navy-card {background-color: #1A3A5F; color: white !important; padding: 30px; border-radius: 5px; text-align: center;}
    .navy-card h1, .navy-card h2, .navy-card h3, .navy-card p {color: white !important;}

    /* Box Delibera Banca - Grigio Professionale */
    .bank-box {background-color: #f1f3f5; border: 2px solid #1A3A5F; padding: 20px; border-radius: 5px; color: #1A3A5F !important;}
    
    /* Box Advisor - Risolto contrasto */
    .advice-box {
        padding: 25px; 
        border-left: 8px solid #1A3A5F !important; 
        background-color: #f8f9fa !important; 
        color: #1A3A5F !important; 
        font-weight: 500; 
        margin: 20px 0px; 
        border-radius: 4px;
    }
    .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f3f5; color: #666; text-align: center; padding: 10px; font-size: 0.8em; border-top: 1px solid #ddd; z-index: 100;}
    </style>
    """, unsafe_allow_html=True)

def fmt(valore):
    return f"€ {int(round(valore, 0)):,}".replace(",", ".")

def parse_it_perc(label, default="3,5"):
    val = st.text_input(label, value=default)
    if "." in val:
        st.error("⚠️ Usa la virgola (,) non il punto (.)")
        return 0.0
    try: return float(val.replace(",", "."))
    except: return 0.0

# --- 2. HEADER ---
st.title("🏛️ Asset Advisor Pro")
st.markdown("<p style='color:#666;'>Analisi strategica patrimoniale e simulazione di delibera bancaria.</p>", unsafe_allow_html=True)

st.divider()

# --- 3. INPUT DATI (FASE 1) ---
st.subheader("📍 1. Asset e Capitale Proprio")
c1, c2, c3 = st.columns(3)
with c1:
    prezzo_casa = st.number_input("Prezzo acquisto immobile (€)", min_value=0, value=250000, step=5000)
    anticipo = st.number_input("Capitale Proprio (Anticipo) (€)", min_value=0, value=50000, step=5000)
with c2:
    tipo_venditore = st.selectbox("Soggetto Venditore:", ["Privato (Imposta Registro)", "Costruttore (Soggetto a IVA)"])
    valore_catastale = st.number_input("Valore catastale (€)", min_value=0, value=1000)
with c3:
    tipo_casa = st.selectbox("Tipologia Immobile", ["Prima Casa", "Seconda Casa", "Immobile di Lusso"])
    durata_anni = st.select_slider("Orizzonte Temporale (Anni)", options=list(range(5, 41)), value=30)

# --- 4. ONERI E FINANZIAMENTO ---
st.divider()
st.subheader("🛠️ 2. Oneri, Lavori e Tassi")
c4, c5, c6 = st.columns(3)
with c4:
    sp_ristr = st.number_input("Budget Ristrutturazione (€)", value=0, step=5000)
    sp_arredi = st.number_input("Budget Arredamento (€)", value=0, step=2000)
with c5:
    sp_age = st.number_input("Commissione Mediazione (€)", value=7500)
    not_tot = st.number_input("Spesa Notaio Unica (€)", value=3000)
with c6:
    sp_perizia = st.number_input("Spese Istruttoria/Perizia/Assicurative (€)", value=1500)
    tasso_annuo = parse_it_perc("Tasso Annuo Nominale (TAN) %", "3,5")

# --- CALCOLI FISCALI & MUTUO ---
if tipo_venditore == "Privato (Imposta Registro)":
    tasse_acq = ((valore_catastale * 110) * 0.02 + 100) if "Prima Casa" in tipo_casa else ((valore_catastale * 120) * 0.09 + 100)
else:
    aliquota = 0.04 if "Prima Casa" in tipo_casa else (0.22 if "Lusso" in tipo_casa else 0.10)
    tasse_acq = (prezzo_casa * aliquota) + 600

fabbisogno_nudo = (prezzo_casa + tasse_acq + sp_age + not_tot + sp_perizia + sp_ristr + sp_arredi) - anticipo
imp_sost = fabbisogno_nudo * (0.0025 if "Prima Casa" in tipo_casa else 0.02)
mutuo_totale = fabbisogno_nudo + imp_sost

i_m = (tasso_annuo / 100) / 12
n_m = durata_anni * 12
rata = mutuo_totale * (i_m * (1 + i_m)**n_m) / ((1 + i_m)**n_m - 1) if i_m > 0 else mutuo_totale / n_m
interessi_t = (rata * n_m) - mutuo_totale

# --- 5. QUADRO FINANZIARIO E RATA (SISTEMATO) ---
st.divider()
st.subheader("🏦 3. Quadro Finanziario e Delibera")
col_rata, col_mutuo, col_delibera = st.columns([1, 1, 1.5])

with col_rata:
    st.markdown(f"""
        <div class="navy-card">
            <p style='margin:0; font-size:1em; opacity:0.8;'>RATA MENSILE</p>
            <h1 style='margin:0;'>{fmt(rata)}</h1>
        </div>
        """, unsafe_allow_html=True)

with col_mutuo:
    st.markdown(f"""
        <div class="navy-card" style="background-color: #4A4A4A;">
            <p style='margin:0; font-size:1em; opacity:0.8;'>MUTUO LORDO</p>
            <h1 style='margin:0;'>{fmt(mutuo_totale)}</h1>
        </div>
        """, unsafe_allow_html=True)

with col_delibera:
    reddito_f = st.number_input("Reddito Mensile Netto Famiglia (€)", min_value=1, value=3500)
    dti = (rata / reddito_f) * 100
    status = "COMPATIBILE ✅" if dti <= 33 else "CRITICO ⚠️"
    color_status = "green" if dti <= 33 else "red"
    
    st.markdown(f"""
    <div class="bank-box">
        <b>Esito Simulazione Delibera:</b> <span style="color:{color_status}; font-weight:bold;">{status}</span><br>
        Rapporto Rata/Reddito: <b>{dti:.1f}%</b><br>
        <small>L'istituto di credito richiede solitamente un rapporto non superiore al 33%. Verificare con la propria banca.</small>
    </div>
    """, unsafe_allow_html=True)

# --- 6. COSTI GESTIONE ---
st.write("")
st.subheader("🔧 4. Gestione Immobile")
cg1, cg2 = st.columns(2)
with cg1:
    sp_casa_ord = st.number_input("Spese Ordinarie (€/mese) - Bollette/Condominio", value=250)
    st.caption("Costi vivi di utilizzo. Non influenzano il patrimonio finale.")
with cg2:
    sp_casa_str = st.number_input("Manutenzione Straordinaria Media (€/anno)", value=1000)
    st.caption("Costi di conservazione asset. Erodono il patrimonio netto futuro.")

# --- 7. ADVISOR PATRIMONIALE ---
st.divider()
st.subheader("📈 5. Asset Advisor: Strategia a Confronto")

rival_imm = parse_it_perc("% Rivalutazione stimata asset", "1,5") / 100
val_imm_f = prezzo_casa * (1 + rival_imm)**durata_anni
# Patrimonio netto: Valore casa - (Interessi + Oneri Iniziali + Ristrutturazione + Manutenzione Straordinaria)
costi_tot_acq = interessi_t + (tasse_acq + sp_age + not_tot + sp_perizia) + sp_ristr + (sp_casa_str * durata_anni)
patr_netto_acq = val_imm_f - costi_tot_acq

with st.expander("Configura Investimento Mobiliare Alternativo (Affitto + Titoli)"):
    canone_affitto = st.number_input("Canone mensile affitto (€)", value=0)
    resa_inv = st.slider("Rendimento annuo portafoglio (%)", 1, 9, 4)
    costo_aff_tot = 0; curr_can = canone_affitto
    for a in range(durata_anni): costo_aff_tot += (curr_can * 12); curr_can *= 1.02 # ISTAT 2%
    mont_n = (anticipo * (1 + (resa_inv/100))**durata_anni)
    mont_n -= (mont_n - anticipo) * 0.20 # Tassa 20% su plusvalenza
    patr_netto_inv = mont_n - costo_aff_tot

ca1, ca2 = st.columns(2)
with ca1: st.markdown(f"<div class='navy-card'><h3>PATRIMONIO NETTO (ACQUISTO)</h3><h2>{fmt(patr_netto_acq)}</h2></div>", unsafe_allow_html=True)
with ca2: st.markdown(f"<div class='navy-card' style='background-color:#4A4A4A'><h3>PATRIMONIO NETTO (CASH)</h3><h2>{fmt(patr_netto_inv)}</h2></div>", unsafe_allow_html=True)

if patr_netto_acq > patr_netto_inv:
    st.markdown(f"<div class='advice-box'>💡 <b>ADVISOR:</b> L'acquisto risulta vincente. Vantaggio patrimoniale: <b>{fmt(patr_netto_acq - patr_netto_inv)}</b>.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='advice-box'>💡 <b>ADVISOR:</b> L'investimento mobiliare risulta superiore per <b>{fmt(patr_netto_inv - patr_netto_acq)}</b>.</div>", unsafe_allow_html=True)

# --- 8. GRAFICO & DETTAGLIO ---
g1, g2 = st.columns([1.3, 1])
with g1:
    voci_raz = {"Mutuo": mutuo_totale, "Oneri & Tasse": tasse_acq + imp_sost + sp_age + not_tot + sp_perizia, "Lavori": sp_ristr + sp_arredi}
    fig = px.pie(names=list(voci_raz.keys()), values=list(voci_raz.values()), hole=0.6, color_discrete_sequence=["#1A3A5F", "#4A4A4A", "#708090"])
    fig.update_traces(textinfo='label+percent', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
with g2:
    st.write("**Riepilogo Costi Operazione**")
    st.table(pd.DataFrame({
        " ": ["🏠", "⚖️", "🤝", "🖊️", "🏗️", "🏦"],
        "Voce": ["Prezzo Asset", "Imposte", "Agenzia", "Notaio", "Ristrutturazione", "Mutuo Lordo"],
        "Valore": [fmt(prezzo_casa), fmt(tasse_acq), fmt(sp_age), fmt(not_tot), fmt(sp_ristr), fmt(mutuo_totale)]
    }))

# --- 9. PREVIDENZA E AMMORTAMENTO (DISTINTI) ---
st.divider()
st.subheader("📈 6. Analisi Previdenziale")
with st.expander("Calcolo Riscatto Fondo Pensione"):
    fa1, fa2, fa3 = st.columns(3)
    anz_f = fa1.number_input("Anzianità Fondo (Anni)", value=8)
    m_v = fa2.number_input("Quota Versata (€)", value=0)
    m_g = fa3.number_input("Quota Gestione (€)", value=0)
    if anz_f >= 8:
        tot_f = m_v + m_g
        st.info(f"Anticipo massimo (75%): {fmt(tot_f*0.75)}")
        perc_r = st.slider("% Riscatto", 0, 75, 75)
        if tot_f > 0:
            lrd = tot_f * (perc_r/100); qv = lrd * (m_v/tot_f); qg = lrd * (m_g/tot_f)
            st.success(f"Liquidità Netta: {fmt((qv * 0.77) + qg)}")

st.subheader("📅 7. Piano di Ammortamento")
with st.expander("Visualizza dettaglio quote capitali e interessi"):
    piano = []; res_p = mutuo_totale
    for anno in range(1, durata_anni + 1):
        i_a = 0; c_a = 0
        for m in range(12):
            im = res_p * i_m; cm = rata - im
            i_a += im; c_a += cm; res_p -= cm
        piano.append([anno, fmt(c_a), fmt(i_a), fmt(max(0, res_p))])
    st.dataframe(pd.DataFrame(piano, columns=["Anno", "Capitale", "Interessi", "Residuo"]), use_container_width=True, hide_index=True)

# --- 10. FOOTER ---
st.divider()
if st.button("🖨️ Stampa Report"):
    st.markdown('<img src="x" onerror="window.print()">', unsafe_allow_html=True)

st.markdown("""<div class="footer">Asset Advisor Pro | <b>Beta Test 0.1.3</b> | Strategic Financial Engine</div>""", unsafe_allow_html=True)