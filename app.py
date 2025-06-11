import streamlit as st
import pandas as pd
from pyairtable import Api
from collections import defaultdict
import re

st.markdown(
    """
    <style>
    .main {
        max-width: 794px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

AIRTABLE_PAT = st.secrets["airtable"]["api_key"]
BASE_ID = st.secrets["airtable"]["base_id"]
TABLE_ID = st.secrets["airtable"]["table_id"]

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

def normalize_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return [] if value is None or (isinstance(value, float) and pd.isna(value)) else [str(value)]

id_to_name = {"2": "Heuristik", "3": "Metly", "6": "Skor", "7": "Robopedics", "9": "Quix", "10": "Calliope", "12": "Nidus Lab", "13": "Vivra", "14": "Lowerton", "15": "Chemometric Brain", "16": "Stamp", "17": "SheerMe", "18": "Zell", "19": "Anyformat", "21": "Valerdat", "22": "Kestrix Ltd.", "26": "Gaddex", "27": "Sheldonn", "28": "Vixiees", "29": "IKI Health Group sL", "30": "ByteHide"}

df["Startup Label"] = df["Id"].apply(lambda x: id_to_name.get(x, f"ID {x}"))
valid_ids = [id_ for id_ in df["Id"].unique() if id_ in id_to_name]
selected_id = st.selectbox("Choose a Startup", options=sorted(valid_ids, key=int), format_func=lambda x: id_to_name.get(x, f"Startup {x}"))

filtered = df[df["Id"] == selected_id]
if filtered.empty:
    st.warning("❌ No data for the selected startup.")
    st.stop()

row = filtered.iloc[0]
st.markdown(f"#### 📊 Feedback for {id_to_name.get(selected_id, selected_id)}")

def compact_row(title, metrics):
    st.markdown(f"##### <u>{title}<u>", unsafe_allow_html=True)
    items = list(metrics.items())
    pairs = [items[i:i+2] for i in range(0, len(items), 2)]
    cols = st.columns(len(pairs))
    for col, pair in zip(cols, pairs):
        for label, val in pair:
            col.markdown(f"**{label}:** {val}")

compact_row("💸 Investability", {
    "✅ Yes Votes": int(row.get("Investable_Yes_Count", 0)),
    "❌ No Votes": int(row.get("Investable_No_Count", 0)),
    "🟢 Yes Ratio": f"{(row.get('Investable_Yes_Count', 0) / max(row.get('Investable_Yes_Count', 0) + row.get('Investable_No_Count', 0), 1) * 100):.1f}%"
})

compact_row("Risk", {
    "State": round(row.get("Average RISK | State of development_Score", 0), 2),
    "Momentum": round(row.get("Average RISK | Momentum_Score", 0), 2),
    "Management": round(row.get("Average RISK | Management_Score", 0), 2),
})

compact_row("Reward", {
    "Market": round(row.get("Average Reward | Market_Score", 0), 2),
    "Team": round(row.get("Average Reward | Team_Score", 0), 2),
    "Pain": round(row.get("Average Reward | Pain_Score", 0), 2),
    "Scalability": round(row.get("Average Reward | Scalability_Score", 0), 2),
})

individual_columns = [
    "Purpose | Average",
    "Openness | Average",
    "Integrity and honesty | Average",
    "Relevant experience | Average",
    "Visionary leadership | Average",
    "Flexibility | Average",
    "Emotional intelligence | Average"
]

individual_metrics = {
    col.split(" | ")[0]: round(row.get(col, 0), 2) for col in individual_columns
}

compact_row("🧠 Individual Metrics", individual_metrics)

team_columns = [
    "Conflict resolution | Average",
    "Clear vision alignment | Average",
    "Clear roles | Average",
    "Complementary hard skills | Average",
    "Execution and speed | Average",
    "Team ambition | Average",
    "Confidence and mutual respect | Average",
    "Product and Customer Focus | Average"
]

team_metrics = {
    col.split(" | ")[0]: round(row.get(col, 0), 2) for col in team_columns
}

compact_row("👥 Team Metrics", team_metrics)

brs_calc = row.get("BRS_Calculation", ["No result"])
gr_calc = row.get("GRIT_Calculation", ["No result"])
olbi_ex = row.get("OLBI_Exhaustion_Descriptor", ["No result"])
olbi_dis = row.get("OLBI_Disengagement_Descriptor", ["No result"])

brs_calc = brs_calc[0] if isinstance(brs_calc, list) else brs_calc
gr_calc = gr_calc[0] if isinstance(gr_calc, list) else gr_calc
olbi_ex = olbi_ex[0] if isinstance(olbi_ex, list) else olbi_ex
olbi_dis = olbi_dis[0] if isinstance(olbi_dis, list) else olbi_dis

def flag_color(text):
    if isinstance(text, str):
        text = text.lower()
        if "high" in text:
            return "🔴"
        elif "moderate" in text:
            return "🟡"
        elif "low" in text:
            return "🟢"
    return "⚪️"

compact_row("🧪 Scientific Results", {
    "BRS": str(brs_calc),
    "GRIT": str(gr_calc),
    "Exhaustion": f"{flag_color(olbi_ex)} {olbi_ex}",
    "Disengagement": f"{flag_color(olbi_dis)} {olbi_dis}"
})

st.markdown("##### 🚩 EM's Feedback")

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
        st.markdown(f"###### 👤**{mentor}**")
        scores = extract_mentor_scores(row).get(mentor, {})

        for color in ["red", "yellow", "green"]:
            comments = grouped[mentor].get(color, [])
            if not comments:
                continue

            emoji = color_to_emoji.get(color, "⚪️")
            st.markdown(f"<span style='color: {'red' if color == 'red' else 'yellow' if color == 'yellow' else 'green'};'> {color.capitalize()} Flags:</span>", unsafe_allow_html=True)

            # Agrupar y mostrar todo como lista
            all_formatted = []
            for comment in comments:
                formatted = _format_categories(comment, scores=scores)
                all_formatted.append(formatted)

            st.markdown(", ".join(all_formatted))

render_flags_by_mentor(row)

st.markdown("""
<style>
.download-btn {
    background-color: #0b6abf;
    color: white;
    padding: 0.6rem 1.2rem;
    font-size: 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-top: 1rem;
}
.download-btn:hover {
    background-color: #095a9c;
}
</style>

<button class="download-btn" id="savepdf">⬇️ Descargar esta página en PDF</button>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script>
const {{ jsPDF }} = window.jspdf;

window.addEventListener("load", () => {
  const btn = document.getElementById("savepdf");
  if (btn) {
    btn.addEventListener("click", function () {
      html2canvas(document.body, { scale: 2, useCORS: true }).then(canvas => {
        const imgData = canvas.toDataURL("image/png");
        const pdf = new jsPDF("p", "mm", "a4");
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const imgHeight = canvas.height * pageWidth / canvas.width;

        let heightLeft = imgHeight;
        let position = 0;

        pdf.addImage(imgData, "PNG", 0, position, pageWidth, imgHeight);
        heightLeft -= pageHeight;

        while (heightLeft > 0) {
          position -= pageHeight;
          pdf.addPage();
          pdf.addImage(imgData, "PNG", 0, position, pageWidth, imgHeight);
          heightLeft -= pageHeight;
        }

        pdf.save("feedback-decelera.pdf");
      });
    });
  }
});
</script>
""", unsafe_allow_html=True)