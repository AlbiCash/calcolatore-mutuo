# ui.py

import streamlit as st
import streamlit.components.v1 as components
from utils import fmt


# ---------------------------------------------------------
# CARD NAVY (blu)
# ---------------------------------------------------------

def card_navy(titolo: str, valore: float):
    st.markdown(f"""
        <div style="
            background:#1A3A5F;
            color:white;
            padding:25px;
            border-radius:5px;
            text-align:center;">
            <h3>{titolo}</h3>
            <h2>{fmt(valore)}</h2>
        </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# CARD GRIGIA
# ---------------------------------------------------------

def card_gray(titolo: str, valore: float):
    st.markdown(f"""
        <div style="
            background:#4A4A4A;
            color:white;
            padding:25px;
            border-radius:5px;
            text-align:center;">
            <h3>{titolo}</h3>
            <h2>{fmt(valore)}</h2>
        </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# BOX BANCA (DTI)
# ---------------------------------------------------------

def box_banca(status: str, dti: float):
    color = "green" if status == "COMPATIBILE" else "red"
    st.markdown(f"""
        <div style="
            background:#f1f3f5;
            border:2px solid #1A3A5F;
            padding:20px;
            border-radius:5px;">
            <b>🔍 Esito Simulazione Delibera:</b>
            <span style="color:{color};font-weight:bold;">{status}</span><br>
            Rapporto Rata/Reddito: <b>{dti:.1f}%</b>
        </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# BOX ADVISOR (fondo pensione)
# ---------------------------------------------------------

def box_advisor(risparmio: float, tasse: float):
    st.markdown(f"""
        <div style="
            padding:25px;
            border-left:8px solid #1A3A5F;
            background:#f8f9fa;
            color:#1A3A5F;
            font-weight:500;
            margin:20px 0;
            border-radius:4px;">
            🎯 <b>ADVISOR:</b> Risparmio interessi ({fmt(risparmio)}) 
            > Tasse riscatto ({fmt(tasse)}).  
            L'uso del fondo è efficiente.
        </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

def footer():
    st.markdown("""
        <div style="
            position:fixed;
            left:0;
            bottom:0;
            width:100%;
            background:#f1f3f5;
            color:#666;
            text-align:center;
            padding:10px;
            font-size:0.8em;
            border-top:1px solid #ddd;
            z-index:100;">
            Asset Advisor Pro | <b>Modular Edition</b>
        </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# PULSANTE STAMPA PDF
# ---------------------------------------------------------

def pulsante_stampa():
    if st.button("🖨️ Stampa Report PDF"):
        components.html(
            """
            <script>
                window.parent.print();
            </script>
            """,
            height=0,
        )
