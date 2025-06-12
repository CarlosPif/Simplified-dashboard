import streamlit as st
import pandas as pd
from pyairtable import Api
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import numpy as np
import re
import streamlit.components.v1 as components

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

# === Fix {'specialValue': 'NaN'} values ===
def fix_cell(val):
    if isinstance(val, dict) and "specialValue" in val:
        return float("nan")
    return val

df = df.applymap(fix_cell)
df2 = df.copy()

# === Fallback to Id as startup identifier ===
df = df[df["Id"].notna()]
df["Id"] = df["Id"].astype(str)

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

#======================Comenzamos con Individual========================

individual_columns = [
    "Purpose | Average",
    "Integrity and honesty | Average",
    "Relevant experience | Average",
    "Visionary leadership | Average",
    "Flexibility | Average",
    "Emotional intelligence | Average"
]

table_purp = normalize_list(row.get("Purpose | Founder & Score", []))
tags_purp = [p.strip() for entry in table_purp for p in entry.split(", ")]

table_int = normalize_list(row.get("Integrity and honesty | Founder & Score", []))
tags_int = [p.strip() for entry in table_int for p in entry.split(", ")]

table_rel = normalize_list(row.get("Relevant experience | Founder & Score", []))
tags_rel = [p.strip() for entry in table_rel for p in entry.split(", ")]

table_vis = normalize_list(row.get("Visionary leadership | Founder & Score", []))
tags_vis = [p.strip() for entry in table_vis for p in entry.split(", ")]

table_flex = normalize_list(row.get("Flexibility | Founder & Score", []))
tags_flex = [p.strip() for entry in table_flex for p in entry.split(", ")]

table_emo = normalize_list(row.get("Emotional intelligence | Founder & Score", []))
tags_emo = [p.strip() for entry in table_emo for p in entry.split(", ")]

list_hum = [tags_purp, tags_int, tags_rel, tags_vis, tags_flex, tags_emo]
campos_hum = ["Purpose", "Integrity and honesty", "Relevant experience", "Visionary leadership", "Flexibility", "Emotional intelligence"]

rec_hum = defaultdict(lambda: defaultdict(list))

for i, lista in enumerate(list_hum):
    campo = campos_hum[i]
    for entrada in lista:
        if ": " in entrada:
            nombre, valor = entrada.split(": ")
            try:
                rec_hum[nombre.strip()][campo].append(float(valor.strip()))
            except ValueError:
                continue

df_hum = {}
for nombre, campos in rec_hum.items():
    rows = []
    for campo, valores in campos.items():
        if valores:
            media = sum(valores) / len(valores)
            rows.append({"Campo": campo, "Media": media})
    df_hum[nombre] = pd.DataFrame(rows)
# Cálculo de la media general por campo
all_rows = []
for df in df_hum.values():
    all_rows.extend(df.to_dict(orient="records"))

df_all = pd.DataFrame(all_rows)
average_by_field = df2[individual_columns].mean().tolist()

sorted_founders = sorted(df_hum)

for i in range(0, len(sorted_founders), 2):
    cols = st.columns(2)
    
    for j in range(2):
        if i + j < len(sorted_founders):
            nombre = sorted_founders[i + j]
            data = df_hum[nombre]

            if not data.empty:
                # Ordenar para alinear con el promedio
                data = data.set_index("Campo").reindex(campos_hum).reset_index()

                fig = go.Figure()

                # Trace individual
                fig.add_trace(go.Scatterpolar(
                    r=data["Media"].tolist() + [data["Media"].iloc[0]],
                    theta=data["Campo"].tolist() + [data["Campo"].iloc[0]],
                    fill='toself',
                    name=nombre,
                    line=dict(color="rgb(52, 199, 89)"),
                    fillcolor='rgba(52, 199, 89, 0.3)'
                ))

                # Trace promedio
                fig.add_trace(go.Scatterpolar(
                    r=average_by_field + [average_by_field[0]],
                    theta=campos_hum + [campos_hum[0]],
                    fill='toself',
                    name="Average",
                    line=dict(color="orange"),
                    fillcolor='rgba(255,165,0,0.2)'
                ))

                # Layout
                fig.update_layout(
                    title=dict(
                        text=f"{nombre}",
                        x=0.5,
                        xanchor='center',
                        font=dict(size=18)
                    ),
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 4]
                        )
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    ),
                    height=500,
                    margin=dict(t=60, b=80)
                )

                with cols[j]:
                    st.plotly_chart(fig, use_container_width=True, key=f"fig_{i+j}")

col1, col2 = st.columns(2)

