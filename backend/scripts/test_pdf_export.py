import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import SessionLocal
from app.models.models import ResearchSession
from app.services.report_formatter import StructuredReportData
from app.services.pdf_generator import PDFReportGenerator

def test_pdf_export():
    db = SessionLocal()
    try:
        session = db.query(ResearchSession).filter(ResearchSession.status == "COMPLETED").order_by(ResearchSession.created_at.desc()).first()
        if not session:
            print("No completed session found in database.")
            return

        print(f"Testing PDF generation for session: {session.id} ({session.question})")
        
        # Clinical English Healthcare Report PDF
        data_en = StructuredReportData.build(session, lang="en")
        pdf_en_bytes = PDFReportGenerator.generate_pdf(data_en)
        en_path = "test_output_en.pdf"
        with open(en_path, "wb") as f:
            f.write(pdf_en_bytes)
        print(f"Clinical Healthcare English PDF generated successfully: {en_path} ({len(pdf_en_bytes)} bytes)")

    finally:
        db.close()

if __name__ == "__main__":
    test_pdf_export()
