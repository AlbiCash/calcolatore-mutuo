# input.py

import streamlit as st
from utils import parse_it_perc


# ---------------------------------------------------------
# 1. INPUT ASSET IMMOBILIARE
# ---------------------------------------------------------

def get_asset_inputs():
    st.subheader("📍 1. Configurazione Asset")

    c1, c2, c3 = st.columns(3)

    with c1:
        prezzo = st.number_input(
            "Prezzo acquisto immobile (€)",
            min_value=0,
            value=250000,
            step=5000
        )
        anticipo = st.number_input(
            "Capitale Proprio (Anticipo) (€)",
            min_value=0,
            value=50000,
            step=5000
        )

    with c2:
        venditore = st.selectbox(
            "Soggetto Venditore:",
            ["Privato (Imposta Registro)", "Costruttore (Soggetto a IVA)"]
        )
        rendita = st.number_input(
            "Valore catastale (Rendita) (€)",
            min_value=0,
            value=1000
        )

    with c3:
        tipo_casa = st.selectbox(
            "Tipologia Immobile",
            ["Prima Casa", "Seconda Casa", "Immobile di Lusso"]
        )
        durata = st.select_slider(
            "Orizzonte Temporale (Anni)",
            options=list(range(5, 41)),
            value=30
        )

    return {
        "prezzo": prezzo,
        "anticipo": anticipo,
        "venditore": venditore,
        "rendita": rendita,
        "tipo_casa": tipo_casa,
        "durata": durata
    }


# ---------------------------------------------------------
# 2. INPUT FONDO PENSIONE
# ---------------------------------------------------------

def get_fondo_inputs(tipo_casa: str):
    """
    Ritorna:
    - dati fondo
    - flag utilizzo fondo
    """
    if tipo_casa != "Prima Casa":
        return {
            "anzianita": 0,
            "montante_v": 0,
            "montante_g": 0,
            "perc_riscatto": 0,
            "usa_fondo": False
        }

    st.subheader("📈 2. Analisi Previdenziale")

    with st.expander("Calcola riscatto fondo pensione per acquisto Prima Casa"):
        c1, c2, c3 = st.columns(3)

        anz = c1.number_input("Anzianità Fondo (Anni)", value=8)
        mv = c2.number_input("Montante Contributi (€)", value=0)
        mg = c3.number_input("Montante Rendimenti (€)", value=0)

        perc = st.slider("% di Riscatto desiderata", 0, 75, 75)

        usa = st.toggle("Applica riscatto per abbattere l'importo del mutuo", value=False)

    return {
        "anzianita": anz,
        "montante_v": mv,
        "montante_g": mg,
        "perc_riscatto": perc,
        "usa_fondo": usa
    }


# ---------------------------------------------------------
# 3. INPUT SPESE E TASSI
# ---------------------------------------------------------

def get_spese_inputs():
    st.subheader("🛠️ 3. Spese, Lavori e Tassi")

    c1, c2, c3 = st.columns(3)

    with c1:
        ristr = st.number_input("Budget Ristrutturazione (€)", value=0, step=5000)
        arredi = st.number_input("Budget Arredamento (€)", value=0, step=2000)

    with c2:
        agenzia = st.number_input("Provvigione Agenzia (€)", value=7500)
        notaio = st.number_input("Oneri Notarili (€)", value=3000)

    with c3:
        perizia = st.number_input("Istruttoria/Perizia/Assicurazioni (€)", value=1500)
        tan = parse_it_perc("Tasso Annuo (TAN) %", "3,5")

    return {
        "ristr": ristr,
        "arredi": arredi,
        "agenzia": agenzia,
        "notaio": notaio,
        "perizia": perizia,
        "tan": tan
    }


# ---------------------------------------------------------
# 4. INPUT SOSTENIBILITÀ
# ---------------------------------------------------------

def get_sostenibilita_inputs():
    st.subheader("🏦 4. Sostenibilità e Fattibilità Creditizia")

    c1, c2 = st.columns(2)

    with c1:
        reddito = st.number_input("Reddito Mensile Netto Famiglia (€)", min_value=1, value=3500)
        altri = st.number_input("Altri prestiti/debiti (€/mese)", value=0)

    with c2:
        sp_ord = st.number_input("Spese Gestione Casa (€/mese)", value=250)
        sp_str = st.number_input("Accantonamento Straordinario (€/anno)", value=1000)

    return {
        "reddito": reddito,
        "altri_debiti": altri,
        "spese_ord": sp_ord,
        "spese_str": sp_str
    }


# ---------------------------------------------------------
# 5. INPUT SCENARIO INVESTIMENTO
# ---------------------------------------------------------

def get_scenario_investimento_inputs():
    with st.expander("Scenario Alternativo (Investimento)"):
        canone = st.number_input("Canone mensile affitto (€)", value=0)
        rendimento = st.slider("Rendimento annuo portafoglio (%)", 1, 9, 4)

    return {
        "canone": canone,
        "rendimento": rendimento
    }
