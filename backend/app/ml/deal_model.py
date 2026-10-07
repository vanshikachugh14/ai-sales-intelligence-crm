import os
import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "deal_win_model.pkl"
)


def train_model():

    # Features:
    #
    # 1. Deal value in lakhs
    # 2. Sales stage
    # 3. Lead score
    # 4. Number of previous activities
    #
    # Target:
    # 1 = Won
    # 0 = Lost

    X = np.array([
        [5, 1, 40, 1],
        [8, 1, 50, 2],
        [10, 2, 55, 2],
        [12, 2, 60, 3],
        [15, 2, 65, 4],
        [18, 3, 70, 5],
        [20, 3, 75, 6],
        [25, 3, 80, 7],
        [30, 3, 85, 8],
        [35, 4, 90, 9],
        [40, 4, 95, 10],

        [50, 1, 20, 0],
        [45, 1, 30, 1],
        [40, 2, 35, 1],
        [35, 2, 40, 2],
        [30, 2, 45, 2],
        [25, 3, 50, 2],
        [20, 3, 55, 3],
        [15, 3, 60, 3],
        [10, 4, 65, 4],
    ])

    y = np.array([
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,

        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
    ])

    # Safety check
    if len(X) != len(y):
        raise ValueError(
            f"Training data mismatch: "
            f"X has {len(X)} rows but "
            f"y has {len(y)} labels."
        )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=5,
        random_state=42
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    return model


def get_model():

    if not os.path.exists(MODEL_PATH):
        return train_model()

    return joblib.load(MODEL_PATH)


def predict_win_probability(
    deal_value,
    stage,
    lead_score,
    activity_count
):

    stage_mapping = {
        "prospecting": 1,
        "qualification": 2,
        "proposal": 3,
        "negotiation": 4,
        "closed_won": 5,
        "closed_lost": 0
    }

    stage_value = stage_mapping.get(
        stage.lower(),
        1
    )

    model = get_model()

    features = np.array([[
        deal_value / 100000,
        stage_value,
        lead_score,
        activity_count
    ]])

    probability = model.predict_proba(
        features
    )[0][1]

    return round(
        float(probability * 100),
        2
    )