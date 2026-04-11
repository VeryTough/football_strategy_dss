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


# -------------------------------------------------------
# Opposition Scouting Report — data-driven, no model needed
# -------------------------------------------------------
def get_scouting_report(team_name):
    """
    Given an opponent team name, returns a full scouting report
    derived from their historical La Liga matches.

    Returns a dict with overall stats, home/away splits,
    most used formations, weak points, and last 5 matches.
    """
    try:
        df = pd.read_csv(DATA_PATH_FOR_FORMATIONS)
    except FileNotFoundError:
        return None

    team_df = df[df["team"] == team_name].copy()

    if len(team_df) == 0:
        return {}

    # ── Overall stats ──
    total     = len(team_df)
    wins      = (team_df["result"] == "W").sum()
    draws     = (team_df["result"] == "D").sum()
    losses    = (team_df["result"] == "L").sum()
    win_rate  = round(wins / total * 100, 1)

    avg_xg    = round(team_df["xg"].mean(), 2)
    avg_xga   = round(team_df["xga"].mean(), 2)
    avg_poss  = round(team_df["poss"].mean(), 1)
    avg_sh    = round(team_df["sh"].mean(), 1)
    avg_sot   = round(team_df["sot"].mean(), 1)

    # ── Home vs Away ──
    home_df   = team_df[team_df["venue"] == "Home"]
    away_df   = team_df[team_df["venue"] == "Away"]
    home_wr   = round((home_df["result"] == "W").mean() * 100, 1) if len(home_df) > 0 else 0
    away_wr   = round((away_df["result"] == "W").mean() * 100, 1) if len(away_df) > 0 else 0
    home_xga  = round(home_df["xga"].mean(), 2) if len(home_df) > 0 else 0
    away_xga  = round(away_df["xga"].mean(), 2) if len(away_df) > 0 else 0

    # ── Most used formations (top 3) ──
    formation_clean = team_df["formation"].str.replace("◆", "", regex=False).str.strip()
    top_formations  = formation_clean.value_counts().head(3).to_dict()

    # ── Weak points ──
    weak_points = []
    if away_xga > avg_xga * 1.2:
        weak_points.append(f"Defensively vulnerable away — avg xGA {away_xga} vs {avg_xga} overall")
    if away_wr < home_wr - 15:
        weak_points.append(f"Significant home/away gap — {home_wr}% home win rate vs {away_wr}% away")
    if avg_xga > 1.5:
        weak_points.append(f"High defensive exposure overall — avg xGA {avg_xga}")
    if avg_sot / avg_sh < 0.35 if avg_sh > 0 else False:
        weak_points.append(f"Low shot accuracy — only {round(avg_sot/avg_sh*100,1)}% of shots on target")
    if not weak_points:
        weak_points.append("No major statistical weaknesses identified — strong all-round team")

    # ── Last 5 matches ──
    last5 = (
        team_df.sort_values("date", ascending=False)
        .head(5)[["date", "opponent", "venue", "result", "formation", "xg", "xga"]]
        .to_dict(orient="records")
    )

    return {
        "team":            team_name,
        "total_matches":   total,
        "wins":            int(wins),
        "draws":           int(draws),
        "losses":          int(losses),
        "win_rate":        win_rate,
        "avg_xg":          avg_xg,
        "avg_xga":         avg_xga,
        "avg_poss":        avg_poss,
        "avg_sh":          avg_sh,
        "avg_sot":         avg_sot,
        "home_win_rate":   home_wr,
        "away_win_rate":   away_wr,
        "home_xga":        home_xga,
        "away_xga":        away_xga,
        "top_formations":  top_formations,
        "weak_points":     weak_points,
        "last_5":          last5,
    }