from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import Customer, Lead, Deal, Activity


def seed_demo_data():
    db = SessionLocal()

    try:
        customer = db.query(Customer).first()
        lead = db.query(Lead).first()
        deal = db.query(Deal).first()

        if not customer:
            print("No customer found. Create a customer first.")
            return

        if not lead:
            print("No lead found. Create a lead first.")
            return

        if not deal:
            print("No deal found. Create a deal first.")
            return

        existing = db.query(Activity).count()

        if existing > 0:
            print(
                f"Activities already exist ({existing}). "
                "Skipping seed."
            )
            return

        now = datetime.now()

        activities = [

            Activity(
                customer_id=customer.id,
                deal_id=deal.id,
                subject="Discovery Call",
                activity_type="Call",
                description=(
                    "Discovery call with customer regarding "
                    "enterprise requirements."
                ),
                due_date=now - timedelta(days=2),
                completed=True
            ),

            Activity(
                customer_id=customer.id,
                deal_id=deal.id,
                subject="Product Demonstration",
                activity_type="Meeting",
                description=(
                    "Product demonstration and solution discussion."
                ),
                due_date=now - timedelta(days=1),
                completed=True
            ),

            Activity(
                customer_id=customer.id,
                deal_id=deal.id,
                subject="Proposal Sent",
                activity_type="Email",
                description=(
                    "Sent proposal and pricing details for review."
                ),
                due_date=now,
                completed=True
            ),

            Activity(
                customer_id=customer.id,
                deal_id=deal.id,
                subject="Proposal Follow-up",
                activity_type="Follow-up",
                description=(
                    "Follow up with decision maker regarding proposal."
                ),
                due_date=now + timedelta(days=1),
                completed=False
            ),

            Activity(
                customer_id=customer.id,
                deal_id=deal.id,
                subject="Implementation Discussion",
                activity_type="Call",
                description=(
                    "Discuss implementation timeline and next steps."
                ),
                due_date=now + timedelta(days=2),
                completed=False
            ),

            Activity(
                lead_id=lead.id,
                subject="Lead Qualification",
                activity_type="Call",
                description=(
                    "Initial qualification call with high-priority lead."
                ),
                due_date=now + timedelta(days=1),
                completed=False
            ),

            Activity(
                lead_id=lead.id,
                subject="Product Information",
                activity_type="Email",
                description=(
                    "Send product information and schedule "
                    "discovery meeting."
                ),
                due_date=now + timedelta(days=3),
                completed=False
            ),

            Activity(
                lead_id=lead.id,
                subject="Lead Follow-up",
                activity_type="Follow-up",
                description=(
                    "Follow up after initial sales conversation."
                ),
                due_date=now + timedelta(days=4),
                completed=False
            )
        ]

        db.add_all(activities)
        db.commit()

        print("Demo activities created successfully.")
        print(f"Created {len(activities)} activities.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()