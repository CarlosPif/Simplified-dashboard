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
    layout="centered"

)

st.markdown("""
<style>
@media print {
    div[data-baseweb="select"] {
        display: none !important;
    }
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* Reduce al mínimo el padding horizontal entre columnas */
[data-testid="column"] {
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
    margin: 0 !important;
}

/* Alinea contenido de las columnas al top */
[data-testid="column"] > div {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

/* Ajusta zoom y márgenes para impresión A4 */
@media print {
    html, body {
        width: 210mm;
        height: 297mm;
        margin: 0;
        zoom: 90%;  /* ajusta si hace falta más espacio */
    }

    .element-container {
        break-inside: avoid;
        page-break-inside: avoid;
    }

    @page {
        size: A4 portrait;
        margin: 10mm 10mm 10mm 10mm;
    }
}
</style>
""", unsafe_allow_html=True)

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
st.markdown("<h1 style='text-align: center;'>Bussiness DD</h1>", unsafe_allow_html=True)


col1, col2 = st.columns([1, 1])

with col2:
    averages_rr = {
        "State of development": df["Average RISK | State of development_Score"].mean(),
        "Momentum": df["Average RISK | Momentum_Score"].mean(),
        "Management": df["Average RISK | Management_Score"].mean(),
        "Market": df["Average Reward | Market_Score"].mean(),
        "Team": df["Average Reward | Team_Score"].mean(),
        "Pain": df["Average Reward | Pain_Score"].mean(),
        "Scalability": df["Average Reward | Scalability_Score"].mean()
    }
    averages_rr_df = pd.DataFrame.from_dict(averages_rr, orient="index", columns=["Score"]).reset_index()
    averages_rr_df.columns = ["Category", "Score"]

    risk_reward_scores = {
        "State of development": row.get("Average RISK | State of development_Score",0),
        "Momentum": row.get("Average RISK | Momentum_Score", 0),
        "Management": row.get("Average RISK | Management_Score", 0),
        "Market": row.get("Average Reward | Market_Score", 0),
        "Team": row.get("Average Reward | Team_Score", 0),
        "Pain": row.get("Average Reward | Pain_Score", 0),
        "Scalability": row.get("Average Reward | Scalability_Score", 0)
    }
    risk_reward_df = pd.DataFrame.from_dict(risk_reward_scores, orient="index", columns=["Score"]).reset_index()
    risk_reward_df.columns = ["Category", "Score"]

    # Normaliza las categorías
    risk_reward_df["Category"] = risk_reward_df["Category"].str.strip().str.lower()
    averages_rr_df["Category"] = averages_rr_df["Category"].str.strip().str.lower()

    # Elimina duplicados si los hubiera (conserva el primero)
    risk_reward_df = risk_reward_df.drop_duplicates(subset="Category")
    averages_rr_df = averages_rr_df.drop_duplicates(subset="Category")

    # Reordena el promedio para que siga el orden de risk_reward_df
    averages_rr_df = averages_rr_df.set_index("Category").reindex(risk_reward_df["Category"]).reset_index()

    # Verifica que no haya valores NaN en scores (esto puede romper el gráfico)
    if risk_reward_df["Score"].isnull().any() or averages_rr_df["Score"].isnull().any():
        raise ValueError("Hay valores NaN en las columnas de Score. Revisa tus datos.")

    # Construye el gráfico
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=risk_reward_df["Score"].tolist() + [risk_reward_df["Score"].iloc[0]],
        theta=risk_reward_df["Category"].tolist() + [risk_reward_df["Category"].iloc[0]],
        fill='toself',
        name="Risk & Reward",
        line=dict(color='skyblue'),
        fillcolor="rgba(135, 206, 235, 0.3)"
    ))
    fig.add_trace(go.Scatterpolar(
        r=averages_rr_df["Score"].tolist() + [averages_rr_df["Score"].iloc[0]],
        theta=averages_rr_df["Category"].tolist() + [averages_rr_df["Category"].iloc[0]],
        name="Average",
        line=dict(color='orange'),
    ))

    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                tickfont=dict(size=11),
                rotation=90,
                direction="clockwise"
            ),
            radialaxis=dict(
                visible=True,
                range=[0, 4],
                tickfont=dict(size=10)
            )
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=450,
        title=dict(
            text="Risk & Reward Scores",
            x=0.5,              # Centra horizontalmente
            xanchor="center",   # Alinea con el centro
            font=dict(size=18, family="Arial", color="black")
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        )
    )
    st.plotly_chart(fig)

