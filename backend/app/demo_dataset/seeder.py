import os
import logging
from sqlalchemy.orm import Session
from app.models.models import Document, DocumentChunk, User
from app.rag.embedding import EmbeddingProvider
from app.rag.chunker import RecursiveStructureChunker
from passlib.context import CryptContext

logger = logging.getLogger("evida.seeder")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

HEALTHCARE_DEMO_DOCUMENTS = [
    {
        "title": "ADA Standards of Care in Diabetes (Clinical Guidelines 2025)",
        "domain": "Healthcare",
        "category": "Diabetes",
        "author": "American Diabetes Association Guidelines Panel",
        "publication_date": "2025-01-10",
        "source_url": "https://diabetesjournals.org/care/standards-2025",
        "description": "Comprehensive clinical practice guidelines for glycemic management, HbA1c target thresholds, microvascular screening, and cardiorenal protection in Type 2 Diabetes.",
        "pages": [
            {
                "page_number": 1,
                "text": """SECTION 1: EXECUTIVE SUMMARY & GLYCEMIC TARGETS
The American Diabetes Association (ADA) 2025 Standards of Care emphasizes individualized glycemic targets for adults with Type 2 Diabetes. An HbA1c goal of <7.0% (53 mmol/mol) is recommended for most nonpregnant adults to significantly lower microvascular complications such as diabetic retinopathy and nephropathy.
Key Guideline Recommendation:
- Routine screening for Type 2 Diabetes should begin at age 35 for all adults, or earlier in individuals with elevated Body Mass Index (BMI ≥ 25 kg/m²) and additional cardiometabolic risk factors.
- Lifestyle modification incorporating structured physical activity (at least 150 minutes per week of moderate-intensity exercise) combined with Mediterranean or low-carbohydrate dietary patterns is essential."""
            },
            {
                "page_number": 2,
                "text": """SECTION 2: RISK FACTORS & MACROVASCULAR COMPLICATIONS
Type 2 diabetes mellitus is a progressive metabolic disorder driven by peripheral insulin resistance and impaired pancreatic beta-cell insulin secretion.
Major Risk Factors:
1. Obesity and Visceral Adiposity: Elevated BMI (≥30 kg/m²) increases insulin resistance by 4-fold.
2. Sedentary Lifestyle: Lack of physical activity decreases GLUT4 translocation in skeletal muscle.
3. Family History and Genetics: First-degree relatives with T2D carry a 2- to 3-fold higher lifetime risk.
4. Hypertension and Dyslipidemia: Elevated blood pressure (≥130/80 mmHg) and high LDL cholesterol accelerate cardiovascular disease mortality by 3-fold in diabetic cohorts."""
            },
            {
                "page_number": 3,
                "text": """SECTION 3: PHARMACOTHERAPY & CARDIORENAL OUTCOMES
First-line pharmacotherapy for Type 2 Diabetes remains Metformin alongside comprehensive lifestyle intervention.
In patients with established atherosclerotic cardiovascular disease (ASCVD), heart failure, or chronic kidney disease (CKD), Sodium-Glucose Cotransporter-2 (SGLT2) inhibitors or Glucagon-Like Peptide-1 (GLP-1) receptor agonists with proven cardiorenal benefit are indicated independent of baseline HbA1c.
Clinical Trial Evidence:
- SGLT2 inhibitors demonstrate a 30% reduction in hospitalization for heart failure and slow diabetic nephropathy progression.
- GLP-1 receptor agonists reduce major adverse cardiovascular events (MACE) by 14% to 26%."""
            }
        ]
    },
    {
        "title": "AHA/ACC Guidelines for the Management of High Blood Pressure & Hypertension",
        "domain": "Healthcare",
        "category": "Hypertension",
        "author": "American Heart Association & American College of Cardiology",
        "publication_date": "2024-11-15",
        "source_url": "https://www.ahajournals.org/hypertension-guidelines",
        "description": "Evidence-based management thresholds, blood pressure categories, lifestyle sodium restriction protocols, and first-line pharmacotherapy recommendations.",
        "pages": [
            {
                "page_number": 1,
                "text": """SECTION 1: BLOOD PRESSURE CLASSIFICATION & DIAGNOSIS
Hypertension is defined as a sustained systolic blood pressure (SBP) ≥130 mmHg or diastolic blood pressure (DBP) ≥80 mmHg.
Blood Pressure Categories:
- Normal: SBP < 120 mmHg and DBP < 80 mmHg.
- Elevated: SBP 120–129 mmHg and DBP < 80 mmHg.
- Stage 1 Hypertension: SBP 130–139 mmHg or DBP 80–89 mmHg.
- Stage 2 Hypertension: SBP ≥ 140 mmHg or DBP ≥ 90 mmHg.

Screening Recommendations:
Out-of-office blood pressure monitoring (ABPM or HBPM) is recommended to confirm diagnosis and exclude masked hypertension or white-coat hypertension before initiating lifelong antihypertensive therapy."""
            },
            {
                "page_number": 2,
                "text": """SECTION 2: LIFESTYLE INTERVENTIONS & EFFICACY
Non-pharmacological lifestyle interventions are first-line for all patients with elevated BP or Stage 1 hypertension:
- Dietary Sodium Restriction: Reducing daily sodium intake to <2,300 mg (ideally <1,500 mg) lowers SBP by 5 to 8 mmHg.
- DASH Diet: Adherence to Dietary Approaches to Stop Hypertension yields a 8–14 mmHg SBP reduction.
- Aerobic Exercise: 90–150 minutes/week of dynamic aerobic exercise lowers SBP by 5 to 8 mmHg.
- Weight Loss: Every 1 kg weight loss reduces SBP by approximately 1 mmHg."""
            }
        ]
    },
    {
        "title": "Global Primary Prevention of Cardiovascular Disease & Lipid Control Study",
        "domain": "Healthcare",
        "category": "Cardiovascular Disease",
        "author": "European Society of Cardiology Research Group",
        "publication_date": "2025-02-01",
        "source_url": "https://www.escardio.org/guidelines-cv-prevention",
        "description": "Multi-center clinical trial investigating high-intensity statin therapy, low-density lipoprotein (LDL) lowering targets, and cardiovascular mortality outcomes.",
        "pages": [
            {
                "page_number": 1,
                "text": """SECTION 1: CARDIOVASCULAR RISK ESTIMATION & ATHEROSCLEROSIS
Cardiovascular disease (CVD) remains the leading cause of global mortality. The 10-year risk of fatal and non-fatal cardiovascular events should be calculated using validated risk calculators (SCORE2 or ASCVD Risk Estimator).
Primary Risk Factors:
1. Elevated Non-HDL and LDL Cholesterol: Sub-endothelial accumulation of ApoB-containing lipoproteins initiates coronary plaque formation.
2. Tobacco Smoking: Increases acute myocardial infarction risk by 300%.
3. Diabetes Mellitus: Accelerates arterial wall calcification and double coronary heart disease mortality.
4. Chronic Kidney Disease: Estimated GFR < 60 mL/min/1.73m² is an independent high-risk equivalent."""
            }
        ]
    },
    {
        "title": "Public Health Report on Chronic Disease Prevention & Screening Efficacy",
        "domain": "Healthcare",
        "category": "General Healthcare",
        "author": "CDC National Center for Health Statistics",
        "publication_date": "2024-10-05",
        "source_url": "https://www.cdc.gov/nchs/chronic-prevention-report",
        "description": "National survey data on early population screening, chronic metabolic disease prevalence, and multi-disease prevention strategies.",
        "pages": [
            {
                "page_number": 1,
                "text": """SECTION 1: POPULATION SCREENING & EARLY INTERVENTION
Chronic non-communicable diseases—including cardiovascular disease, diabetes, hypertension, and chronic respiratory disorders—account for over 70% of global mortality.
Key Epidemiological Findings:
- Early multi-disease screening programs reduce late-stage hospitalization costs by 34%.
- Over 38% of adults with prediabetes remain undiagnosed, highlighting systemic gaps in routine preventive care.
- Integrated community health clinic initiatives targeting combined metabolic risk factors demonstrate high cost-effectiveness."""
            }
        ]
    }
]

