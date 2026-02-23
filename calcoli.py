# calcoli.py

from dataclasses import dataclass
from typing import List, Dict
from math import pow

# ---------------------------------------------------------
# 1. IMPOSTE ACQUISTO
# ---------------------------------------------------------

def calcola_imposte(prezzo: float, rendita: float, tipo_casa: str, venditore: str) -> float:
    """
    Calcola le imposte di acquisto in base alla normativa corretta.
    """
    if venditore == "Privato (Imposta Registro)":
        if tipo_casa == "Prima Casa":
            base = rendita * 115.5
            return base * 0.02 + 100
        else:
            base = rendita * 126
            return base * 0.09 + 100

    # Venditore costruttore → IVA
    if tipo_casa == "Prima Casa":
        aliquota = 0.04
    elif tipo_casa == "Immobile di Lusso":
        aliquota = 0.22
    else:
        aliquota = 0.10

    return prezzo * aliquota + 600


# ---------------------------------------------------------
# 2. FONDO PENSIONE
# ---------------------------------------------------------

@dataclass
class FondoResult:
    netto: float
    tasse: float
    lordo: float


def calcola_fondo_pensione(anzianita: int, montante_v: float, montante_g: float, perc: float) -> FondoResult:
    """
    Calcola il riscatto fondo pensione (solo parte versata tassata).
    Gestisce correttamente il caso tot = 0 per evitare divisioni per zero.
    """
    if anzianita < 8:
        return FondoResult(0, 0, 0)

    tot = montante_v + montante_g

    # Caso limite: nessun montante → nessun riscatto
    if tot <= 0:
        return FondoResult(0, 0, 0)

    lordo = tot * (perc / 100)

    quota_v = lordo * (montante_v / tot)
    quota_g = lordo * (montante_g / tot)

    tasse = quota_v * 0.23
    netto = (quota_v - tasse) + quota_g

    return FondoResult(netto=netto, tasse=tasse, lordo=lordo)


# ---------------------------------------------------------
# 3. MUTUO
# ---------------------------------------------------------

@dataclass
class MutuoResult:
    rata: float
    interessi_tot: float
    mutuo_totale: float


def calcola_mutuo(fabbisogno: float, tipo_casa: str, tan: float, anni: int) -> MutuoResult:
    """
    Calcola mutuo totale, rata e interessi totali.
    """
    imp_sost = fabbisogno * (0.0025 if tipo_casa == "Prima Casa" else 0.02)
    mutuo = fabbisogno + imp_sost

    i_m = (tan / 100) / 12
    n_m = anni * 12

    if i_m == 0:
        rata = mutuo / n_m
    else:
        rata = mutuo * (i_m * pow(1 + i_m, n_m)) / (pow(1 + i_m, n_m) - 1)

    interessi = rata * n_m - mutuo

    return MutuoResult(rata=rata, interessi_tot=interessi, mutuo_totale=mutuo)


# ---------------------------------------------------------
# 4. RISPARMIO INTERESSI DA FONDO (corretto)
# ---------------------------------------------------------

def risparmio_interessi_da_fondo(mutuo: float, tan: float, anni: int, fondo: float) -> float:
    """
    Calcola il risparmio reale di interessi confrontando:
    - mutuo pieno
    - mutuo ridotto dal fondo
    """
    if fondo <= 0:
        return 0

    full = calcola_mutuo(mutuo, "Prima Casa", tan, anni)
    ridotto = calcola_mutuo(mutuo - fondo, "Prima Casa", tan, anni)

    return full.interessi_tot - ridotto.interessi_tot


# ---------------------------------------------------------
# 5. PATRIMONIO NETTO ACQUISTO
# ---------------------------------------------------------

def patrimonio_acquisto(valore_futuro: float, debito_residuo: float, costi_vivi: float) -> float:
    return valore_futuro - debito_residuo - costi_vivi


# ---------------------------------------------------------
# 6. SCENARIO INVESTIMENTO
# ---------------------------------------------------------

def scenario_investimento(anni: int, capitale: float, rendimento: float, canone: float) -> float:
    montante = capitale * pow(1 + rendimento / 100, anni)
    tasse = (montante - capitale) * 0.20
    montante_netto = montante - tasse

    costo_aff = 0
    curr = canone
    for _ in range(anni):
        costo_aff += curr * 12
        curr *= 1.02

    return montante_netto - costo_aff


# ---------------------------------------------------------
# 7. DTI
# ---------------------------------------------------------

def calcola_dti(rata: float, altri_debiti: float, reddito: float) -> float:
    if reddito <= 0:
        return 999
    return ((rata + altri_debiti) / reddito) * 100


# ---------------------------------------------------------
# 8. PIANO AMMORTAMENTO
# ---------------------------------------------------------

def piano_ammortamento(mutuo: float, tan: float, anni: int) -> List[Dict]:
    i_m = (tan / 100) / 12
    n_m = anni * 12

    if i_m == 0:
        rata = mutuo / n_m
    else:
        rata = mutuo * (i_m * pow(1 + i_m, n_m)) / (pow(1 + i_m, n_m) - 1)

    residuo = mutuo
    piano = []

    for anno in range(1, anni + 1):
        cap_annuo = 0
        int_annuo = 0

        for _ in range(12):
            interesse = residuo * i_m
            capitale = rata - interesse
            residuo -= capitale

            cap_annuo += capitale
            int_annuo += interesse

        piano.append({
            "Anno": anno,
            "Capitale": cap_annuo,
            "Interessi": int_annuo,
            "Residuo": max(0, residuo)
        })

    return piano
