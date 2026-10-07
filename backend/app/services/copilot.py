from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Lead, Customer, Deal, Activity


def answer(question: str, db: Session) -> str:

    question = question.lower().strip()

    # -------------------------
    # CRM DATA
    # -------------------------

    leads = db.query(Lead).order_by(
        Lead.lead_score.desc()
    ).all()

    deals = db.query(Deal).all()

    customers = db.query(Customer).all()

    pending_activities = (
        db.query(Activity)
        .filter(Activity.completed == False)
        .order_by(Activity.due_date.asc())
        .all()
    )

    # -------------------------
    # TOP LEADS
    # -------------------------

    if (
        "lead" in question
        and (
            "call" in question
            or "contact" in question
            or "priority" in question
            or "today" in question
        )
    ):

        high_leads = [
            lead
            for lead in leads
            if lead.priority == "High"
        ]

        if not high_leads:
            return "There are currently no high-priority leads."

        response = "I recommend contacting these high-priority leads first:\n\n"

        for lead in high_leads[:5]:
            response += (
                f"• {lead.name} ({lead.company_name}) — "
                f"Score: {lead.lead_score}, "
                f"Estimated value: ₹{lead.estimated_value:,.0f}\n"
            )

        return response

    # -------------------------
    # PIPELINE
    # -------------------------

    if (
        "pipeline" in question
        or "revenue" in question
    ):

        total_pipeline = sum(
            deal.value for deal in deals
        )

        weighted_pipeline = sum(
            deal.value * deal.probability / 100
            for deal in deals
        )

        won_revenue = sum(
            deal.value
            for deal in deals
            if deal.stage == "closed_won"
        )

        lost_revenue = sum(
            deal.value
            for deal in deals
            if deal.stage == "closed_lost"
        )

        return (
            f"Current sales pipeline: "
            f"₹{total_pipeline:,.0f}\n\n"
            f"Weighted pipeline: "
            f"₹{weighted_pipeline:,.0f}\n\n"
            f"Won revenue: "
            f"₹{won_revenue:,.0f}\n\n"
            f"Lost revenue: "
            f"₹{lost_revenue:,.0f}\n\n"
            f"There are {len(deals)} deals currently in the pipeline."
        )

    # -------------------------
    # BEST DEALS
    # -------------------------

    if (
        "deal" in question
        or "opportunit" in question
    ) and (
        "likely" in question
        or "close" in question
        or "best" in question
        or "probability" in question
    ):

        if not deals:
            return "There are currently no deals."

        sorted_deals = sorted(
            deals,
            key=lambda x: (
                x.probability,
                x.value
            ),
            reverse=True
        )

        response = "Deals with the strongest closing potential:\n\n"

        for deal in sorted_deals[:5]:

            weighted_value = (
                deal.value *
                deal.probability /
                100
            )

            response += (
                f"• {deal.name} — "
                f"₹{deal.value:,.0f}, "
                f"{deal.probability}% probability, "
                f"weighted value ₹{weighted_value:,.0f}\n"
            )

        return response

    # -------------------------
    # CUSTOMERS
    # -------------------------

    if (
        "customer" in question
        or "client" in question
    ):

        if not customers:
            return "There are currently no customers."

        total_revenue = sum(
            customer.annual_revenue or 0
            for customer in customers
        )

        return (
            f"You currently have {len(customers)} customers.\n\n"
            f"Combined reported annual revenue: "
            f"₹{total_revenue:,.0f}."
        )

    # -------------------------
    # ACTIVITIES
    # -------------------------

    if (
        "follow" in question
        or "activity" in question
        or "task" in question
        or "meeting" in question
    ):

        if not pending_activities:
            return "There are no pending sales activities."

        response = (
            f"You have {len(pending_activities)} "
            f"pending sales activities.\n\n"
        )

        for activity in pending_activities[:5]:

            response += (
                f"• {activity.activity_type}: "
                f"{activity.description}\n"
            )

        return response

    # -------------------------
    # HIGH VALUE LEADS
    # -------------------------

    if (
        "highest value" in question
        or "valuable lead" in question
        or "valuable leads" in question
    ):

        if not leads:
            return "There are currently no leads."

        sorted_leads = sorted(
            leads,
            key=lambda x: x.estimated_value,
            reverse=True
        )

        response = "Highest-value leads:\n\n"

        for lead in sorted_leads[:5]:

            response += (
                f"• {lead.name} — "
                f"{lead.company_name}, "
                f"₹{lead.estimated_value:,.0f}, "
                f"Score: {lead.lead_score}\n"
            )

        return response

    # -------------------------
    # DEFAULT RESPONSE
    # -------------------------

    return (
        "I can analyze your current CRM data. Try asking:\n\n"
        "• Which leads should I call today?\n"
        "• What is our current pipeline?\n"
        "• Which deals are most likely to close?\n"
        "• Which leads have the highest value?\n"
        "• How many customers do we have?\n"
        "• What follow-ups are pending?"
    )