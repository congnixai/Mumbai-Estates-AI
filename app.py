import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import io

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Mumbai Real Estate AI | Congnix AI", page_icon="🏙️", layout="wide"
)

# --- CUSTOM CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 800;
        color: #B91C1C; /* Mumbai Red Accent */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    div[data-testid="column"] {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        color: #6B7280;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- UTILITY FUNCTIONS ---
def format_mumbai_currency(cr_value):
    """Formats Crores into a readable Indian system string"""
    if cr_value >= 1:
        return f"₹{cr_value:.2f} Cr"
    else:
        lakhs = cr_value * 100
        return f"₹{lakhs:.2f} Lakhs"


def generate_mumbai_insight(loc, mun, p_type, bhk, area, floor, age):
    """Mumbai-Specific Dynamic Insight Engine"""
    insights = []

    # 1. Space Efficiency (Mumbai standards are tighter)
    if area / bhk > 600:
        insights.append(
            f"Spacious for Mumbai standards; usually commands a premium in {loc}."
        )
    else:
        insights.append(
            f"Typical Mumbai compact layout; optimized for high rental demand."
        )

    # 2. Vertical Premium
    if floor > 30:
        insights.append(
            "Skyscraper advantage: High floor placement ensures better air quality and 'Skyline' views."
        )
    elif floor > 10:
        insights.append(
            "Mid-level floor: Balanced accessibility and reduced street noise."
        )

    # 3. Location & Governance
    if mun == "BMC":
        insights.append(
            f"Premium BMC jurisdiction ensures superior infrastructure and high resale liquidity."
        )
    else:
        insights.append(
            f"Located in a satellite hub ({mun}); offers better ROI potential through upcoming connectivity."
        )

    # 4. Property Age
    if age < 5:
        insights.append(
            "Modern construction with latest RERA compliance and safety standards."
        )

    return " ".join(insights[:3])


def generate_pdf(data_summary, price_str, price_cr, insight):
    pdf = FPDF()
    pdf.add_page()

    # Branding
    pdf.set_fill_color(185, 28, 28)  # Mumbai Red
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "VALUATION CERTIFICATE", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        5,
        f"Mumbai Real Estate Intelligence Terminal | {datetime.now().strftime('%d %b %Y')}",
        ln=True,
        align="C",
    )

    # Price Section
    pdf.ln(20)
    pdf.set_text_color(185, 28, 28)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "ESTIMATED MARKET VALUATION", ln=True, align="L")
    pdf.set_fill_color(240, 244, 248)
    pdf.set_font("Arial", "B", 28)
    pdf.cell(0, 25, f"{price_str.replace('₹', 'Rs. ')}", ln=True, align="C", fill=True)
    pdf.ln(10)

    # Grid
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "PROPERTY CONFIGURATION", ln=1)
    pdf.set_font("Arial", "", 10)
    col_width = 95
    for key, value in data_summary.items():
        pdf.set_font("Arial", "B", 10)
        pdf.cell(col_width, 10, f" {key.upper()}", border="B")
        pdf.set_font("Arial", "", 10)
        pdf.cell(col_width, 10, f" {str(value).replace('₹', 'Rs. ')}", border="B", ln=1)

    # Insights
    pdf.ln(15)
    pdf.set_fill_color(232, 245, 233)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " AI MARKET INSIGHTS", ln=True, fill=True)
    pdf.set_font("Arial", "I", 11)
    pdf.multi_cell(0, 10, insight.encode("latin-1", "ignore").decode("latin-1"))

    # Footer
    pdf.set_y(-40)
    pdf.set_draw_color(185, 28, 28)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, "Congnix AI", ln=True, align="R")
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "Principal Developer & Data Architect", ln=True, align="R")

    return pdf.output(dest="S").encode("latin-1", "ignore")


@st.cache_resource
def load_assets():
    # Ensure you have exported the model as 'mumbai_price_predictor.pkl'
    model = joblib.load("mumbai_price_predictor.pkl")
    return model


# --- LOGIC ---
model = load_assets()

