# app.py
# This is the main app file — run this to launch the web interface
#
# How to run:
#   streamlit run app.py
#
# Make sure you have run train_model.py at least once before this

import streamlit as st
from strategy_evaluator import evaluate_strategy

# -------------------------------------------------------
# Page config — sets the browser tab title and layout
# -------------------------------------------------------
st.set_page_config(
    page_title="Football Strategy DSS",
    page_icon="⚽",
    layout="centered"
)

# -------------------------------------------------------
# Header
# -------------------------------------------------------
st.title("⚽ Football Strategy Decision Support System")
st.markdown(
    "Enter your planned match strategy below. "
    "The system will evaluate it against historical La Liga data (2019–2025) "
    "and return a probability-based outcome rating."
)
st.markdown("---")

# -------------------------------------------------------
# Sidebar — context info
# -------------------------------------------------------
with st.sidebar:
    st.header("About This Tool")
    st.write(
        "This is a pattern-based strategy evaluation tool. "
        "It does not replace a coach — it supports decision-making "
        "by comparing your strategy to 4,700 historical La Liga matches."
    )
    st.markdown("---")
    st.write("**Model:** Random Forest Classifier")
    st.write("**Data:** La Liga 2019–2025 (FBref via Kaggle)")
    st.write("**Teams covered:** 28 La Liga clubs")
    st.markdown("---")
    st.caption("SDG 3 — Good Health & Well-Being")
    st.caption("SDG 4 — Quality Education")

# -------------------------------------------------------
# Input Section
# -------------------------------------------------------
st.subheader("Step 1 — Enter Your Strategy Parameters")

col1, col2 = st.columns(2)

with col1:
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

venue = st.radio(
    "Match Venue",
    options=["Home", "Away"],
    horizontal=True
)
venue_encoded = 1 if venue == "Home" else 0

# Small validation warning
if sot > sh:
    st.warning("Shots on target can't be more than total shots. Please adjust.")

st.markdown("---")

# -------------------------------------------------------
# Evaluate Button
# -------------------------------------------------------
st.subheader("Step 2 — Evaluate Strategy")

if st.button("🔍 Evaluate Strategy", use_container_width=True):

    if sot > sh:
        st.error("Please fix: Shots on target cannot exceed total shots.")
    else:
        with st.spinner("Analysing strategy against historical data..."):
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
        st.subheader("Step 3 — Evaluation Results")

        # -------------------------------------------------------
        # Probabilities — 3 columns
        # -------------------------------------------------------
        r1, r2, r3 = st.columns(3)

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
        # Rating and Risk
        # -------------------------------------------------------
        r4, r5 = st.columns(2)

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
        # Explanation
        # -------------------------------------------------------
        st.subheader("📋 Strategy Assessment")
        st.info(results["explanation"])

        # -------------------------------------------------------
        # Visual bar chart of probabilities
        # -------------------------------------------------------
        st.subheader("📊 Outcome Probability Breakdown")
        import pandas as pd
        chart_data = pd.DataFrame({
            "Outcome": ["Win", "Draw", "Loss"],
            "Probability (%)": [
                results["win_probability"],
                results["draw_probability"],
                results["loss_probability"]
            ]
        }).set_index("Outcome")

        st.bar_chart(chart_data)

        # -------------------------------------------------------
        # Disclaimer — important for viva
        # -------------------------------------------------------
        st.markdown("---")
        st.caption(
            "⚠️ This tool is a decision support aid only. It identifies statistical patterns "
            "from historical data and does not understand football tactics. "
            "All final decisions remain with the coaching staff."
        )
