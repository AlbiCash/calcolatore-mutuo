import streamlit as st
import plotly.express as px
import pandas as pd
import streamlit.components.v1 as components

# --- 1. CONFIGURAZIONE & STILE ---
st.set_page_config(page_title="Asset Advisor Pro | Beta 0.1.6", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Stile pulsanti e card */
    .stButton>button {width: 100%; border-radius: 2px; height: 3em; background-color: #1A3A5F; color: white; font-weight: bold; border: none;}
    .navy-card {background-color: #1A3A5F; color: white !important; padding: 30px; border-radius: 5px; text-align: center;}
    .navy-card h1, .navy-card h2, .navy-card h3, .navy-card p {color: white !important;}
    .bank-box {background-color: #f1f3f5; border: 2px solid #1A3A5F; padding: 20px; border-radius: 5px; color: #1A3A5F !important;}
    .advice-box {padding: 25px; border-left: 8px solid #1A3A5F !important; background-color: #f8f9fa !important; color: #1A3A5F !important; font-weight: 500; margin: 20px 0px; border-radius: 4px;}
    
    /* Footer */
    .footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f3f5; color: #666; text-align: center; padding: 10px; font-size: 0.8em; border-top: 1px solid #ddd; z-index: 100;}

    /* LOGICA PER LA STAMPA: Nasconde elementi non necessari nel PDF */
    @media print {
        .stButton, .footer, .stSelectbox, .stNumberInput, .stSlider, .stExpander, hr {
            display: none !important;
        }
        .main {
            background-color: white !important;
        }
        .navy-card {
            background-color: #1A3A5F !important;
            -webkit-print-color-adjust: exact;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def fmt(valore):
    return f"€ {int(round(valore, 0)):,}".replace(",", ".")

def parse_it_perc(label, default="3,5", help_text=""):
    val = st.text_input(label, value=default, help=help_text)
    if "." in val:
        st.error("⚠️ Usa la virgola (,) non il punto (.)")
        return 0.0
    try: return float(val.replace(",", "."))
    except: return 0.0

# --- 2. HEADER ---
st.title("🏛️ Asset Advisor Pro")
st.markdown("<p style='color:#666;'>Analisi strategica patrimoniale: Immobiliare, Previdenza e Sostenibilità Creditizia.</p>", unsafe_allow_html=True)

st.divider()

# --- 3. INPUT ASSET ---
st.subheader("📍 1. Configurazione Asset")
c1, c2, c3 = st.columns(3)
with c1:
    prezzo_casa = st.number_input("Prezzo acquisto immobile (€)", min_value=0, value=250000, step=5000, help="Il prezzo di compravendita pattuito tra le parti.")
    anticipo_cash = st.number_input("Capitale Proprio (Anticipo) (€)", min_value=0, value=50000, step=5000, help="Liquidità totale versata subito (escluso il fondo pensione).")
with c2:
    tipo_venditore = st.selectbox("Soggetto Venditore:", ["Privato (Imposta Registro)", "Costruttore (Soggetto a IVA)"], help="Scegli 'Costruttore' per immobili nuovi o ristrutturati dalla società negli ultimi 5 anni.")
    valore_catastale = st.number_input("Valore catastale (€)", min_value=0, value=1000, help="Dato reperibile sulla visura catastale (Rendita).")
with c3:
    tipo_casa = st.selectbox("Tipologia Immobile", ["Prima Casa", "Seconda Casa", "Immobile di Lusso"], help="Influisce sulle aliquote fiscali (IVA/Registro) e sull'imposta sostitutiva.")
    durata_anni = st.select_slider("Orizzonte Temporale (Anni)", options=list(range(5, 41)), value=30, help="Durata del mutuo. Default 30 anni.")

# --- 4. LOGICA FONDO PENSIONE (SOLO PRIMA CASA) ---
netto_fondo = 0.0
tasse_fondo = 0.0
usa_fondo_per_mutuo = False

if tipo_casa == "Prima Casa":
    st.divider()
    st.subheader("📈 2. Analisi Previdenziale")
    with st.expander("Calcola riscatto fondo pensione per acquisto Prima Casa", expanded=False):
        f1, f2, f3 = st.columns(3)
        anz_f = f1.number_input("Anzianità Fondo (Anni)", value=8, help="Minimo 8 anni per acquisto prima casa.")
        m_v = f2.number_input("Montante Contributi (€)", value=0, help="Somma dei contributi versati.")
        m_g = f3.number_input("Montante Rendimenti (€)", value=0, help="Quota generata dalla gestione finanziaria.")
        
        if anz_f >= 8:
            tot_f = m_v + m_g
            max_ant = tot_f * 0.75
            st.info(f"Anticipo massimo richiedibile (75%): {fmt(max_ant)}")
            perc_r = st.slider("% di Riscatto desiderata", 0, 75, 75)
            
            if tot_f > 0:
                lordo_r = tot_f * (perc_r/100)
                qv_r = lordo_r * (m_v/tot_f)
                qg_r = lordo_r * (m_g/tot_f)
                tasse_fondo = qv_r * 0.23 # Tassazione 23% solo su versato
                netto_fondo = (qv_r - tasse_fondo) + qg_r
                st.success(f"Liquidità Netta Ottenibile: **{fmt(netto_fondo)}**")
                usa_fondo_per_mutuo = st.toggle("Applica riscatto per abbattere l'importo del mutuo", value=False)
        else:
            st.warning("⚠️ Riscatto non disponibile per anzianità inferiore a 8 anni.")

# --- 5. ONERI E TASSI ---
st.divider()
st.subheader("🛠️ 3. Spese, Lavori e Tassi")
c4, c5, c6 = st.columns(3)
with c4:
    sp_ristr = st.number_input("Budget Ristrutturazione (€)", value=0, step=5000, help="Incluso nel mutuo richiesto.")
    sp_arredi = st.number_input("Budget Arredamento (€)", value=0, step=2000)
with c5:
    sp_age = st.number_input("Provvigione Agenzia (€)", value=7500, help="Mediazione immobiliare.")
    not_tot = st.number_input("Oneri Notarili (€)", value=3000, help="Atto acquisto e mutuo.")
with c6:
    sp_perizia = st.number_input("Istruttoria/Perizia/Assicurazioni (€)", value=1500)
    tasso_annuo = parse_it_perc("Tasso Annuo (TAN) %", "3,5", help_text="Tasso nominale applicato dalla banca.")

# --- CALCOLI FINANZIARI ---
if tipo_venditore == "Privato (Imposta Registro)":
    tasse_acq = ((valore_catastale * 110) * 0.02 + 100) if "Prima Casa" in tipo_casa else ((valore_catastale * 120) * 0.09 + 100)
else:
    aliquota = 0.04 if "Prima Casa" in tipo_casa else (0.22 if "Lusso" in tipo_casa else 0.10)
    tasse_acq = (prezzo_casa * aliquota) + 600

riduzione_da_fondo = netto_fondo if usa_fondo_per_mutuo else 0
fabbisogno_nudo = (prezzo_casa + tasse_acq + sp_age + not_tot + sp_perizia + sp_ristr + sp_arredi) - anticipo_cash - riduzione_da_fondo
imp_sost = fabbisogno_nudo * (0.0025 if "Prima Casa" in tipo_casa else 0.02)
mutuo_totale = max(0, fabbisogno_nudo + imp_sost)

i_m = (tasso_annuo / 100) / 12
n_m = durata_anni * 12
rata = mutuo_totale * (i_m * (1 + i_m)**n_m) / ((1 + i_m)**n_m - 1) if i_m > 0 else mutuo_totale / n_m
interessi_t = (rata * n_m) - mutuo_totale

# --- 6. SOSTENIBILITÀ ---
st.divider()
st.subheader("🏦 4. Sostenibilità e Fattibilità Creditizia")
col_rata, col_reddito = st.columns([1, 2])

with col_rata:
    st.markdown(f"""
        <div class="navy-card">
            <p style='margin:0;opacity:0.8;'>RATA MENSILE</p>
            <h1 style='margin:0;'>{fmt(rata)}</h1>
            <hr style='border: 0.5px solid white; opacity:0.3;'>
            <p style='margin:0;opacity:0.8;font-size:0.9em;'>MUTUO LORDO RICHIESTO</p>
            <h2 style='margin:0;'>{fmt(mutuo_totale)}</h2>
        </div>
        """, unsafe_allow_html=True)

with col_reddito:
    r1, r2 = st.columns(2)
    reddito_f = r1.number_input("Reddito Mensile Netto Famiglia (€)", min_value=1, value=3500)
    altri_debiti = r1.number_input("Altri prestiti/debiti (€/mese)", value=0)
    sp_casa_ord = r2.number_input("Spese Gestione Casa (€/mese)", value=250)
    sp_casa_str = r2.number_input("Accantonamento Straordinario (€/anno)", value=1000)
    
    dti = ((rata + altri_debiti) / reddito_f) * 100
    status_bank = "COMPATIBILE ✅" if dti <= 33 else "CRITICO ⚠️"
    color_bank = "green" if dti <= 33 else "red"
    
    st.markdown(f"""
    <div class="bank-box">
        <b>🔍 Esito Simulazione Delibera:</b> <span style="color:{color_bank}; font-weight:bold;">{status_bank}</span><br>
        Rapporto Rata/Reddito: <b>{dti:.1f}%</b><br>
        Esborso Mensile Reale: <b>{fmt(rata + altri_debiti + sp_casa_ord + (sp_casa_str/12))}</b>
    </div>
    """, unsafe_allow_html=True)

# --- 7. ASSET ADVISOR ---
st.divider()
st.subheader("📈 5. Verdetto Asset Advisor")

rival_imm = parse_it_perc("% Rivalutazione annua immobile", "1,5") / 100
val_imm_f = prezzo_casa * (1 + rival_imm)**durata_anni
costi_tot_acq = interessi_t + (tasse_acq + sp_age + not_tot + sp_perizia) + sp_ristr + (sp_casa_str * durata_anni)
patr_netto_acq = val_imm_f - costi_tot_acq

with st.expander("Scenario Alternativo (Investimento)", expanded=False):
    canone_affitto = st.number_input("Canone mensile affitto (€)", value=0)
    resa_inv = st.slider("Rendimento annuo portafoglio (%)", 1, 9, 4)
    cost_aff_tot = 0; curr_can = canone_affitto
    for a in range(durata_anni): cost_aff_tot += (curr_can * 12); curr_can *= 1.02
    cap_i_inv = anticipo_cash + (netto_fondo if netto_fondo > 0 else 0)
    
    mont_n = (cap_i_inv * (1 + (resa_inv/100))**durata_anni)
    mont_n -= (mont_n - cap_i_inv) * 0.20
    patr_netto_inv = mont_n - cost_aff_tot

ca1, ca2 = st.columns(2)
with ca1: st.markdown(f"<div class='navy-card'><h3>NETTO ACQUISTO</h3><h2>{fmt(patr_netto_acq)}</h2></div>", unsafe_allow_html=True)
with ca2: st.markdown(f"<div class='navy-card' style='background-color:#4A4A4A'><h3>NETTO INVESTIMENTO</h3><h2>{fmt(patr_netto_inv)}</h2></div>", unsafe_allow_html=True)

# CONSIGLIO PREVIDENZIALE
if netto_fondo > 0:
    risparmio_int = (interessi_t / mutuo_totale * netto_fondo) if mutuo_totale > 0 else 0
    if risparmio_int > tasse_fondo:
        st.markdown(f"<div class='advice-box'>🎯 <b>ADVISOR:</b> Risparmio interessi ({fmt(risparmio_int)}) > Tasse riscatto ({fmt(tasse_fondo)}). L'uso del fondo è efficiente.</div>", unsafe_allow_html=True)

# --- 8. GRAFICO & PIANO ---
st.divider()
g1, g2 = st.columns([1.2, 1])
with g1:
    voci = {"Mutuo": mutuo_totale, "Oneri/Tasse": tasse_acq + imp_sost + sp_age + not_tot + sp_perizia, "Lavori": sp_ristr + sp_arredi}
    fig = px.pie(names=list(voci.keys()), values=list(voci.values()), hole=0.6, color_discrete_sequence=["#1A3A5F", "#4A4A4A", "#708090"])
    fig.update_traces(textinfo='label+percent', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
with g2:
    st.table(pd.DataFrame({
        " ": ["🏠", "⚖️", "🤝", "🖊️", "🏗️", "🏦"],
        "Voce": ["Prezzo Casa", "Imposte", "Agenzia", "Notaio", "Ristrutturazione", "Mutuo Lordo"],
        "Valore": [fmt(prezzo_casa), fmt(tasse_acq), fmt(sp_age), fmt(not_tot), fmt(sp_ristr), fmt(mutuo_totale)]
    }))

# --- 9. PIANO AMMORTAMENTO ---
with st.expander("📅 Piano di Ammortamento"):
    piano = []; res_p = mutuo_totale
    for anno in range(1, durata_anni + 1):
        i_a = 0; c_a = 0
        for m in range(12):
            im = res_p * i_m; cm = rata - im
            i_a += im; c_a += cm; res_p -= cm
        piano.append([anno, fmt(c_a), fmt(i_a), fmt(max(0, res_p))])
    st.dataframe(pd.DataFrame(piano, columns=["Anno", "Capitale", "Interessi", "Residuo"]), use_container_width=True, hide_index=True)

# --- 10. FOOTER & FIX STAMPA ---
st.divider()

# Bottone Stampa con JavaScript integrato per bypassare i blocchi iframe
if st.button("🖨️ Stampa Report PDF"):
    components.html(
        """
        <script>
            window.parent.print();
        </script>
        """,
        height=0,
    )

st.markdown("""<div class="footer">Asset Advisor Pro | <b>Beta Test 0.1.6</b> | Income & Printing Fix</div>""", unsafe_allow_html=True)