# --- HEADER ---
st.title("🏙️ Mumbai Metropolitan AI Estimator")
st.markdown(
    "**Real-Time Valuation Engine** | Covering BMC, NMMC, TMC, and KDMC jurisdictions."
)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Property Parameters")

    # Updated Mumbai Locations
    localities = {
        "Malabar Hill": "BMC",
        "Worli": "BMC",
        "Bandra West": "BMC",
        "Andheri West": "BMC",
        "Borivali West": "BMC",
        "Vashi": "NMMC",
        "Kharghar": "NMMC",
        "Thane West": "TMC",
        "Kalyan": "KDMC",
        "Mira Road": "MBMC",
    }

    locality = st.selectbox("Locality", list(localities.keys()))
    municipality = localities[locality]

    st.info(f"Jurisdiction: {municipality}")

    prop_type = st.segmented_control(
        "Segment", ["Standard", "Luxury"], default="Standard"
    )
    bhk = st.slider("BHK", 1, 5, 2)
    carpet_area = st.number_input("Carpet Area (Sq.Ft)", 300, 5000, 750)
    floor = st.slider("Floor Number", 1, 60, 12)
    parking = st.radio("Parking Spaces", [1, 2, 3], horizontal=True)
    age = st.number_input("Building Age (Years)", 0, 30, 2)

    predict_btn = st.button("Generate Mumbai Valuation")

# --- DATA PREPARATION ---
input_df = pd.DataFrame(
    {
        "Locality": [locality],
        "Municipality": [municipality],
        "Property_Type": [prop_type],
        "BHK": [bhk],
        "Carpet_Area_SqFt": [carpet_area],
        "Floor_No": [floor],
        "Parking_Spaces": [parking],
        "Age_Years": [age],
    }
)

# --- PREDICTION ---
# Model predicts Log(Price_Cr), so we use expm1
raw_pred = model.predict(input_df)[0]
price_cr = np.expm1(raw_pred)
human_readable_price = format_mumbai_currency(price_cr)

# --- MAIN DASHBOARD ---
col_main, col_stats = st.columns([3, 2], gap="large")

with col_main:
    st.subheader("Market Valuation")

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Estimated Valuation", human_readable_price)
    with m_col2:
        # Rate per SqFt calculation
        psf = (price_cr * 10_000_000) / carpet_area
        st.metric("Market Rate", f"₹{int(psf):,}/sqft")

    # Visual Gauge (Adjusted for Mumbai Cr scale)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=price_cr,
            number={"suffix": " Cr", "font": {"size": 40}},
            gauge={
                "axis": {"range": [0, 15], "tickwidth": 1},  # Adjusted scale
                "bar": {"color": "#B91C1C"},
                "steps": [
                    {"range": [0, 2], "color": "#D1FAE5"},
                    {"range": [2, 7], "color": "#FEF3C7"},
                    {"range": [7, 15], "color": "#FEE2E2"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "value": price_cr,
                },
            },
        )
    )
    fig.update_layout(height=350, margin=dict(t=50, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("Property Scorecard")

    # Radar Chart
    categories = ["Area", "BHK", "Floor Height", "Newness"]
    r_values = [
        (carpet_area / 3000) * 10,
        (bhk / 5) * 10,
        (floor / 60) * 10,
        (1 - age / 30) * 10,
    ]

    fig_radar = go.Figure(
        data=go.Scatterpolar(
            r=r_values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(185, 28, 28, 0.3)",
            line_color="#B91C1C",
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])), height=350
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    dynamic_text = generate_mumbai_insight(
        locality, municipality, prop_type, bhk, carpet_area, floor, age
    )
    st.info(f"💡 **AI Insight:** {dynamic_text}")

# --- APPRECIATION FORECAST ---
st.subheader("📈 5-Year Capital Appreciation Forecast")
years = [datetime.now().year + i for i in range(6)]
# Assuming 9.5% for Mumbai (slightly higher than Pune due to infrastructure projects)
forecast = [price_cr * (1.095**i) for i in range(6)]

fig_growth = px.area(x=years, y=forecast, labels={"x": "Year", "y": "Valuation (Cr)"})
fig_growth.update_traces(line_color="#B91C1C", fillcolor="rgba(185, 28, 28, 0.1)")
st.plotly_chart(fig_growth, use_container_width=True)

# --- PDF & FOOTER ---
if predict_btn:
    summary = {
        "Locality": locality,
        "Municipality": municipality,
        "Type": prop_type,
        "BHK": f"{bhk} BHK",
        "Area": f"{carpet_area} Sq.Ft",
        "Floor": f"Level {floor}",
        "Age": f"{age} Years",
        "Rate/Sq.Ft": f"Rs. {int(psf):,}",
    }

    try:
        pdf_bytes = generate_pdf(summary, human_readable_price, price_cr, dynamic_text)
        st.sidebar.success("✅ Valuation Certificate Ready!")
        st.sidebar.download_button(
            label="📥 Download Certificate",
            data=pdf_bytes,
            file_name=f"Mumbai_Valuation_{locality}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.sidebar.error(f"PDF Error: {e}")

st.markdown("---")
footer_html = f"""
    <div class="footer">
        <p>Developed by <b>Congnix AI</b></p>
        <p>© {datetime.now().year} | Mumbai Metropolitan Intelligence Terminal</p>
    </div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
