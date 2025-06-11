import streamlit as st
import pandas as pd
from pyairtable import Api
import plotly.graph_objects as go
from collections import defaultdict
import numpy as np

id_to_name = {
    "2": "Heuristik",
    "3": "Metly",
    "6": "Skor",
    "7": "Robopedics",
    "9": "Quix",
    "10": "Calliope",
    "12": "Nidus Lab",
    "13": "Vivra",
    "14": "Lowerton",
    "15": "Chemometric Brain",
    "16": "Stamp",
    "17": "SheerMe",
    "18": "Zell",
    "19": "Anyformat",
    "21": "Valerdat",
    "22": "Kestrix Ltd.",
    "23": "LingLoop (Menorca)",
    "24": "Stand Up (Menorca)",
    "26": "Gaddex",
    "27": "Sheldonn",
    "28": "Vixiees",
    "29": "IKI Health Group sL",
    "30" : "ByteHide"
}

founder_id_to_name = {
    "reckEp7yXcc5kUzw4": "Joan Jover",
    "recc1YJvKk9y9sNre": "Lluis Jover Vilafranca",
    "recjj5TVqlQ73gIml": "Artem Loginov",
    "recSj5tMjcNT787Gp": "Dmitry Zaets",
    "rec9qQtBw86jdfo0x": "Paula Camps",
    "recOv4tuPs1ZJQeLB": "Nil Rodas",
    "recmdeZCzXI2DyfDk": "Juan Alberto España Garcia",
    "recJs9xDdf3GHhhbJ": "Alejandro Fernández Rodríguez",
    "recq1vn95maYO1AFF": "Diego Pérez Sastre",
    "recAwUcK4UwYCQ8Nb": "Juan Huguet",
    "recogcsAZibIk4OPH": "Joaquin Diez",
    "rec60NVqarI2s48u3": "Rafael Casuso",
    "recsOZlQNZsFDSqtw": "Henrik Stamm Kristensen",
    "recAjgqqnSqgN6v8r": "Jacob Kristensen Illán",
    "recChH7IwT6LQOyv7": "Alejandro Paloma",
    "recLQijSLzobSCODd": "Víctor Vicente Sánchez",
    "recmhid6dQCAYG88A": "Antxon Caballero",
    "recUAQITJFLdtUYIz": "Thomas Carson",
    "recSrfVzDvKFjILAx": "Patricia Puiggros",
    "rec9Jv3VH5N3S2H7c": "Silvia Fernandez Mulero",
    "recD4WlvpZsevcIHT": "Lucy Lyons",
    "recTqg6QXDwmjKLmg": "Gorka Muñecas",
    "recW3rDeBmB5tq2Kz": "Anna Torrents",
    "recvQEIoPUFehzmeJ": "Graeme Harris",
    "recYcgQh2VU8KcrgU": "Lydia Taranilla",
    "recb5zUyj1wWDjkgT": "Ana Lozano Portillo",
    "reclX7It1sxtNFHOW": "Ignacio Barrea",
    "recqudxt04FlAgcKy": "Santiago Gomez",
    "recYjsxu2q09VddMK": "Dionís Guzmán",
    "recR7t8yYqGhlIc3C": "Iván Martínez",
    "rec7zMyfjA5RSDGmm": "Marc Serra",
    "rec26pQKXNolvda2P": "Miguel Alves Ribeiro",
    "recTf976Q3xY0zWnH": "Shakil Satar",
    "recoyqN8ST1jUO58Y": "Francisco Alejandro Jurado Pérez",
    "recDBB7bHPU1q397X": "Giorgio Fidei",
    "recKFc88VGjI7xpJn": "Aditya  Malhotra",
    "reccZ0ZCEPj48DZ1h": "Carlos Moreno Martín",
    "recpb9EYIYYU8jrpq": "Abel Navajas",
    "recxzCofGUvIuTJaM": "Javier Castrillo",
    "recr0MHr9fQReJy2m": "Eduard  Aran Calonja",
    "recy3oVDwgLtha2MV": "Carlos  Arboleya",
    "recWPSZTxNWOvbL4d": "Carlos Saro",
    "recjVjpczDp5CbYsU": "Alex Sanchez",
    "rec842iG1sXEsgmf1": "Pablo Pascual",
    "recGik3FBuGqYbZN5": "Alberto Garagnani",
    "recuT12JFw2AZIEGX": "Moritz Beck"
}

def normalize_list(value):
    """Return a list no matter what Airtable gives back."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return [] if value is None or (isinstance(value, float) and pd.isna(value)) else [str(value)]

def get_founder_id(val):
    """Handle Airtable linked-record objects or plain IDs."""
    return val.get("id") if isinstance(val, dict) else val

st.set_page_config(
    page_title="Startup Program Feedback Dashboard",
    page_icon=".streamlit/static/favicon.png",  # or "🚀", or "📊", or a path to a .png
    layout="wide"
)

AIRTABLE_PAT = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_ID = st.secrets["airtable"]["table_id"]

# === Airtable Connection ===
api = Api(AIRTABLE_PAT)
table = api.table(BASE_ID, TABLE_ID)
records = table.all()

df = pd.DataFrame([r["fields"] for r in records])

def fix_cell(val):
    if isinstance(val, dict) and "specialValue" in val:
        return float("nan")
    return val

df = df.applymap(fix_cell)

df = df[df["Id"].notna()]
df["Id"] = df["Id"].astype(str)

# representacion de arañas
def radar_chart(scores, labels, title):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name=title
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 4])
        ),
        showlegend=False,
        height=450,
        title=title
    )
    return fig

# Dropdown de st's
valid_ids = [id_ for id_ in df["Id"].unique() if id_ in id_to_name]
selected_id = st.selectbox(
    "Choose a Startup",
    options=sorted(valid_ids, key=int),
    format_func=lambda x: id_to_name.get(x, f"Startup {x}")
)

filtered = df[df["Id"] == selected_id]
if filtered.empty:
    st.warning("❌ No data for the selected startup.")
    st.stop()

row = filtered.iloc[0]

# =========Primera fila de arañas============
col1, col2, col3 = st.columns(3)

with col1:
    risk_reward_scores = {
        "Sate of development": row.get("Average RISK | State of development_Score",0),
        "Momentum": row.get("Average RISK | Momentum_Score", 0),
        "Management": row.get("Average RISK | Management_Score", 0),
        "Market": row.get("Average RISK | Market_Score", 0),
        "Team": row.get("Average RISK | Team_Score", 0),
        "Pain": row.get("Average RISK | Pain_Score", 0),
        "Scalability": row.get("Average RISK | Scalability_Score", 0)
    }
    risk_reward_df = pd.DataFrame.from_dict(risk_reward_scores, orient="index", columns=["Score"]).reset_index()
    risk_reward_df.columns = ["Category", "Score"]

st.plotly_chart(
    radar_chart(
        risk_reward_df["Score"].tolist(),
        risk_reward_df["Category"].tolist(),
        "Risk/Reward Analysis"
    )
)