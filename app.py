# app.py
# This is the main app file — run this to launch the web interface
#
# How to run:
#   streamlit run app.py
#
# Make sure you have run train_model.py at least once before this

import streamlit as st
from strategy_evaluator import evaluate_strategy
import random

# -------------------------------------------------------
# Football Facts Database
# -------------------------------------------------------
FOOTBALL_FACTS = [
    "🎯 Messi holds the record for most Ballon d'Or awards with 8 titles.",
    "⚽ The first official football match was played in 1872 between England and Scotland.",
    "🏆 La Liga is the top professional football division in Spain since 1929.",
    "💪 Cristiano Ronaldo has scored over 890 career goals across all competitions.",
    "🧠 The average football player covers 9.5 km per match.",
    "⚡ The fastest goal ever scored in La Liga was by Álvaro García in 5 seconds.",
    "🌍 Football is played by over 250 million players worldwide.",
    "🎪 Pele won 3 FIFA World Cups with Brazil (1958, 1962, 1970).",
    "🔥 Barcelona's MSN (Messi-Suárez-Neymar) is considered one of the greatest attacking trios.",
    "🛡️ The offside rule was introduced in 1874 to prevent 'goal hanging'.",
    "⭐ Real Madrid has won La Liga title a record 35 times.",
    "🎬 The first televised football match was in 1937 in England.",
    "💯 A regulation football field is between 100-130 yards long.",
    "🏅 The FIFA World Cup has been held every 4 years since 1930 (except 1942, 1946).",
    "🔮 VAR (Video Assistant Referee) was first used in La Liga in 2017.",
]

