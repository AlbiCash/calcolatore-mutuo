import streamlit as st
import plotly.express as px
import pandas as pd

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Analisi Patrimoniale Real Estate", layout="wide")

# CSS per colori e stile professionale
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #1A3A5F; color: white;}
    /* Alert personalizzati */
    .bank-alert {padding: 15px; border-radius: 10px; border-left: 5px solid #800020; background-color: #f9f9f9;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONI DI UTILITÀ ---
def fmt(valore):
    """Formatta in Euro: 100.000 €"""
    return f"€ {int(round(valore, 0)):,}".replace(",", ".")

def parse_it_perc(label, default="3,5"):
    """Gestisce l'input con virgola obbligatoria"""
    val = st.text_input(label, value=default)
    if "." in val:
        st.error("Usa la virgola (,) come separatore per le percentuali.")
        return 0.0
    try:
        return float(val.replace(",", "."))
    except:
        return 0.0

# --- 3. INPUT DATI ---
st.title("🏦 Analisi Finanziaria Immobiliare")

col_a, col_b, col_c = st.columns(3)
with col_a:
    prezzo_casa = st.number_input("Prezzo acquisto immobile (€)", min_value=0, value=250000, step=1000)
    anticipo = st.number_input("Anticipo contante (€)", min_value=0, max_value=prezzo_casa, value=50000, step=1000)
with col_b:
    valore_catastale = st.number_input("Valore catastale (€)", min_value=0, value=1000, step=100)
    mq = st.number_input("Superficie immobile (mq)", min_value=1, value=100)
with col_c:
    tipo_casa = st.selectbox("Destinazione immobile", ["Prima Casa", "Seconda Casa"])
    tasso_annuo = parse_it_perc("Tasso annuo mutuo %", "3,5")

# --- 4. SPESE D'ACQUISTO ---
st.subheader("📝 Spese d'Acquisto e Oneri Professionisti")
with st.expander("Modifica Notaio e Agenzia", expanded=True):
    c_acq1, c_acq2 = st.columns(2)
    with c_acq1:
        sp_age = st.number_input("Agenzia Immobiliare (Totale IVA inclusa) (€)", value=7500)
        not_rogito = st.number_input("Onorario Notaio per Rogito d'acquisto (€)", value=1800)
    with c_acq2:
        not_mutuo = st.number_input("Onorario Notaio per Atto di Mutuo (€)", value=1200)
        sp_perizia = st.number_input("Perizia e Istruttoria fisse (€)", value=800)

# --- 5. LOGICA FISCALE E LAVORI ---
tasse_reg = ((valore_catastale * 110) * 0.02 + 100) if tipo_casa == "Prima Casa" else ((valore_catastale * 120) * 0.09 + 100)
t_mutuo_p = 0.0025 if tipo_casa == "Prima Casa" else 0.02

st.subheader("🛠️ Allestimento e Lavori")
cl1, cl2 = st.columns(2)
with cl1:
    spesa_r = st.number_input("Totale preventivo ristrutturazione (€)", value=0)
with cl2:
    spesa_m = st.number_input("Totale preventivo arredi (€)", value=0)

# Calcoli Mutuo
cap_netto_casa = max(0, prezzo_casa - anticipo)
spese_accessorie_tot = tasse_reg + spesa_r + spesa_m + sp_age + not_rogito + not_mutuo + sp_perizia
imp_sost = (cap_netto_casa + spese_accessorie_tot) * t_mutuo_p
cap_finanziato = cap_netto_casa + spese_accessorie_tot + imp_sost

durata_anni = st.slider("Durata Mutuo (Anni)", 5, 40, 25, step=1)
i_m = (tasso_annuo / 100) / 12
n_m = durata_anni * 12
rata = cap_finanziato * (i_m * (1 + i_m)**n_m) / ((1 + i_m)**n_m - 1) if i_m > 0 else cap_finanziato / n_m

# --- 6. SOSTENIBILITÀ BANCARIA E FAMILIARE ---
st.divider()
st.subheader("📊 Analisi della Sostenibilità")
col_sos1, col_sos2 = st.columns(2)

with col_sos1:
    st.markdown("**🏦 Parametri per la Banca**")
    reddito_famiglia = st.number_input("Reddito mensile netto (totale famiglia) (€)", min_value=0, value=3000)
    altri_impegni = st.number_input("Altri impegni mensili (€)", value=0)
    
    if reddito_famiglia > 0:
        incidenza_banca = ((rata + altri_impegni) / reddito_famiglia) * 100
        st.metric("Rapporto Rata/Reddito", f"{incidenza_banca:.1f}%")
        
        # ALERT SOSTENIBILITÀ BANCARIA
        if incidenza_banca > 35:
            st.error("⚠️ ALERT: L'incidenza supera la soglia del 35%. Possibili difficoltà nel rilascio del mutuo.")
        else:
            st.success("✅ Parametri di sostenibilità bancaria rispettati.")

with col_sos2:
    st.markdown("**🏠 Sostenibilità Reale Famiglia**")
    spese_g = st.number_input("Condominio + Bollette (€/mese)", value=250)
    spese_s = st.number_input("Accantonamento Straordinario (€/anno)", value=600)
    tot_reale = rata + spese_g + (spese_s/12)
    st.metric("Esborso Mensile Reale", fmt(tot_reale))

# --- 7. INVESTIMENTO VS ACQUISTO ---
st.divider()
st.subheader("📈 Scenario Alternativo: Affitto + Investimento")
with st.expander("Confronto Patrimoniale dopo " + str(durata_anni) + " anni", expanded=True):
    i_inv1, i_inv2 = st.columns(2)
    with i_inv1:
        st.write("**Dati Affitto**")
        canone_i = st.number_input("Canone mensile affitto (€)", value=800)
        rival_istat = parse_it_perc("% Rivalutazione annua ISTAT", "2,0") / 100
        
        costo_affitto_tot = 0
        curr_can = canone_i
        for a in range(durata_anni):
            costo_affitto_tot += (curr_can * 12)
            curr_can *= (1 + rival_istat)
        st.write(f"Costo totale affitto pagato nel periodo: **{fmt(costo_affitto_tot)}**")

    with i_inv2:
        st.write("**Dati Investimento**")
        perc_inv = st.slider("Resa annua investimento (%)", 1, 9, 4, step=1)
        rend = perc_inv / 100
        # Capitale iniziale = Solo anticipo contante
        capitale_inv = anticipo
        montante_lordo = capitale_inv * (1 + rend)**durata_anni
        plusvalenza = montante_lordo - capitale_inv
        montante_netto = montante_lordo - (plusvalenza * 0.20) # Tassazione 20%
        
        # Patrimonio netto dell'investitore sottraendo l'affitto
        patr_residuo = montante_netto - costo_affitto_tot
        st.write(f"Capitale iniziale investito: **{fmt(capitale_inv)}**")
        st.write(f"Valore netto titoli a scadenza: **{fmt(montante_netto)}**")

# --- 8. VERDETTO PATRIMONIALE ---
st.divider()
rival_imm = parse_it_perc("% Rivalutazione annua immobile", "1,5") / 100
val_imm_futuro = prezzo_casa * (1 + rival_imm)**durata_anni

cv1, cv2 = st.columns(2)
with cv1:
    st.markdown(f"""
    <div style="background-color:#1A3A5F; padding:25px; border-radius:12px; color:white; border-left: 8px solid #4A4A4A;">
    <h3 style="color:white; margin-top:0;">SCENARIO ACQUISTO</h3>
    <p>Valore di vendita dell'immobile tra {durata_anni} anni:</p>
    <h2 style="color:white">{fmt(val_imm_futuro)}</h2>
    <p style="font-size:0.9em; opacity:0.8;">Il mutuo è estinto. Patrimonio immobiliare netto.</p>
    </div>
    """, unsafe_allow_html=True)

with cv2:
    p_visual = max(0, patr_residuo)
    st.markdown(f"""
    <div style="background-color:#800020; padding:25px; border-radius:12px; color:white; border-left: 8px solid #D3D3D3;">
    <h3 style="color:white; margin-top:0;">SCENARIO INVESTIMENTO</h3>
    <p>Liquidità residua dopo {durata_anni} anni di affitto:</p>
    <h2 style="color:white">{fmt(p_visual)}</h2>
    <p style="font-size:0.9em; opacity:0.8;">Somma derivante dal fondo titoli meno i canoni pagati.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
delta = val_imm_futuro - p_visual
if delta > 0:
    st.success(f"L'acquisto della casa genera un patrimonio superiore di **{fmt(delta)}** rispetto all'affitto.")
else:
    st.success(f"L'investimento finanziario (+ affitto) genera un patrimonio superiore di **{fmt(abs(delta))}**.")

# --- 9. GRAFICO E AMMORTAMENTO ---
st.divider()
g1, g2 = st.columns([1, 1])
with g1:
    # Palette Blue, Bordeaux, Grigi
    prof_colors = ["#1A3A5F", "#800020", "#4A4A4A", "#708090", "#D3D3D3"]
    voci = {"Capitale Casa": cap_netto_casa, "Tasse & Oneri": tasse_reg + sp_age + not_rogito, "Lavori & Arredi": spesa_r + spesa_m, "Costi Banca": not_mutuo + sp_perizia + imp_sost}
    fig = px.pie(names=list(voci.keys()), values=list(voci.values()), hole=0.5, color_discrete_sequence=prof_colors)
    fig.update_traces(textinfo='percent+label', textfont_size=12, hoverinfo='none')
    st.plotly_chart(fig, use_container_width=True)

with g2:
    piano = []
    res_a = cap_finanziato
    for anno in range(1, durata_anni + 1):
        int_a = 0; cap_a = 0
        for m in range(12):
            im = res_a * i_m; cm = rata - im
            int_a += im; cap_a += cm; res_a -= cm
        piano.append([anno, fmt(cap_a), fmt(int_a), fmt(max(0, res_a))])
    st.dataframe(pd.DataFrame(piano, columns=["Anno", "Capitale pagato", "Interessi pagati", "Residuo"]), use_container_width=True, hide_index=True)

# --- 10. STAMPA ---
st.info(f"LTV (Loan to Value): **{(cap_finanziato/prezzo_casa)*100:.1f}%**")
if st.button("🖨️ Stampa Report Professionale"):
    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)