def seed_database_if_empty(db: Session, force: bool = False):
    """Seed initial demo user and Healthcare Research Knowledge Base documents."""
    try:
        # 1. Seed Demo User
        user = db.query(User).filter(User.email == "demo@evida.research").first()
        if not user:
            import hashlib
            hashed_pwd = hashlib.sha256("evida2026".encode()).hexdigest()
            user = User(
                email="demo@evida.research",
                full_name="Healthcare Researcher",
                password_hash=hashed_pwd,
                role="admin"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Check if demo documents exist
        demo_count = db.query(Document).filter(Document.is_demo == True).count()
        if demo_count > 0 and not force:
            logger.info(f"Database already contains {demo_count} demo documents. Skipping seeding.")
            return

        logger.info("Seeding Healthcare Research Knowledge Base demo dataset...")
        chunker = RecursiveStructureChunker(chunk_size=600, chunk_overlap=75)
        embedder = EmbeddingProvider()

        for doc_data in HEALTHCARE_DEMO_DOCUMENTS:
            doc = Document(
                user_id=user.id,
                title=doc_data["title"],
                domain=doc_data["domain"],
                category=doc_data["category"],
                author=doc_data["author"],
                publication_date=doc_data["publication_date"],
                source_url=doc_data["source_url"],
                description=doc_data["description"],
                total_pages=len(doc_data["pages"]),
                processing_status="READY",
                is_demo=True
            )
            db.add(doc)
            db.flush()

            # Process & Chunk
            chunks_data = chunker.chunk_document(
                document_id=doc.id,
                document_title=doc.title,
                pages_content=doc_data["pages"],
                domain=doc.domain,
                category=doc.category
            )

            chunk_models = []
            for c in chunks_data:
                vec = embedder.get_embedding(c["text"])
                chunk_m = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=c["chunk_index"],
                    page_number=c["page_number"],
                    section=c["section"],
                    text=c["text"],
                    token_count=c["token_count"],
                    domain=c["domain"],
                    category=c["category"],
                    embedding=vec
                )
                chunk_models.append(chunk_m)

            db.add_all(chunk_models)
            doc.chunk_count = len(chunk_models)

        db.commit()
        logger.info("Successfully seeded Healthcare Research Knowledge Base dataset!")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {str(e)}")
