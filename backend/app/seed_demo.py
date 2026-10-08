from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import Customer, Lead, Deal, Activity
from app.services.scoring import calculate_lead_score, deal_probability


def seed_demo_data():
    db = SessionLocal()

    try:
        # --------------------------------------------------
        # Avoid creating duplicate demo data
        # --------------------------------------------------
        if db.query(Customer).count() > 0:
            print("Demo data already exists. Skipping seed.")
            return

        # --------------------------------------------------
        # CUSTOMERS
        # --------------------------------------------------
        customers = [
            Customer(
                company_name="Acme Technologies",
                contact_name="Rahul Mehta",
                email="rahul.mehta@acmetech.com",
                phone="+91-9876543210",
                industry="Technology",
                location="Bengaluru",
                annual_revenue=75000000
            ),
            Customer(
                company_name="TechNova Solutions",
                contact_name="Rahul Malhotra",
                email="rahul.malhotra@technova.com",
                phone="+91-9876543211",
                industry="Technology",
                location="Bengaluru",
                annual_revenue=120000000
            ),
            Customer(
                company_name="FinEdge Capital",
                contact_name="Sneha Iyer",
                email="sneha.iyer@finedge.com",
                phone="+91-9876543212",
                industry="Finance",
                location="Mumbai",
                annual_revenue=180000000
            ),
            Customer(
                company_name="MediCore Health",
                contact_name="Karan Bhatia",
                email="karan.bhatia@medicore.com",
                phone="+91-9876543213",
                industry="Healthcare",
                location="Delhi",
                annual_revenue=95000000
            ),
            Customer(
                company_name="RetailHub India",
                contact_name="Meera Nair",
                email="meera.nair@retailhub.com",
                phone="+91-9876543214",
                industry="Retail",
                location="Mumbai",
                annual_revenue=65000000
            ),
            Customer(
                company_name="InsureMax",
                contact_name="Aditya Rao",
                email="aditya.rao@insuremax.com",
                phone="+91-9876543215",
                industry="Insurance",
                location="Pune",
                annual_revenue=150000000
            ),
            Customer(
                company_name="CloudWorks India",
                contact_name="Pooja Kapoor",
                email="pooja.kapoor@cloudworks.com",
                phone="+91-9876543216",
                industry="Technology",
                location="Hyderabad",
                annual_revenue=85000000
            )
        ]

        db.add_all(customers)
        db.flush()

        # --------------------------------------------------
        # LEADS
        # --------------------------------------------------
        lead_data = [
            (
                "Amit Sharma",
                "amit.sharma@techcorp.com",
                "TechCorp India",
                "referral",
                "technology",
                5000000
            ),
            (
                "Rahul Malhotra",
                "rahul.malhotra@technova.com",
                "TechNova Solutions",
                "referral",
                "technology",
                8000000
            ),
            (
                "Sneha Iyer",
                "sneha.iyer@finedge.com",
                "FinEdge Capital",
                "linkedin",
                "finance",
                6000000
            ),
            (
                "Karan Bhatia",
                "karan.bhatia@medicore.com",
                "MediCore Health",
                "website",
                "healthcare",
                4500000
            ),
            (
                "Meera Nair",
                "meera.nair@retailhub.com",
                "RetailHub India",
                "email",
                "retail",
                1500000
            ),
            (
                "Aditya Rao",
                "aditya.rao@insuremax.com",
                "InsureMax",
                "referral",
                "insurance",
                7000000
            ),
            (
                "Pooja Kapoor",
                "pooja.kapoor@cloudworks.com",
                "CloudWorks India",
                "website",
                "technology",
                2500000
            ),
            (
                "Vivek Joshi",
                "vivek.joshi@marketpro.com",
                "MarketPro",
                "cold_call",
                "retail",
                400000
            ),
            (
                "Nisha Sharma",
                "nisha.sharma@finserve.com",
                "FinServe",
                "referral",
                "finance",
                5500000
            )
        ]

        leads = []

        for (
            name,
            email,
            company_name,
            source,
            industry,
            estimated_value
        ) in lead_data:

            score, priority = calculate_lead_score(
                source,
                industry,
                estimated_value
            )

            leads.append(
                Lead(
                    name=name,
                    email=email,
                    company_name=company_name,
                    source=source,
                    industry=industry,
                    estimated_value=estimated_value,
                    lead_score=score,
                    priority=priority
                )
            )

        db.add_all(leads)
        db.flush()

        # --------------------------------------------------
        # DEALS
        # --------------------------------------------------
        deal_data = [
            (
                "TechNova AI Analytics Platform",
                customers[1].id,
                8000000,
                "negotiation"
            ),
            (
                "FinEdge Customer Intelligence",
                customers[2].id,
                6000000,
                "proposal"
            ),
            (
                "MediCore Data Modernization",
                customers[3].id,
                4500000,
                "qualification"
            ),
            (
                "RetailHub Personalization Suite",
                customers[4].id,
                1500000,
                "prospecting"
            ),
            (
                "InsureMax Risk Analytics",
                customers[5].id,
                7000000,
                "closed_won"
            ),
            (
                "CloudWorks ML Platform",
                customers[6].id,
                5700000,
                "closed_won"
            ),
            (
                "Acme Enterprise Software Deal",
                customers[0].id,
                2500000,
                "closed_lost"
            )
        ]

        deals = []

        for name, customer_id, value, stage in deal_data:

            probability = deal_probability(stage)

            deals.append(
                Deal(
                    name=name,
                    customer_id=customer_id,
                    value=value,
                    stage=stage,
                    probability=probability
                )
            )

        db.add_all(deals)
        db.flush()

        # --------------------------------------------------
        # ACTIVITIES
        # --------------------------------------------------
        now = datetime.utcnow()

        activities = [
            Activity(
                customer_id=customers[0].id,
                deal_id=deals[6].id,
                subject="Discovery Call",
                activity_type="Call",
                description="Discovery call regarding enterprise requirements.",
                due_date=now - timedelta(days=3),
                completed=True
            ),
            Activity(
                customer_id=customers[1].id,
                deal_id=deals[0].id,
                subject="Negotiation Follow-up",
                activity_type="Follow-up",
                description="Follow up with decision maker regarding pricing.",
                due_date=now + timedelta(days=1),
                completed=False
            ),
            Activity(
                customer_id=customers[2].id,
                deal_id=deals[1].id,
                subject="Proposal Review",
                activity_type="Meeting",
                description="Review proposal and commercial terms.",
                due_date=now + timedelta(days=2),
                completed=False
            ),
            Activity(
                customer_id=customers[3].id,
                deal_id=deals[2].id,
                subject="Technical Requirements",
                activity_type="Call",
                description="Discuss technical requirements and implementation.",
                due_date=now - timedelta(days=1),
                completed=True
            ),
            Activity(
                customer_id=customers[5].id,
                deal_id=deals[4].id,
                subject="Contract Signed",
                activity_type="Meeting",
                description="Contract completion and handover.",
                due_date=now - timedelta(days=5),
                completed=True
            ),
            Activity(
                customer_id=customers[6].id,
                deal_id=deals[5].id,
                subject="Implementation Kickoff",
                activity_type="Meeting",
                description="Kickoff meeting for implementation.",
                due_date=now - timedelta(days=2),
                completed=True
            ),
            Activity(
                lead_id=leads[0].id,
                subject="Lead Qualification",
                activity_type="Call",
                description="Initial qualification call with high-priority lead.",
                due_date=now + timedelta(days=1),
                completed=False
            ),
            Activity(
                lead_id=leads[5].id,
                subject="Stakeholder Introduction",
                activity_type="Email",
                description="Introduce solution to key stakeholders.",
                due_date=now + timedelta(days=3),
                completed=False
            )
        ]

        db.add_all(activities)
        db.commit()

        print("========================================")
        print("Demo data created successfully.")
        print(f"Customers: {len(customers)}")
        print(f"Leads: {len(leads)}")
        print(f"Deals: {len(deals)}")
        print(f"Activities: {len(activities)}")
        print("========================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()