# -------------------------------------------------------
# Custom CSS for Futuristic UI
# -------------------------------------------------------
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a0e3a 50%, #0f2544 100%);
        color: #e0e0e0;
    }
    
    /* Hide default sidebar and restructure */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid #00d4ff;
    }
    
    /* Headers styling */
    h1, h2, h3 {
        color: #00d4ff;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        font-weight: 700;
    }
    
    /* Title glow effect */
    .title-glow {
        text-align: center;
        font-size: 3.5em;
        font-weight: 900;
        background: linear-gradient(90deg, #00d4ff, #00ffff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
    }
    
    /* Subtitle styling */
    .subtitle-text {
        text-align: center;
        font-size: 1.2em;
        color: #b0b0ff;
        margin-bottom: 30px;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Input containers */
    .stSlider > label {
        color: #00d4ff !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .stRadio > label {
        color: #00d4ff !important;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #0099cc) !important;
        color: #000 !important;
        font-weight: 800 !important;
        font-size: 1.1em !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 15px 30px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6) !important;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #00ffff, #00d4ff) !important;
        box-shadow: 0 0 30px rgba(0, 212, 255, 1) !important;
        transform: scale(1.05) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98) !important;
    }
    
    /* Metric cards */
    .stMetric {
        background: rgba(0, 212, 255, 0.05) !important;
        border: 2px solid #00d4ff !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        background: rgba(0, 212, 255, 0.1) !important;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.6) !important;
        transform: translateY(-3px);
    }
    
    .stMetricLabel {
        color: #b0b0ff !important;
        font-weight: 600 !important;
        font-size: 0.95em !important;
    }
    
    .stMetricValue {
        color: #00ffff !important;
        font-weight: 900 !important;
        font-size: 2.5em !important;
    }
    
    /* Info/Warning boxes */
    .stInfo, .stWarning {
        background: rgba(0, 212, 255, 0.1) !important;
        border-left: 4px solid #00d4ff !important;
        color: #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    
    .stError {
        background: rgba(255, 68, 68, 0.1) !important;
        border-left: 4px solid #ff4444 !important;
        color: #ff8888 !important;
    }
    
    /* Divider */
    hr {
        border-color: #00d4ff !important;
        opacity: 0.3;
        margin: 25px 0 !important;
    }
    
    /* Football fact box */
    .football-fact {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 255, 0.05));
        border: 2px solid #00d4ff;
        border-radius: 12px;
        padding: 18px;
        margin: 15px 0;
        color: #b0e0ff;
        font-weight: 500;
        font-size: 1.05em;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
        animation: pulse 3s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 15px rgba(0, 212, 255, 0.3); }
        50% { box-shadow: 0 0 25px rgba(0, 212, 255, 0.6); }
    }
    
    /* Caption text */
    .stCaption {
        color: #888 !important;
        font-size: 0.85em;
    }
    
    /* Column divider styling */
    .column-header {
        color: #00ffff;
        font-weight: 700;
        border-bottom: 2px solid #00d4ff;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    
    /* Chart styling */
    .st-ba {
        background-color: rgba(0, 212, 255, 0.1) !important;
    }
    
    /* Write text styling */
    .stMarkdown {
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# Page config — sets the browser tab title and layout
# -------------------------------------------------------
st.set_page_config(
    page_title="Football Strategy DSS",
    page_icon="⚽",
    layout="wide"
)

# -------------------------------------------------------
# Header with Futuristic Design
# -------------------------------------------------------
st.markdown("""
    <div class="title-glow">
        ⚽ FOOTBALL STRATEGY DSS
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="subtitle-text">
        Advanced Pattern Analysis & Predictive Strategy Evaluation System
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <p style='text-align: center; color: #a0a0ff; font-size: 1.05em; margin-bottom: 25px;'>
        Powered by AI-driven historical La Liga data analysis (2019–2025) | 4,700+ Match Database
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------
# Sidebar — context info and random football facts
# -------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h2 style='color: #00d4ff; text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);'>⚙️ SYSTEM INFO</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.write(
        "This is a **pattern-based strategy evaluation tool** built with advanced machine learning. "
        "It does not replace a coach — it supports decision-making "
        "by comparing your strategy to 4,700+ historical La Liga matches."
    )
    st.markdown("---")
    
    st.markdown("""
        <div style='background: rgba(0, 212, 255, 0.08); border: 2px solid #00d4ff; border-radius: 8px; padding: 15px;'>
            <p style='color: #00ffff; font-weight: 700;'>🤖 MODEL SPECIFICATIONS</p>
            <p style='color: #b0b0ff; margin: 8px 0;'><strong>Algorithm:</strong> Random Forest Classifier</p>
            <p style='color: #b0b0ff; margin: 8px 0;'><strong>Data Source:</strong> La Liga 2019–2025 (FBref via Kaggle)</p>
            <p style='color: #b0b0ff; margin: 8px 0;'><strong>Teams:</strong> 28 La Liga clubs</p>
            <p style='color: #b0b0ff; margin: 8px 0;'><strong>Matches:</strong> 4,700+</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Random Football Fact
    random_fact = random.choice(FOOTBALL_FACTS)
    st.markdown(f"""
        <div class='football-fact'>
            {random_fact}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
        <p style='text-align: center; color: #888; font-size: 0.9em;'>
            🌱 SDG 3 — Good Health & Well-Being<br>
            🎓 SDG 4 — Quality Education
        </p>
    """, unsafe_allow_html=True)

# -------------------------------------------------------
# Input Section — Modern Design
# -------------------------------------------------------
st.markdown("""
    <div style='background: rgba(0, 212, 255, 0.05); border-left: 4px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 30px;'>
        <h3 style='color: #00ffff; margin: 0 0 10px 0;'>📊 STEP 1 — CONFIGURE YOUR STRATEGY</h3>
        <p style='color: #a0a0ff; margin: 0;'>Fine-tune your match parameters below. The system will analyze patterns from 4,700+ La Liga matches.</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
        <p style='color: #00ffff; font-weight: 700; margin-bottom: 20px;'>⚽ ATTACKING METRICS</p>
    """, unsafe_allow_html=True)
    
    poss = st.slider(
        "Possession Target (%)",
        min_value=20, max_value=85, value=55, step=1,
        help="How much possession are you targeting?"
    )
    
    sh = st.slider(
        "Total Shots",
        min_value=0, max_value=40, value=12, step=1,
        help="Total shots you expect to take"
    )
    
    sot = st.slider(
        "Shots on Target",
        min_value=0, max_value=20, value=5, step=1,
        help="How many of those shots on target"
    )

with col2:
    st.markdown("""
        <p style='color: #00ffff; font-weight: 700; margin-bottom: 20px;'>🔥 QUALITY & DEFENSE</p>
    """, unsafe_allow_html=True)
    
    xg = st.slider(
        "Expected Goals (xG)",
        min_value=0.0, max_value=5.0, value=1.5, step=0.1,
        help="Attacking quality — higher means more dangerous chances"
    )
    
    xga = st.slider(
        "Expected Goals Against (xGA)",
        min_value=0.0, max_value=5.0, value=1.2, step=0.1,
        help="Defensive exposure — lower is better"
    )
    
    fk = st.slider(
        "Free Kicks / Fouls",
        min_value=0, max_value=25, value=10, step=1,
        help="Expected number of fouls conceded"
    )

# Venue selection with better styling
st.markdown("""
    <p style='color: #00ffff; font-weight: 700; margin: 20px 0 15px 0;'>🏟️ MATCH VENUE</p>
""", unsafe_allow_html=True)

col_venue_left, col_venue_right = st.columns([1, 3])
with col_venue_left:
    venue = st.radio(
        "Select Venue",
        options=["Home", "Away"],
        horizontal=True,
        label_visibility="collapsed"
    )

venue_encoded = 1 if venue == "Home" else 0

# Small validation warning
if sot > sh:
    st.markdown("""
        <div style='background: rgba(255, 150, 0, 0.15); border-left: 4px solid #ffa500; padding: 12px; border-radius: 6px; color: #ffb366;'>
            ⚠️ <strong>Validation Alert:</strong> Shots on target can't exceed total shots. Please adjust.
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("---")

# -------------------------------------------------------
# Evaluate Button
# -------------------------------------------------------
st.markdown("""
    <div style='background: rgba(0, 212, 255, 0.05); border-left: 4px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 20px;'>
        <h3 style='color: #00ffff; margin: 0 0 10px 0;'>⚡ STEP 2 — ANALYZE & PREDICT</h3>
        <p style='color: #a0a0ff; margin: 0;'>Click below to run AI analysis on your strategy against historical La Liga data.</p>
    </div>
""", unsafe_allow_html=True)

col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])
with col_btn_center:
    evaluate_button = st.button("🔍 EVALUATE STRATEGY", use_container_width=True)

if evaluate_button:

    if sot > sh:
        st.error("❌ Please fix: Shots on target cannot exceed total shots.")
    else:
        with st.spinner("⏳ Analyzing strategy against historical data..."):
            results = evaluate_strategy(
                poss=poss,
                sh=sh,
                sot=sot,
                xg=xg,
                xga=xga,
                fk=fk,
                venue=venue_encoded
            )

        st.markdown("---")
        
        # -------------------------------------------------------
        # Results Header
        # -------------------------------------------------------
        st.markdown("""
            <div style='text-align: center; margin-bottom: 30px;'>
                <h2 style='color: #00ffff; text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);'>✅ ANALYSIS COMPLETE</h2>
                <p style='color: #a0a0ff; font-size: 1.1em;'>Your strategy has been evaluated across 4,700+ historical matches</p>
            </div>
        """, unsafe_allow_html=True)

        # -------------------------------------------------------
        # Probabilities — 3 columns with enhanced styling
        # -------------------------------------------------------
        st.markdown("""
            <p style='color: #00ffff; font-weight: 700; margin: 30px 0 20px 0; font-size: 1.2em;'>📈 MATCH OUTCOME PROBABILITY</p>
        """, unsafe_allow_html=True)
        
        r1, r2, r3 = st.columns(3, gap="medium")

        with r1:
            st.metric(
                label="✅ Win Probability",
                value=f"{results['win_probability']}%"
            )
        with r2:
            st.metric(
                label="🟡 Draw Probability",
                value=f"{results['draw_probability']}%"
            )
        with r3:
            st.metric(
                label="❌ Loss Probability",
                value=f"{results['loss_probability']}%"
            )

        st.markdown("---")

        # -------------------------------------------------------
        # Rating and Risk — Side by side
        # -------------------------------------------------------
        st.markdown("""
            <p style='color: #00ffff; font-weight: 700; margin: 20px 0 20px 0; font-size: 1.2em;'>🎯 STRATEGY ASSESSMENT</p>
        """, unsafe_allow_html=True)
        
        r4, r5 = st.columns(2, gap="medium")

        with r4:
            st.metric(
                label="⭐ Strategy Rating",
                value=f"{results['strategy_rating']} / 10"
            )

        with r5:
            risk = results["risk_level"]
            risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
            st.metric(
                label="🛡️ Defensive Risk Level",
                value=f"{risk_color[risk]} {risk}"
            )

        st.markdown("---")

        # -------------------------------------------------------
        # Detailed Explanation
        # -------------------------------------------------------
        st.markdown("""
            <p style='color: #00ffff; font-weight: 700; margin: 20px 0 15px 0; font-size: 1.1em;'>📋 DETAILED ASSESSMENT</p>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style='background: rgba(0, 212, 255, 0.1); border-left: 4px solid #00d4ff; padding: 18px; border-radius: 8px; color: #e0e0e0; line-height: 1.6;'>
                {results["explanation"]}
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # -------------------------------------------------------
        # Visual bar chart of probabilities
        # -------------------------------------------------------
        st.markdown("""
            <p style='color: #00ffff; font-weight: 700; margin: 20px 0 15px 0; font-size: 1.1em;'>📊 PROBABILITY BREAKDOWN</p>
        """, unsafe_allow_html=True)
        
        import pandas as pd
        chart_data = pd.DataFrame({
            "Outcome": ["Win", "Draw", "Loss"],
            "Probability (%)": [
                results["win_probability"],
                results["draw_probability"],
                results["loss_probability"]
            ]
        }).set_index("Outcome")

        st.bar_chart(chart_data, use_container_width=True)

        # -------------------------------------------------------
        # Historical Comparison Table
        # -------------------------------------------------------
        st.markdown("---")
        st.markdown("""
            <p style='color: #00ffff; font-weight: 700; margin: 20px 0 15px 0; font-size: 1.1em;'>🗂️ HISTORICAL COMPARISON TABLE</p>
            <p style='color: #a0a0ff; margin-bottom: 15px;'>How your strategy compares against typical patterns in historical La Liga data</p>
        """, unsafe_allow_html=True)

        hist_data = {
            "Metric": ["Possession (%)", "Total Shots", "Shots on Target", "xG", "xGA", "Free Kicks"],
            "Your Strategy": [poss, sh, sot, xg, xga, fk],
            "Avg — WIN (La Liga)":  [57.2, 14.1, 5.8, 1.82, 0.97, 10.3],
            "Avg — DRAW (La Liga)": [50.1, 11.3, 4.2, 1.21, 1.19, 11.1],
            "Avg — LOSS (La Liga)": [42.8,  8.9, 3.1, 0.89, 2.14, 12.4],
        }
        hist_df = pd.DataFrame(hist_data)

        st.dataframe(
            hist_df.style.set_properties(**{
                'background-color': 'rgba(0,0,0,0)',
                'color': '#e0e0e0',
                'border-color': '#00d4ff'
            }).highlight_between(
                subset=["Your Strategy"],
                color="rgba(0, 212, 255, 0.15)"
            ),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("""
            <p style='color: #888; font-size: 0.85em; margin-top: 8px;'>
                📌 Reference averages computed from 4,700+ La Liga matches (2019–2025). 
                Comparing your inputs against winning/drawing/losing team benchmarks helps identify strategic gaps.
            </p>
        """, unsafe_allow_html=True)

        # -------------------------------------------------------
        # Random Football Fact in Results
        # -------------------------------------------------------
        st.markdown("---")
        random_fact = random.choice(FOOTBALL_FACTS)
        st.markdown(f"""
            <div class='football-fact'>
                {random_fact}
            </div>
        """, unsafe_allow_html=True)

        # -------------------------------------------------------
        # Disclaimer — important for viva
        # -------------------------------------------------------
        st.markdown("---")
        st.markdown("""
            <div style='background: rgba(255, 150, 0, 0.08); border-left: 4px solid #ffa500; padding: 15px; border-radius: 8px; margin-top: 20px;'>
                <p style='color: #ffb366; margin: 0; font-weight: 500;'>
                    ⚠️ <strong>IMPORTANT DISCLAIMER:</strong><br>
                    This tool is a decision support aid only. It identifies statistical patterns from historical data 
                    and does not understand football tactics. All final decisions remain with the coaching staff. 
                    Use this as a reference tool, not as the sole basis for strategic decisions.
                </p>
            </div>
        """, unsafe_allow_html=True)