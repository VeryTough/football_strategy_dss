# config.py
# Central place for all settings, feature names, and thresholds
# If you want to change anything about the model or app, change it here

# Path to the dataset
DATA_PATH = "data/matches_laliga.csv"

# Path where the trained model will be saved
MODEL_PATH = "model.pkl"

# These are the columns we use to train the model
# We drop gf and ga because a coach won't know goals before the match
FEATURE_COLUMNS = ["poss", "sh", "sot", "xg", "xga", "fk", "venue_encoded"]

# This is what we're trying to predict
TARGET_COLUMN = "result_encoded"

# How we convert W/D/L to numbers for the model
RESULT_MAPPING = {"W": 2, "D": 1, "L": 0}

# Reverse mapping for displaying results
RESULT_LABELS = {2: "Win", 1: "Draw", 0: "Loss"}

# Venue encoding
VENUE_MAPPING = {"Home": 1, "Away": 0}

# Strategy rating thresholds (based on win probability)
# Win probability above 60% = high rating, below 40% = low rating
def get_strategy_rating(win_prob):
    rating = round(win_prob * 10, 1)
    return rating

# Defensive risk is based on xga and shots conceded pattern
def get_risk_level(win_prob, xga):
    if xga > 2.0:
        return "High"
    elif xga > 1.2:
        return "Medium"
    else:
        return "Low"

# Explanation text based on win probability
def get_explanation(win_prob, draw_prob, loss_prob):
    if win_prob >= 0.65:
        return "This strategy closely matches historically successful matches in La Liga. The attacking and possession patterns are strong."
    elif win_prob >= 0.45:
        return "This strategy shows moderate effectiveness. Similar patterns have resulted in mixed outcomes historically."
    elif draw_prob >= 0.35:
        return "This strategy is more likely to result in a draw. Consider increasing attacking output."
    else:
        return "This strategy carries high risk based on historical patterns. Defensive vulnerabilities may be a concern."
