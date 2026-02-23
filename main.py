# main.py

import streamlit as st
import pandas as pd

from utils import fmt
from input import (
    get_asset_inputs,
    get_fondo_inputs,
    get_spese_inputs,
    get_sostenibilita_inputs,
    get_scenario_investimento_inputs
)
from calcoli import (
    calcola_imposte,
    calcola_fondo_pensione,
    calcola_mutuo,
    risparmio_interessi_da_fondo,
    patrimonio_acquisto,
    scenario_investimento,
    calcola_dti,
    piano_ammortamento
)
from grafici import grafico_costi
from ui import (
    card_navy,
    card_gray,
    box_banca,
    box_advisor,
    footer,
    pulsante_stampa
)

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------

st.set_page_config(page_title="Asset Advisor Pro | Modular Edition", layout="wide")

st.title("🏛️ Asset Advisor Pro")
st.markdown("<p style='color:#666;'>Analisi strategica patrimoniale: Immobiliare, Previdenza e Sostenibilità Creditizia.</p>", unsafe_allow_html=True)
st.divider()

# ---------------------------------------------------------
# 1. INPUT
# ---------------------------------------------------------

asset = get_asset_inputs()
fondo = get_fondo_inputs(asset["tipo_casa"])
spese = get_spese_inputs()
sost = get_sostenibilita_inputs()
scenario = get_scenario_investimento_inputs()

# ---------------------------------------------------------
# 2. CALCOLI PRINCIPALI
# ---------------------------------------------------------

# Imposte acquisto
tasse_acq = calcola_imposte(
    prezzo=asset["prezzo"],
    rendita=asset["rendita"],
    tipo_casa=asset["tipo_casa"],
    venditore=asset["venditore"]
)

# Fondo pensione
fondo_res = calcola_fondo_pensione(
    anzianita=fondo["anzianita"],
    montante_v=fondo["montante_v"],
    montante_g=fondo["montante_g"],
    perc=fondo["perc_riscatto"]
)

riduzione_fondo = fondo_res.netto if fondo["usa_fondo"] else 0

# Fabbisogno finanziario
fabbisogno = (
    asset["prezzo"] +
    tasse_acq +
    spese["agenzia"] +
    spese["notaio"] +
    spese["perizia"] +
    spese["ristr"] +
    spese["arredi"]
) - asset["anticipo"] - riduzione_fondo

# Mutuo
mutuo = calcola_mutuo(
    fabbisogno=fabbisogno,
    tipo_casa=asset["tipo_casa"],
    tan=spese["tan"],
    anni=asset["durata"]
)

# Sostenibilità
dti = calcola_dti(
    rata=mutuo.rata,
    altri_debiti=sost["altri_debiti"],
    reddito=sost["reddito"]
)

status = "COMPATIBILE" if dti <= 33 else "CRITICO"

# Scenario alternativo
capitale_iniziale = asset["anticipo"] + (fondo_res.netto if fondo_res.netto > 0 else 0)

patr_inv = scenario_investimento(
    anni=asset["durata"],
    capitale=capitale_iniziale,
    rendimento=scenario["rendimento"],
    canone=scenario["canone"]
)

# Valore futuro immobile (default rivalutazione 1.5%)
valore_futuro = asset["prezzo"] * (1 + 0.015)**asset["durata"]

# Piano ammortamento
piano = piano_ammortamento(
    mutuo=mutuo.mutuo_totale,
    tan=spese["tan"],
    anni=asset["durata"]
)

debito_residuo = piano[-1]["Residuo"]

# Patrimonio netto acquisto
costi_vivi = (
    tasse_acq +
    spese["agenzia"] +
    spese["notaio"] +
    spese["perizia"] +
    spese["ristr"] +
    spese["arredi"]
)

patr_acq = patrimonio_acquisto(
    valore_futuro=valore_futuro,
    debito_residuo=debito_residuo,
    costi_vivi=costi_vivi
)

# ---------------------------------------------------------
# 3. OUTPUT UI
# ---------------------------------------------------------

st.subheader("🏦 4. Sostenibilità e Fattibilità Creditizia")

col1, col2 = st.columns([1, 2])

with col1:
    card_navy("RATA MENSILE", mutuo.rata)
    st.write("")
    card_navy("MUTUO LORDO RICHIESTO", mutuo.mutuo_totale)

with col2:
    box_banca(status, dti)

# Advisor fondo pensione
if fondo_res.netto > 0 and fondo["usa_fondo"]:
    risp = risparmio_interessi_da_fondo(
        mutuo=mutuo.mutuo_totale,
        tan=spese["tan"],
        anni=asset["durata"],
        fondo=fondo_res.netto
    )
    if risp > fondo_res.tasse:
        box_advisor(risp, fondo_res.tasse)

# ---------------------------------------------------------
# 4. VERDETTO ASSET ADVISOR
# ---------------------------------------------------------

st.subheader("📈 5. Verdetto Asset Advisor")

c1, c2 = st.columns(2)

with c1:
    card_navy("NETTO ACQUISTO", patr_acq)

with c2:
    card_gray("NETTO INVESTIMENTO", patr_inv)

# ---------------------------------------------------------
# 5. GRAFICO COSTI
# ---------------------------------------------------------

st.subheader("📊 Distribuzione Costi")

voci = {
    "Mutuo": mutuo.mutuo_totale,
    "Imposte": tasse_acq,
    "Agenzia": spese["agenzia"],
    "Notaio": spese["notaio"],
    "Ristrutturazione": spese["ristr"],
    "Arredi": spese["arredi"]
}

fig = grafico_costi(voci)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 6. PIANO AMMORTAMENTO
# ---------------------------------------------------------

with st.expander("📅 Piano di Ammortamento"):
    df = pd.DataFrame(piano)
    df["Capitale"] = df["Capitale"].apply(fmt)
    df["Interessi"] = df["Interessi"].apply(fmt)
    df["Residuo"] = df["Residuo"].apply(fmt)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 7. FOOTER & STAMPA
# ---------------------------------------------------------

pulsante_stampa()
footer()
