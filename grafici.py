# grafici.py

import plotly.express as px

def grafico_costi(voci: dict):
    """
    Grafico a torta dei costi principali.
    """
    fig = px.pie(
        names=list(voci.keys()),
        values=list(voci.values()),
        hole=0.6,
        color_discrete_sequence=[
            "#1A3A5F", "#4A4A4A", "#708090", "#999", "#555", "#777"
        ]
    )
    fig.update_traces(textinfo='label+percent', textposition='outside')
    return fig
