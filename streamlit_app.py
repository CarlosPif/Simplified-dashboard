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
first_col1, first_col2, first_col3 = st.columns(3)

with first_col1:
    risk_reward_scores = {
        "Sate of development": row.get("Average RISK | State of development_Score",0),
        "Momentum": row.get("Average RISK | Momentum_Score", 0),
        "Management": row.get("Average RISK | Management_Score", 0),
        "Market": row.get("Average Reward | Market_Score", 0),
        "Team": row.get("Average Reward | Team_Score", 0),
        "Pain": row.get("Average Reward | Pain_Score", 0),
        "Scalability": row.get("Average Reward | Scalability_Score", 0)
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

with first_col2:
    team_scores = {
        "Conflict resolution": row.get("Conflict resolution | Average"),
        "Clear vision alignment": row.get("Clear vision alignment | Average"),
        "Clear roles": row.get("Clear roles | Average"),
        "Complementary hard skills": row.get("Complementary hard skills | Average"),
        "Execution and speed": row.get("Execution and speed | Average"),
        "Team ambition": row.get("Team ambition | Average"),
        "Confidence and mutual respect": row.get("Confidence and mutual respect | Average"),
        "Product and customer focus": row.get("Product and customer focus | Average")
    }

    team_df = pd.DataFrame.from_dict(team_scores, orient="index", columns=["Score"]).reset_index()
    team_df.columns = ["Category", "Score"]

    st.plotly_chart(
    radar_chart(
        team_df["Score"].tolist(),
        team_df["Category"].tolist(),
        "Human Due Diligence (Team)"
    )
)

with first_col3:
    JUDGE_NAMES = [
    "Jorge Gonzalez-Iglesias", "Juan de Antonio", "Adam Beguelin",
    "Alejandro Lopez", "Alex Barrera", "Álvaro Dexeus", "Anastasia Dedyukhina",
    "Andrea Klimowitz", "Anna  Fedulow", "Bastien  Pierre Jean Gambini",
    "Beth Susanne", "David Beratech", "Elise Mitchell", "Esteban Urrea",
    "Fernando Cabello", "Gennaro Bifulco", "Ivan Alaiz", "Ivan Nabalon",
    "Ivan Peña", "Jair Halevi", "Jason Eckenroth", "Javier Darriba",
    "Juan Pablo Tejela", "Laura Montells", "Manel Adell", "Oscar Macia",
    "Paul Ford", "Pedro Claveria", "Philippe Gelis", "Ranny Nachmais",
    "Rebeca De Sancho", "Rui Fernandes", "Sean Cook", "Shadi  Yazdan",
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
def render_flags_by_mentor(row):

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

    for mentor in sorted(grouped):
        st.markdown(f"### 👤 **{mentor}**")
        scores = extract_mentor_scores(row).get(mentor, {})

        for color in ["red", "yellow", "green"]:
            comments = grouped[mentor].get(color, [])
            if not comments:
                continue

            emoji = color_to_emoji.get(color, "⚪️")
            st.markdown(f"{emoji} **{color.capitalize()} Flag**")

            # Agrupar y mostrar todo como lista
            all_formatted = []
            for comment in comments:
                formatted = _format_categories(comment, scores=scores)
                all_formatted.append(formatted)

            st.markdown(", ".join(all_formatted))

render_flags_by_mentor(row)