# strategy_evaluator.py
# This file handles all the evaluation logic
# It loads the trained model and takes strategy inputs to produce outputs
# app.py calls this file — you don't run this directly

import pickle
import numpy as np
import pandas as pd
from config import (
    MODEL_PATH, RESULT_LABELS,
    get_strategy_rating, get_risk_level, get_explanation
)

def load_model():
    """Load the trained model from disk"""
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        raise FileNotFoundError(
            "Model file not found. Please run train_model.py first."
        )

def evaluate_strategy(poss, sh, sot, xg, xga, fk, venue):
    """
    Takes strategy inputs from the coach and returns evaluation metrics.

    Parameters:
        poss  : Possession percentage (e.g. 65)
        sh    : Total shots (e.g. 15)
        sot   : Shots on target (e.g. 7)
        xg    : Expected goals for (e.g. 1.8)
        xga   : Expected goals against (e.g. 1.0)
        fk    : Free kicks / fouls (e.g. 10)
        venue : 1 for Home, 0 for Away

    Returns a dictionary with all evaluation metrics
    """

    model = load_model()

    # Build the input as a 2D array (model expects this shape)
    input_features = np.array([[poss, sh, sot, xg, xga, fk, venue]])

    # Get probabilities for Loss, Draw, Win
    probabilities = model.predict_proba(input_features)[0]

    # The model classes are ordered as 0=Loss, 1=Draw, 2=Win
    # We match them to their labels
    class_order = model.classes_  # e.g. [0, 1, 2]
    prob_dict = {cls: prob for cls, prob in zip(class_order, probabilities)}

    loss_prob = prob_dict.get(0, 0.0)
    draw_prob = prob_dict.get(1, 0.0)
    win_prob  = prob_dict.get(2, 0.0)

    # Calculate strategy rating and risk
    rating = get_strategy_rating(win_prob)
    risk   = get_risk_level(win_prob, xga)
    explanation = get_explanation(win_prob, draw_prob, loss_prob)

    return {
        "win_probability":  round(win_prob * 100, 1),
        "draw_probability": round(draw_prob * 100, 1),
        "loss_probability": round(loss_prob * 100, 1),
        "strategy_rating":  rating,
        "risk_level":       risk,
        "explanation":      explanation
    }


# -------------------------------------------------------
# Formation Recommendation — data-driven, no model needed
# -------------------------------------------------------
DATA_PATH_FOR_FORMATIONS = "data/matches_laliga.csv"

def recommend_formation(opp_formation, min_matches=10):
    """
    Given the opponent's formation, looks at historical La Liga data
    and returns the top 3 formations that won most often against it.

    Parameters:
        opp_formation : str  — e.g. "4-4-2"
        min_matches   : int  — minimum matches needed to include a formation
                               (avoids small-sample flukes like 1W/1 match = 100%)

    Returns a list of dicts: [{ formation, win_rate, wins, total }, ...]
    """
    try:
        df = pd.read_csv(DATA_PATH_FOR_FORMATIONS)
    except FileNotFoundError:
        return None  # caller will show a friendly error

    # Clean the diamond variant symbol from formations (e.g. "4-3-3◆" → "4-3-3")
    df["formation_clean"] = df["formation"].str.replace("◆", "", regex=False).str.strip()

    # Filter to only matches where opponent used this formation
    subset = df[df["opp formation"] == opp_formation].copy()

    if len(subset) == 0:
        return []

    # Group by your formation and calculate win rate
    grouped = subset.groupby("formation_clean").agg(
        total=("result", "count"),
        wins=("result", lambda x: (x == "W").sum())
    ).reset_index()

    # Drop formations with too few matches — unreliable sample
    grouped = grouped[grouped["total"] >= min_matches]

    if grouped.empty:
        return []

    grouped["win_rate"] = (grouped["wins"] / grouped["total"] * 100).round(1)
    grouped = grouped.sort_values("win_rate", ascending=False).head(3)

    return grouped.rename(columns={"formation_clean": "formation"}).to_dict(orient="records")