with col1:
    startup_ut_talks = normalize_list(row.get("Talks | Unconventional thinking (Founder & Score)", []))
    talks_ut_list = [p.strip() for entry in startup_ut_talks for p in entry.split(", ")]  # tenemos nuestra lista de founder: tag

    startup_ut_works = normalize_list(row.get("Workstations | Unconventional Thinking (Founder & Score)", []))
    works_ut_list = [p.strip() for entry in startup_ut_works for p in entry.split(", ")]

    startup_ut_ind = normalize_list(row.get("Individual Contest | Unconventional Thinking (Founder & Score)", []))
    ind_ut_list = [p.strip() for entry in startup_ut_ind for p in entry.split(", ")]

    list_ut = [talks_ut_list, works_ut_list, ind_ut_list]
    #Vamos a contar cuantas de cada hay por founder
    scores_count_ut = defaultdict(lambda: {"Bonus Star": 0, "Red Flag": 0})
    for l in list_ut:
        for tag in l:
            nombre, score = tag.split(": ")
            nombre = nombre.strip()
            score = score.strip()
            if "Bonus" in score:
                scores_count_ut[nombre]["Bonus Star"] += 1
            elif "Red" in score:
                scores_count_ut[nombre]["Red Flag"] += 1

    if scores_count_ut:
        st.subheader("🧠 Unconventional Thinking")
        for nombre in sorted(scores_count_ut):
            st.markdown(f"**{nombre}**")
            col_bonus, col_red = st.columns(2)
            col_bonus.metric("⭐ Bonus Star", int(scores_count_ut[nombre]["Bonus Star"]))
            col_red.metric("🚩 Red Flag",    int(scores_count_ut[nombre]["Red Flag"]))

    # --------Ambition y Confidence (de Individual Contest)----------------------------

    startup_conf = normalize_list(row.get("Individual Contest | Confidence (Founder & Score)", []))
    ind_conf_list = [p.strip() for entry in startup_conf for p in entry.split(", ")]

    startup_amb = normalize_list(row.get("Individual Contest | Ambition (Founder & Score)", []))
    ind_amb_list = [p.strip() for entry in startup_amb for p in entry.split(", ")]

    scores_count_conf = defaultdict(lambda: {"Bonus Star": 0, "Red Flag": 0})
    scores_count_amb = defaultdict(lambda: {"Bonus Star": 0, "Red Flag": 0})

    for tag in ind_conf_list:
        if ": " in tag:
            nombre, score = tag.split(": ")
            nombre = nombre.strip()
            score = score.strip()
            if "Bonus" in score:
                scores_count_conf[nombre]["Bonus Star"] += 1
            elif "Red" in score:
                scores_count_conf[nombre]["Red Flag"] += 1

    for tag in ind_amb_list:
        if ": " in tag:
            nombre, score = tag.split(": ")
            nombre = nombre.strip()
            score = score.strip()
            if "Bonus" in score:
                scores_count_amb[nombre]["Bonus Star"] += 1
            elif "Red" in score:
                scores_count_amb[nombre]["Red Flag"] += 1

    for title, score_dict in zip(["Confidence", "Ambition"], [scores_count_conf, scores_count_amb]):
        if score_dict:
            st.subheader(title)
            for nombre in sorted(score_dict):
                st.markdown(f"**{nombre}**")
                col_bonus, col_red = st.columns(2)
                col_bonus.metric("⭐ Bonus Star", int(score_dict[nombre]["Bonus Star"]))
                col_red.metric("🚩 Red Flag", int(score_dict[nombre]["Red Flag"]))

with col2:
    team_fields = [
    "Conflict resolution | Average",
    "Clear vision alignment | Average",
    "Clear roles | Average",
    "Complementary hard skills | Average",
    "Execution and speed | Average",
    "Team ambition | Average",
    "Confidence and mutual respect | Average",
    "Product and Customer Focus | Average",
    ]

    team_averages = df2[team_fields].mean().tolist()

    team_scores = {
    "Conflict resolution": row.get("Conflict resolution | Average"),
    "Clear vision alignment": row.get("Clear vision alignment | Average"),
    "Clear roles": row.get("Clear roles | Average"),
    "Complementary hard skills": row.get("Complementary hard skills | Average"),
    "Execution and speed": row.get("Execution and speed | Average"),
    "Team ambition": row.get("Team ambition | Average"),
    "Confidence and mutual respect": row.get("Confidence and mutual respect | Average"),
    "Product and customer focus": row.get("Product and Customer Focus | Average")
    }

    labels = list(team_scores.keys())
    values = list(team_scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name='Team',
        line=dict(color='royalblue'),
        fillcolor='rgba(65, 105, 225, 0.3)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=team_averages + [team_averages[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name='Average',
        line=dict(color='orange'),
        fillcolor='rgba(255,165,0,0.2)'
    ))

    fig.update_layout(
            title=dict(
                text=f"Human Team DD",
                x=0.5,
                xanchor='center',
                font=dict(size=18)
            ),
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 4]
                )
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            height=500,
            margin=dict(t=60, b=80)
        )
    
    st.plotly_chart(fig, use_container_width=True)