with col1:
    JUDGE_NAMES = [
    "Jorge Gonzalez-Iglesias", "Juan de Antonio", "Adam Beguelin",
    "Alejandro Lopez", "Alex Barrera", "Álvaro Dexeus", "Anastasia Dedyukhina",
    "Andrea Klimowitz", "Anna  Fedulow", "Bastien  Pierre Jean Gambini",
    "Beth Susanne", "David Baratech", "Elise Mitchell", "Esteban Urrea",
    "Fernando Cabello", "Gennaro Bifulco", "Ivan Alaiz", "Ivan Nabalon",
    "Ivan Peña", "Jair Halevi", "Juan Pablo y Laura", "Jason Eckenroth", "Javier Darriba",
    "Juan Pablo Tejela", "Laura Montells", "Manel Adell", "Oscar Macia",
    "Paul Ford", "Pedro Claveria", "Philippe Gelis", "Ranny Nachmais",
    "Rebeca De Sancho", "Rui Fernandes", "Sean Cook", "Shadi Yazdan",
    "Shari Swan", "Stacey  Ford", "Sven  Huber", "Torsten Kolind", "Jaime", "John Varuguese", "Elise Mitchel"
    ]

    # --- 2. Simple HTML cleaner (unchanged) ------------------------------------
    _HTML_BREAK_RE = re.compile(r"<br\s*/?>", flags=re.I)

    def _clean_html(raw: str) -> str:
        if not isinstance(raw, str):
            return raw or ""
        txt = _HTML_BREAK_RE.sub("\n", raw)
        txt = txt.replace("**", "")
        return txt.strip()

    # --- 3. Updated NAME regex --------------------------------------------------
    # It matches a judge name followed by EITHER:
    #   • end-of-string
    #   • whitespace
    #   • a capital letter (for “State”, “Momentum”…), a colon, or a newline
    CATS = [
        "State of development", "Momentum", "Management",
        "Market", "Team", "Pain", "Scalability",
    ]

    # === Expresión regular para categorías (con ":")
    _CAT_RE = re.compile(r"(" + "|".join(map(re.escape, CATS)) + r")\s*:", flags=re.I)

    # === Expresión regular para nombres de mentor
    _NAME_RE = re.compile(
        r"(" + "|".join(re.escape(n) for n in JUDGE_NAMES) + r")(?=$|\s|[A-Z])",
        flags=re.I
    )

    def extract_mentor_scores(row) -> dict[str, dict[str, float]]:
        mentor_scores = defaultdict(dict)

        for cat in CATS:
            field_name = f"{cat} | Mentor Scores"
            raw = row.get(field_name)
            if not raw:
                continue
            entries = normalize_list(raw)
            for entry in entries:
                parts = [p.strip() for p in entry.split(",")]
                for p in parts:
                    if ": " in p:
                        name, score = p.split(": ")
                        try:
                            mentor_scores[name.strip()][cat.lower()] = float(score.strip())
                        except ValueError:
                            continue
        return mentor_scores

    # === Formatea texto con puntuaciones del mentor
    def _format_categories(text: str, scores: dict[str, float] | None = None) -> str:
        text = _clean_html(text)
        matches = list(_CAT_RE.finditer(text))
        if not matches:
            return text.strip()

        out = []

        if matches[0].start() > 0:
            out.append(text[:matches[0].start()].strip())

        for idx, match in enumerate(matches):
            label = match.group(1).strip()
            key = label.lower()
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            body = text[start:end].strip()

            score = scores.get(key) if scores else None
            score_text = f" ({score:.2f})" if score is not None and pd.notna(score) else ""
            out.append(f"**{label}{score_text}:** {body}")

        return ", ".join(out)

    # === Extrae (mentor, comentario sin procesar) desde string largo
    def _group_by_mentor(raw: str) -> list[tuple[str, str]]:
        text = _clean_html(raw)
        hits = list(_NAME_RE.finditer(text))

        if not hits:
            yield "Anonymous", text.strip()
            return

        for idx, hit in enumerate(hits):
            mentor = hit.group(1).strip()
            start = hit.end()
            end = hits[idx + 1].start() if idx + 1 < len(hits) else len(text)
            comment = text[start:end].lstrip(' :–').strip()
            if comment:
                yield mentor, comment

    # === Junta todas las banderas (green/yellow/red) para cada mentor
    def collect_flag_records(row):
        flag_fields = [
            ("RISK | Green_exp",   "green"),
            ("RISK | Yellow_exp",  "yellow"),
            ("RISK | Red_exp",     "red"),
            ("Reward | Green_exp", "green"),
            ("Reward | Yellow_exp","yellow"),
            ("Reward | Red_exp",   "red"),
        ]

        records = []
        for field, color in flag_fields:
            for raw in normalize_list(row.get(field, [])):
                for mentor, raw_comment in _group_by_mentor(raw):
                    records.append((mentor, color, raw_comment))
        return records

    # === Pinta cada mentor y su lista de flags con puntuaciones
    st.markdown("#### 🚩 EM's Feedback")

    def render_flags_by_mentor(row, start, limit):

        mentor_scores = extract_mentor_scores(row)
        records = collect_flag_records(row)

        if not records:
            st.markdown("_No hay feedback para este startup._")
            return

        # Agrupar por mentor y color
        grouped = defaultdict(lambda: defaultdict(list))  # mentor → color → [raw_text]

        for mentor, color, raw_comment in records:
            grouped[mentor][color].append(raw_comment)

        color_to_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}

        j = 0
        for mentor in sorted(grouped)[start:]:
            st.markdown(f"###### 👤 **{mentor}**")
            scores = extract_mentor_scores(row).get(mentor, {})

            for color in ["red", "yellow", "green"]:
                comments = grouped[mentor].get(color, [])
                if not comments:
                    continue

                emoji = color_to_emoji.get(color, "⚪️")

                # Agrupar y mostrar todo como lista
                all_formatted = []
                for comment in comments:
                    formatted = _format_categories(comment, scores=scores)
                    all_formatted.append(formatted)

                st.markdown(f"{emoji}" + ", ".join(all_formatted))

            j += 1
            if j == limit:
                break

    render_flags_by_mentor(row, 0, 1)

render_flags_by_mentor(row, 1, limit=None)