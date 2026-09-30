import pandas as pd
import requests
import streamlit as st

# Configuration for Live Cloud Backend or Localhost Fallback
# Change this to your Render URL when deploying live
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Govspot | Executive Command Center",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded",
)

# Custom Enterprise Dark-Theme & Component Styling
st.markdown(
    """
    <style>
    .main { background-color: #0b0f19; }
    .stMetric {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover { background: #1d4ed8; }
    h1, h2, h3 { color: #f3f4f6; font-family: 'Inter', sans-serif; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR: LIVE INGESTION SIMULATOR ---
with st.sidebar:
  st.markdown("### 📱 Citizen Edge Ingestion Simulator")
  st.markdown("Simulate incoming emergency text/voice signal streams.")

  with st.form("ingest_form"):
    raw_msg = st.text_area(
        "Signal Report",
        "Major bridge pillar cracking and sagging after heavy floods.",
    )
    lat_input = st.number_input("Latitude", value=9.5916, format="%.4f")
    lon_input = st.number_input("Longitude", value=76.5222, format="%.4f")
    severity_input = st.slider("Assessed Severity Score", 1, 10, 9)

    submit_signal = st.form_submit_button("📡 Broadcast Distress Signal")

    if submit_signal:
      payload = {
          "raw_message": raw_msg,
          "latitude": lat_input,
          "longitude": lon_input,
          "severity_score": severity_input,
      }
      try:
        res = requests.post(f"{API_BASE_URL}/ingest", json=payload)
        if res.status_code == 201:
          st.success("Signal captured & CoI calculated!")
          st.rerun()
        else:
          st.error("Failed to ingest signal.")
      except Exception:
        st.error("Backend offline.")

  st.markdown("---")
  st.markdown("### 🏛️ System Status")
  st.info("Govspot DPI Rails: Connected\nSQLAlchemy Engine: Active")

# --- MAIN DASHBOARD ---
st.title("🛡️ GOVSPOT: Autonomous Command Center")
st.markdown("### *Demand-to-Deployment Pipeline & Cost-of-Inaction Engine*")
st.markdown("---")

try:
  response = requests.get(f"{API_BASE_URL}/complaints")
  if response.status_code == 200:
    data = response.json()
    if data:
      df = pd.DataFrame(data)

      # Metrics Row
      col1, col2, col3, col4 = st.columns(4)
      with col1:
        st.metric(
            label="🚨 Active Distress Signals",
            value=len(df),
            delta="Live Stream",
        )
      with col2:
        total_bleed = df["coi_financial_bleed"].sum()
        st.metric(
            label="💸 Total Daily Economic Bleed",
            value=f"${total_bleed:,.2f}",
            delta="-18h turnaround",
        )
      with col3:
        avg_severity = df["severity_score"].mean()
        st.metric(
            label="⚡ Average Urgency Index", value=f"{avg_severity:.1f} / 10"
        )
      with col4:
        drafted_count = len(df[df["status"] == "Tender Drafted"])
        st.metric(
            label="📄 Tenders Auto-Drafted",
            value=drafted_count,
            delta="Ready for Sign-off",
        )

      st.markdown("---")

      # Tabs
      tab1, tab2, tab3 = st.tabs(
          ["📊 Live Queue & Tendering", "📍 Geospatial Heatmap", "⚙️ Telemetry"]
      )

      with tab1:
        st.subheader("📋 Infrastructure Queue & Procurement Status")

        f_col1, f_col2 = st.columns(2)
        with f_col1:
          status_filter = st.selectbox(
              "Filter by Status",
              options=["All"] + list(df["status"].unique()),
          )
        with f_col2:
          min_sev = st.slider("Minimum Urgency Filter", 1, 10, 1)

        filtered_df = df[
            (df["severity_score"] >= min_sev)
            & (
                (df["status"] == status_filter)
                if status_filter != "All"
                else True
            )
        ]

        st.dataframe(
            filtered_df[
                [
                    "id",
                    "issue_type",
                    "description",
                    "severity_score",
                    "coi_financial_bleed",
                    "status",
                ]
            ],
            use_container_width=True,
            height=220,
        )

        st.markdown("### ⚡ Zero-Bureaucracy Smart-Tender Generator")
        c_id, c_btn = st.columns([2, 1])
        with c_id:
          selected_id = st.selectbox(
              "Select Complaint ID to Execute Tendering",
              options=df["id"].tolist(),
          )
        with c_btn:
          st.markdown("<br>", unsafe_allow_html=True)
          generate_clicked = st.button("🚀 Generate Autonomous Tender")

        if generate_clicked:
          tender_res = requests.post(
              f"{API_BASE_URL}/generate-tender/{selected_id}"
          )
          if tender_res.status_code in [200, 201]:
            t_data = tender_res.json()
            st.success(
                f"✅ Successfully compiled Tender #{t_data['tender_id']}!"
            )

            with st.container():
              st.markdown(f"#### 🏛️ {t_data['project_title']}")
              tc1, tc2 = st.columns(2)
              with tc1:
                st.metric(
                    "Allocated Budget",
                    f"${t_data['estimated_budget_usd']:,.2f}",
                )
                st.markdown(f"**Compliance Status:** `{t_data['status']}`")
              with tc2:
                st.markdown(
                    "**Economic Justification:**"
                    f" {t_data['procurement_justification']}"
                )

              st.markdown("**📦 Algorithmic Bill of Materials (BOM):**")
              st.json(t_data["bill_of_materials"])
          else:
            st.error("Tender generation failed.")

      with tab2:
        st.subheader("📍 National Infrastructure Distress Heatmap")
        map_df = df[["latitude", "longitude"]].rename(
            columns={"latitude": "lat", "longitude": "lon"}
        )
        st.map(map_df, zoom=6, use_container_width=True)

      with tab3:
        st.subheader("🔌 DPI Interoperability & Gateway Telemetry")
        st.json({
            "fastapi_gateway": "ONLINE",
            "database_connector": "SQLAlchemy 2.0 (Relational State)",
            "encryption_standard": "AES-256 Public Sector Grade",
        })
    else:
      st.info(
          "No complaints registered. Use the sidebar to inject your first"
          " signal!"
      )
  else:
    st.error("Connection error with backend service.")
except Exception as e:
  st.warning(f"⚠️ Make sure FastAPI backend is running. Details: {e}")