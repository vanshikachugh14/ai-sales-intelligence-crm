def calculate_lead_score(source, industry, estimated_value):
    score = 0

    # Lead source
    source_scores = {
        "referral": 30,
        "website": 20,
        "linkedin": 15,
        "email": 10,
        "cold_call": 5
    }

    if source:
        score += source_scores.get(source.lower(), 5)

    # Industry
    high_value_industries = [
        "technology",
        "finance",
        "banking",
        "healthcare",
        "insurance"
    ]

    if industry and industry.lower() in high_value_industries:
        score += 25
    else:
        score += 10

    # Estimated deal value
    if estimated_value >= 5000000:
        score += 45
    elif estimated_value >= 1000000:
        score += 30
    elif estimated_value >= 500000:
        score += 20
    else:
        score += 10

    score = min(score, 100)

    if score >= 70:
        priority = "High"
    elif score >= 40:
        priority = "Medium"
    else:
        priority = "Low"

    return score, priority


def deal_probability(stage):
    probabilities = {
        "prospecting": 10,
        "qualification": 25,
        "proposal": 50,
        "negotiation": 75,
        "closed_won": 100,
        "closed_lost": 0
    }

    if not stage:
        return 10

    return probabilities.get(stage.lower(), 10)