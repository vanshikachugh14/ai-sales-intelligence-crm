from sqlalchemy.orm import Session

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
    # LEAD PRIORITIZATION
    # -------------------------

    if (
        "lead" in question
        and (
            "call" in question
            or "contact" in question
            or "priority" in question
            or "today" in question
            or "focus" in question
        )
    ):

        if not leads:
            return "There are currently no leads."

        # Rank using both lead score and estimated value.
        ranked_leads = sorted(
            leads,
            key=lambda x: (
                x.lead_score or 0,
                x.estimated_value or 0
            ),
            reverse=True
        )

        response = (
            "Based on lead score and potential deal value, "
            "I would prioritize these leads:\n\n"
        )

        for i, lead in enumerate(ranked_leads[:5], 1):

            response += (
                f"{i}. {lead.name} ({lead.company_name})\n"
                f"   Lead score: {lead.lead_score}/100 | "
                f"Priority: {lead.priority}\n"
                f"   Estimated value: "
                f"₹{lead.estimated_value:,.0f}\n"
                f"   Recommended action: Contact first\n\n"
            )

        return response

    # -------------------------
    # PIPELINE ANALYSIS
    # -------------------------

    if (
        "pipeline" in question
        or "revenue" in question
    ):

        if not deals:
            return "There are currently no deals."

        total_pipeline = sum(
            deal.value or 0
            for deal in deals
        )

        weighted_pipeline = sum(
            (deal.value or 0) *
            (deal.probability or 0) /
            100
            for deal in deals
        )

        won_revenue = sum(
            deal.value or 0
            for deal in deals
            if deal.stage == "closed_won"
        )

        lost_revenue = sum(
            deal.value or 0
            for deal in deals
            if deal.stage == "closed_lost"
        )

        open_deals = [
            deal for deal in deals
            if deal.stage not in [
                "closed_won",
                "closed_lost"
            ]
        ]

        response = (
            f"Current sales pipeline: "
            f"₹{total_pipeline:,.0f}\n\n"
            f"Weighted pipeline: "
            f"₹{weighted_pipeline:,.0f}\n\n"
            f"Won revenue: "
            f"₹{won_revenue:,.0f}\n\n"
            f"Lost revenue: "
            f"₹{lost_revenue:,.0f}\n\n"
            f"Open opportunities: {len(open_deals)}\n\n"
        )

        if total_pipeline > 0:

            conversion = (
                won_revenue /
                total_pipeline *
                100
            )

            response += (
                f"Won revenue currently represents "
                f"{conversion:.1f}% of total pipeline value."
            )

        return response

    # -------------------------
    # DEAL ANALYSIS
    # -------------------------

    if (
        "deal" in question
        or "opportunit" in question
    ) and (
        "likely" in question
        or "close" in question
        or "best" in question
        or "probability" in question
        or "strongest" in question
    ):

        if not deals:
            return "There are currently no deals."

        sorted_deals = sorted(
            deals,
            key=lambda x: (
                x.probability or 0,
                x.value or 0
            ),
            reverse=True
        )

        response = (
            "The deals with the strongest closing potential are:\n\n"
        )

        for i, deal in enumerate(sorted_deals[:5], 1):

            weighted_value = (
                (deal.value or 0) *
                (deal.probability or 0) /
                100
            )

            response += (
                f"{i}. {deal.name}\n"
                f"   Deal value: ₹{deal.value:,.0f}\n"
                f"   Win probability: {deal.probability}%\n"
                f"   Weighted value: ₹{weighted_value:,.0f}\n"
                f"   Stage: {deal.stage}\n\n"
            )

        return response

    # -------------------------
    # PIPELINE RISK
    # -------------------------

    if (
        "risk" in question
        or "at risk" in question
        or "weak" in question
        or "danger" in question
    ) and "pipeline" in question:

        risky_deals = [
            deal for deal in deals
            if (
                deal.stage not in [
                    "closed_won",
                    "closed_lost"
                ]
                and (deal.probability or 0) <= 25
            )
        ]

        if not risky_deals:
            return "There are currently no obvious high-risk open deals."

        response = (
            "These open deals currently represent the highest "
            "pipeline risk:\n\n"
        )

        for deal in risky_deals[:5]:

            response += (
                f"• {deal.name} — "
                f"₹{deal.value:,.0f}, "
                f"{deal.probability}% probability, "
                f"stage: {deal.stage}\n"
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
            key=lambda x: x.estimated_value or 0,
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
    # ACTIVITIES / FOLLOW-UPS
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
    # DEFAULT
    # -------------------------

    return (
        "I can analyze your CRM data. Try asking:\n\n"
        "• Which leads should I call today?\n"
        "• What is our current pipeline?\n"
        "• Which deals are most likely to close?\n"
        "• Which deals are putting the pipeline at risk?\n"
        "• Which leads have the highest value?\n"
        "• How many customers do we have?\n"
        "• What follow-ups are pending?"
    )