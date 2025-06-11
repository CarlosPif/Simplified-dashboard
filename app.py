import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict

# === Simulated data fetch from Airtable (replace with real logic as needed) ===
st.set_page_config(layout="wide")
st.title("📊 Decelera Startup Snapshot - Horizontal Dashboard")

# Placeholder data (you would load this from your Airtable-derived df and row)
st.markdown("### Example: Skor")

# Simulated Scores
human_scores = [3.8, 3.2, 3.5, 3.7, 3.0, 3.6, 3.4]
human_labels = ["Purpose", "Openness", "Integrity", "Experience", "Leadership", "Flexibility", "EQ"]

team_scores = [3.5, 3.2, 3.6, 3.3, 3.7, 3.4, 3.1, 3.5]
teams_labels = ["Conflict", "Vision", "Roles", "Hard Skills", "Execution", "Ambition", "Respect", "Focus"]

science_scores = [3.6, 3.8, 2.1, 1.9]
science_labels = ["Resilience", "Grit", "Exhaustion", "Disengagement"]

# === Helper to create radar chart ===
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

# === Layout horizontal ===
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(radar_chart(human_scores, human_labels, "Human DD"), use_container_width=True)

with col2:
    st.plotly_chart(radar_chart(team_scores, teams_labels, "Team DD"), use_container_width=True)

with col3:
    st.plotly_chart(radar_chart(science_scores, science_labels, "Scientific DD"), use_container_width=True)

# === Summary bullets ===
st.markdown("---")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Business Highlights")
    st.markdown("""
    - ✅ **Scalable SaaS** with strong demand.
    - 🧠 **Needs clarity** on SaaS go-to-market plan.
    - 🔁 **Leadership change** in progress.
    - 🌍 Expansion interest in **Latin America & Europe**.
    - ⚠️ **Transition risk** from remote to in-person leadership.
    """)

with col_right:
    st.subheader("Summary Flags")
    st.markdown("""
    - 🟢 3 Green Flags
    - 🟡 2 Yellow Flags
    - 🔴 1 Red Flag
    """)

# === Optional: For PDF Landscape Print ===
st.markdown("""
    <style>
        @media print {
            @page {
                size: landscape;
                margin: 10mm;
            }
            body {
                -webkit-print-color-adjust: exact;
            }
        }
    </style>
""", unsafe_allow_html=True)

# === PDF Export Button (Optional) ===
st.markdown("""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <button id="savepdf">⬇️ Descargar en PDF (Apaisado)</button>
    <script>
    const {{ jsPDF }} = window.jspdf;
    document.getElementById("savepdf").addEventListener("click", function () {{
        html2canvas(document.body, {{ scale: 2 }}).then(canvas => {{
            const pdf = new jsPDF('l', 'mm', 'a4');
            const imgData = canvas.toDataURL('image/png');
            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();
            const imgHeight = canvas.height * pageWidth / canvas.width;

            let heightLeft = imgHeight;
            let position = 0;

            pdf.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight);
            heightLeft -= pageHeight;

            while (heightLeft > 0) {{
                position -= pageHeight;
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight);
                heightLeft -= pageHeight;
            }}

            pdf.save("startup-overview.pdf");
        }});
    }});
    </script>
""", unsafe_allow_html=True)
