# utils.py
import streamlit as st

# -----------------------------
# FORMATTATORE EURO
# -----------------------------
def fmt(val: float) -> str:
    """
    Formatta un numero in stile euro con separatore dei migliaia.
    Esempio: 123456 -> "€ 123.456"
    """
    try:
        return f"€ {int(round(val, 0)):,}".replace(",", ".")
    except Exception:
        return "€ 0"


# -----------------------------
# PARSER PERCENTUALI ITALIANE
# -----------------------------
def parse_it_perc(
    label: str,
    default: str = "3,5",
    help_text: str = ""
) -> float:
    """
    Gestisce input percentuali in formato italiano (virgola).
    Restituisce un float (es. "3,5" -> 3.5).
    Mostra errori Streamlit se l'utente usa il punto.
    """
    val = st.text_input(label, value=default, help=help_text)

    # Errore: l'utente usa il punto
    if "." in val:
        st.error("⚠️ Usa la virgola (,) non il punto (.)")
        return 0.0

    # Parsing sicuro
    try:
        return float(val.replace(",", "."))
    except ValueError:
        st.error("⚠️ Formato non valido. Usa numeri tipo: 3,5")
        return 0.0


# -----------------------------
# VALIDATORE INPUT NUMERICI
# -----------------------------
def safe_float(value, default=0.0) -> float:
    """
    Converte in float in modo sicuro.
    """
    try:
        return float(value)
    except:
        return default


# -----------------------------
# VALIDATORE PERCENTUALI (0-100)
# -----------------------------
def clamp_percentage(val: float) -> float:
    """
    Garantisce che una percentuale sia tra 0 e 100.
    """
    return max(0, min(val, 100))


# -----------------------------
# CONVERSIONE ANNUALE → MENSILE
# -----------------------------
def annual_to_monthly_rate(tan: float) -> float:
    """
    Converte TAN annuo in tasso mensile.
    Esempio: 3.5 -> 0.0029
    """
    return (tan / 100) / 12
