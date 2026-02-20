import streamlit as st
import plotly.express as px
import pandas as pd

# --- 1. CONFIGURAZIONE & STILE ---
st.set_page_config(page_title="Professional Asset Advisor", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 2px; height: 3em; background-color: #1A3A5F; color: white; font-weight: bold; border: none;}
    .navy-card {background-color: #1A3A5F; color: white; padding: 30px; border-radius: 5px; text-align: center;}
    .grey-card {background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 5px;}
    
    /* FIX CSS ADVISOR BOX (Per renderlo leggibile) */
    .advice-box {
        padding: 25px; 
        border-left: 8px solid #1A3A5F !important; 
        background-color: #f1f3f5 !important; /* Grigio chiaro */
        color: #1A3A5F !important; /* Testo Navy scuro */
        font-weight: 500;
        margin: 20px 0px;
        border-radius: 4px;
    }
    .advice-box b { color: #1A3A5F !important; }
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

# --- 2. INPUT DATI ---
st.title("🏛️ Professional Asset & Mortgage Advisor")

with st.container():
    st.subheader("📍 Configurazione Immobile")
    c1, c2, c3 = st.columns(3)
    with c1:
        prezzo_casa = st.number_input("Prezzo acquisto (€)", min_value=0, value=250000, step=5000)
        tipo_venditore = st.selectbox("Acquisto da:", ["Privato (Registro)", "Costruttore (IVA)"])
    with c2:
        valore_catastale = st.number_input("Valore catastale (€)", min_value=0, value=1000)
        tipo_casa = st.selectbox("Destinazione", ["Prima Casa", "Seconda Casa", "Immobile di Lusso"])
    with c3:
        mq = st.number_input("Superficie (mq)", min_value=1, value=100)
        anticipo = st.number_input("Anticipo contante (€)", min_value=0, value=50000, step=5000)

st.divider()
st.subheader("🛠️ Spese Accessorie e Lavori")
c4, c5, c6 = st.columns(3)
with c4:
    sp_ristr = st.number_input("Ristrutturazione (€)", value=0, step=5000)
    sp_arredi = st.number_input("Arredamento (€)", value=0, step=2000)
with c5:
    sp_age = st.number_input("Agenzia Immobiliare (€)", value=7500)
    not_tot = st.number_input("Spesa Notaio Totale (€)", value=3000)
with c6:
    sp_perizia = st.number_input("Istruttoria/Perizia Banca (€)", value=800)
    tasso_annuo = parse_it_perc("Tasso annuo mutuo %", "3,5")
    durata_anni = st.slider("Durata Mutuo (Anni)", 5, 40, 25)

# --- LOGICA CALCOLI ---
if tipo_venditore == "Privato (Registro)":
    tasse_acq = ((valore_catastale * 110) * 0.02 + 100) if "Prima Casa" in tipo_casa else ((valore_catastale * 120) * 0.09 + 100)
else:
    aliquota = 0.04 if "Prima Casa" in tipo_casa else (0.22 if "Lusso" in tipo_casa else 0.10)
    tasse_acq = (prezzo_casa * aliquota) + 600

# Fabbisogno per calcolo mutuo (Tutto - Anticipo)
fabbisogno_nudo = (prezzo_casa + tasse_acq + sp_age + not_tot + sp_perizia + sp_ristr + sp_arredi) - anticipo
imp_sost = fabbisogno_nudo * (0.0025 if "Prima Casa" in tipo_casa else 0.02)
mutuo_totale = fabbisogno_nudo + imp_sost

i_m = (tasso_annuo / 100) / 12
n_m = durata_anni * 12
rata = mutuo_totale * (i_m * (1 + i_m)**n_m) / ((1 + i_m)**n_m - 1) if i_m > 0 else mutuo_totale / n_m
interessi_t = (rata * n_m) - mutuo_totale

# --- SEZIONE FABBISOGNO ---
st.divider()
st.subheader("💳 Analisi del Credito e Sostenibilità")
col_fin_left, col_fin_right = st.columns([1.2, 2])

with col_fin_left:
    st.markdown(f"""
        <div class="navy-card">
            <p style='margin:0; font-size:1em; opacity:0.8;'>MUTUO DA RICHIEDERE</p>
            <h1 style='margin:0; color:white; font-size:3em;'>{fmt(mutuo_totale)}</h1>
            <p style='margin-top:10px; font-size:0.8em;'>Copertura su valore immobile: {(mutuo_totale/prezzo_casa)*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

with col_fin_right:
    st.write("**Verifica Reddituale e Gestione**")
    r1, r2, r3 = st.columns(3)
    with r1:
        reddito_f = st.number_input("Reddito mensile netto (€)", min_value=0, value=3500)
        inc_banca = (rata / reddito_f * 100) if reddito_f > 0 else 0
        st.metric("Rapporto Rata/Reddito", f"{inc_banca:.1f}%")
    with r2:
        altri_debiti = st.number_input("Altri impegni (€/mese)", value=0)
        inc_reale = ((rata + altri_debiti) / reddito_f * 100) if reddito_f > 0 else 0
        st.write(f"Soglia Banca Totale: **{inc_reale:.1f}%**")
    with r3:
        sp_casa = st.number_input("Spese Casa (€/mese)", value=250)
        esborso_famiglia = rata + altri_debiti + sp_casa
        st.metric("Uscita Mensile Totale", fmt(esborso_famiglia))
    
    if inc_reale > 35: st.error("⚠️ ALERT: Sostenibilità bancaria compromessa (>35%)")
    else: st.success("✅ Parametri di sostenibilità approvati")

# --- SEZIONE ADVISOR ---
st.divider()
st.subheader("📈 Asset Advisor: Confronto Strategico")

rival_imm = parse_it_perc("% Rivalutazione annua casa", "1,5") / 100
val_imm_f = prezzo_casa * (1 + rival_imm)**durata_anni
# Netto Acquisto: Valore - (Interessi + Tasse/Agenzia/Notaio + Ristrutturazione + Manutenzione)
patr_netto_acq = val_imm_f - (interessi_t + (tasse_acq + sp_age + not_tot + sp_perizia) + sp_ristr + (1000 * durata_anni))

with st.expander("Configura Scenario Alternativo (Affitto + Investimento)"):
    canone_affitto = st.number_input("Canone mensile (€)", value=850)
    resa_inv = st.slider("Rendimento annuo portafoglio (%)", 1, 9, 4)
    costo_aff_tot = 0; curr_can = canone_affitto
    for a in range(durata_anni): costo_aff_tot += (curr_can * 12); curr_can *= 1.02 # ISTAT 2%
    mont_n = (anticipo * (1 + (resa_inv/100))**durata_anni)
    mont_n -= (mont_n - anticipo) * 0.20 # Tassa plusvalenza media
    patr_netto_inv = mont_n - costo_aff_tot

ca1, ca2 = st.columns(2)
with ca1:
    st.markdown(f"<div class='navy-card'><h3>PATRIMONIO NETTO ACQUISTO</h3><h2>{fmt(patr_netto_acq)}</h2></div>", unsafe_allow_html=True)
with ca2:
    st.markdown(f"<div class='navy-card' style='background-color:#4A4A4A'><h3>PATRIMONIO NETTO INVESTIMENTO</h3><h2>{fmt(patr_netto_inv)}</h2></div>", unsafe_allow_html=True)

# --- BOX ADVISOR CON FIX CSS ---
if patr_netto_acq > patr_netto_inv:
    st.markdown(f"<div class='advice-box'>💡 <b>ADVISOR:</b> L'acquisto risulta vincente. Il patrimonio finale è superiore di <b>{fmt(patr_netto_acq - patr_netto_inv)}</b> rispetto allo scenario alternativo.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='advice-box'>💡 <b>ADVISOR:</b> L'investimento finanziario (+ affitto) genera un valore superiore di <b>{fmt(patr_netto_inv - patr_netto_acq)}</b>.</div>", unsafe_allow_html=True)

# --- SEZIONE GRAFICO (TORTA PROFESSIONALE) & TABELLA ---
st.divider()
g1, g2 = st.columns([1.3, 1])

with g1:
    st.subheader("Ripartizione dei Costi")
    # 1. Razionalizzazione delle voci per evitare fettine illeggibili
    voci_razionalizzate = {
        "Immobile Netto": max(0, prezzo_casa - anticipo),
        "Tasse & Imposte": tasse_acq + imp_sost,
        "Professionisti (Agenzia/Notaio/Banca)": sp_age + not_tot + sp_perizia,
        "Lavori & Arredi": sp_ristr + sp_arredi
    }
    
    # 2. Creazione della torta professionale
    # Colori: Navy principale, poi scala di grigi distinti
    colors_pro = ["#1A3A5F", "#4A4A4A", "#6c757d", "#adb5bd"]
    fig = px.pie(
        names=list(voci_razionalizzate.keys()), 
        values=list(voci_razionalizzate.values()), 
        hole=0.6, # Donut chart
        color_discrete_sequence=colors_pro
    )
    
    # 3. Configurazione etichette esterne (fondamentale per la leggibilità)
    fig.update_traces(
        textposition='outside', 
        textinfo='label+percent',
        pull=[0.05, 0, 0, 0], # Estrae leggermente la fetta principale
        marker=dict(line=dict(color='#FFFFFF', width=2)) # Bordi bianchi puliti
    )
    
    # 4. Layout pulito senza legenda
    fig.update_layout(
        showlegend=False,
        margin=dict(t=30, b=30, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with g2:
    st.subheader("Dettaglio Analitico")
    st.table(pd.DataFrame({
        " ": ["🏠", "⚖️", "🤝", "🖊️", "🏗️", "🛋️", "🏦"],
        "Voce": ["Prezzo Immobile", "Imposte Totali", "Provvigione Agenzia", "Notaio Totale", "Ristrutturazione", "Arredamento", "Mutuo Erogato"],
        "Importo": [fmt(prezzo_casa), fmt(tasse_acq), fmt(sp_age), fmt(not_tot), fmt(sp_ristr), fmt(sp_arredi), fmt(mutuo_totale)]
    }))

# --- APPENDICI (FONDO PENSIONE & AMMORTAMENTO) ---
st.divider()
t1, t2 = st.tabs(["📊 Calcolo Fondo Pensione", "📅 Piano Ammortamento"])

with t1:
    st.subheader("Modulo Riscatto Fondo Pensione")
    fa1, fa2, fa3 = st.columns(3)
    anz_f = fa1.number_input("Anni iscrizione", value=8, key="anz")
    m_vers = fa2.number_input("Montante Versato (€)", value=0, key="vers")
    m_gest = fa3.number_input("Montante Gestione (€)", value=0, key="gest")
    
    if anz_f >= 8:
        tot_f = m_vers + m_gest
        max_ant = tot_f * 0.75
        st.markdown(f"<div style='background-color:#e9ecef;border-left:5px solid #1A3A5F;padding:15px;color:#1A3A5F;'>💡 L'anticipo massimo (75%) è di <b>{fmt(max_ant)}</b>.</div>", unsafe_allow_html=True)
        perc_r = st.slider("% Riscatto Proporzionale", 0, 75, 75)
        if tot_f > 0:
            lordo = tot_f * (perc_r/100)
            q_v = lordo * (m_vers/tot_f); q_g = lordo * (m_gest/tot_f)
            st.success(f"Liquidità Netta: **{fmt((q_v * 0.77) + q_g)}** (Tassazione 23% solo su quota versata)")

with t2:
    piano = []
    res_p = mutuo_totale
    for anno in range(1, durata_anni + 1):
        i_a = 0; c_a = 0
        for m in range(12):
            im = res_p * i_m; cm = rata - im
            i_a += im; c_a += cm; res_p -= cm
        piano.append([anno, fmt(c_a), fmt(i_a), fmt(max(0, res_p))])
    st.dataframe(pd.DataFrame(piano, columns=["Anno", "Capitale", "Interessi", "Residuo"]), use_container_width=True, hide_index=True)

# --- CONTATTI & STAMPA ---
st.divider()
c_f1, c_f2 = st.columns(2)
with c_f1:
     st.subheader("📩 Richiedi Consulenza")
     with st.form("contact"):
        st.text_input("Email")
        st.text_area("Messaggio")
        st.form_submit_button("Invia")
with c_f2:
    st.write("") # Spacer
    st.write("")
    if st.button("🖨️ Stampa Report"): st.markdown("<script>window.print();</script>", unsafe_allow_html=True)