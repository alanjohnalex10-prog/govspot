import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

# Live Cloud Backend Configuration
API_BASE_URL = "https://govspot-backend.onrender.com"

st.set_page_config(
    page_title="Govspot | Public Reporting Portal",
    layout="centered",
    page_icon="📢",
)

st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        background: #0ea5e9;
        color: white;
        border: none;
        padding: 0.75rem 1rem;
    }
    .stButton>button:hover { background: #0284c7; }
    h1, h2, h3 { color: #1e293b; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📢 Public Infrastructure Reporting Portal")
st.markdown("### *Govspot Citizen Engagement Node*")
st.markdown(
    "Report road damage, bridge failures, water leaks, or power outages"
    " instantly. **Click the exact location on the map below** to pin the"
    " incident."
)
st.markdown("---")

with st.form("citizen_report_form"):
  st.subheader("📝 Describe the Issue")
  raw_message = st.text_area(
      "What is happening?",
      placeholder=(
          "e.g., Major bridge pillar cracking and sagging heavily after last"
          " night's flood near the south market."
      ),
  )

  st.subheader("📍 Pin Location on Map")
  st.markdown(
      "Click anywhere on the map to set the precise incident coordinates."
  )

  m = folium.Map(location=[9.5916, 76.5222], zoom_start=11)
  m.add_child(folium.LatLngPopup())
  map_data = st_folium(m, height=300, width="100%")

  lat = 9.5916
  lng = 76.5222
  if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lng = map_data["last_clicked"]["lng"]
    st.success(f"📍 Selected Pin Coordinates: Lat {lat:.4f}, Lng {lng:.4f}")
  else:
    st.info(
        "💡 Tip: Click on the map above to select the exact failure site."
    )

  severity_score = st.slider(
      "How urgent or severe is this problem?",
      min_value=1,
      max_value=10,
      value=7,
      help="1 = Minor maintenance, 10 = Emergency danger to life/property",
  )

  submitted = st.form_submit_button(
      "🚀 Submit Distress Signal to Government DPI"
  )

  if submitted:
    if not raw_message.strip():
      st.error("Please enter a description of the issue.")
    else:
      payload = {
          "raw_message": raw_message,
          "latitude": lat,
          "longitude": lng,
          "severity_score": severity_score,
      }
      try:
        response = requests.post(f"{API_BASE_URL}/ingest", json=payload)
        if response.status_code == 201:
          res_data = response.json()
          st.success(
              "✅ Report successfully submitted! Assigned Tracking ID:"
              f" **#{res_data['message_id']}**"
          )
          st.info(
              f"🔍 **AI Extraction Result:** `{res_data['extracted_category']}`\n\n"
              f"💸 **Calculated Cost-of-Inaction Bleed:**"
              f" `${res_data['daily_cost_of_inaction_usd']:,.2f}/day`\n\n"
              "Your report has been securely registered in the national asset"
              " pipeline."
          )
        else:
          st.error("Failed to connect to backend service.")
      except Exception:
        st.error("⚠️ Backend connection error. Please try again.")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 14px;'>Powered"
    " by Govspot Interoperable Digital Public Infrastructure Rails</p>",
    unsafe_allow_html=True,
)