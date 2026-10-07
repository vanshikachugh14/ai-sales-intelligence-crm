from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Customer, Lead, Deal, Activity


def dashboard(db: Session):

    total_customers = db.query(Customer).count()

    total_leads = db.query(Lead).count()

    high_priority_leads = (
        db.query(Lead)
        .filter(Lead.priority == "High")
        .count()
    )

    total_deals = db.query(Deal).count()

    total_pipeline_value = (
        db.query(
            func.coalesce(
                func.sum(Deal.value),
                0
            )
        ).scalar()
    )

    weighted_pipeline_value = (
        db.query(
            func.coalesce(
                func.sum(
                    Deal.value *
                    Deal.probability /
                    100
                ),
                0
            )
        ).scalar()
    )

    average_deal_probability = (
        db.query(
            func.coalesce(
                func.avg(Deal.probability),
                0
            )
        ).scalar()
    )

    won_revenue = (
        db.query(
            func.coalesce(
                func.sum(Deal.value),
                0
            )
        )
        .filter(
            Deal.stage == "closed_won"
        )
        .scalar()
    )

    lost_revenue = (
        db.query(
            func.coalesce(
                func.sum(Deal.value),
                0
            )
        )
        .filter(
            Deal.stage == "closed_lost"
        )
        .scalar()
    )

    total_activities = (
        db.query(Activity).count()
    )

    pending_activities = (
        db.query(Activity)
        .filter(
            Activity.completed == False
        )
        .count()
    )

    completed_activities = (
        db.query(Activity)
        .filter(
            Activity.completed == True
        )
        .count()
    )

    # -------------------------
    # PIPELINE BY STAGE
    # -------------------------

    stage_data = (
        db.query(
            Deal.stage,
            func.count(Deal.id),
            func.coalesce(
                func.sum(Deal.value),
                0
            )
        )
        .group_by(Deal.stage)
        .all()
    )

    pipeline_by_stage = []

    for stage, count, value in stage_data:
        pipeline_by_stage.append({
            "stage": stage,
            "deals": count,
            "value": float(value)
        })

    return {
        "customers": {
            "total": total_customers
        },

        "leads": {
            "total": total_leads,
            "high_priority": high_priority_leads
        },

        "deals": {
            "total": total_deals,
            "pipeline_value": round(
                float(total_pipeline_value),
                2
            ),
            "weighted_pipeline_value": round(
                float(weighted_pipeline_value),
                2
            ),
            "average_probability": round(
                float(average_deal_probability),
                2
            ),
            "won_revenue": round(
                float(won_revenue),
                2
            ),
            "lost_revenue": round(
                float(lost_revenue),
                2
            ),
            "pipeline_by_stage": pipeline_by_stage
        },

        "activities": {
            "total": total_activities,
            "pending": pending_activities,
            "completed": completed_activities
        }
    }