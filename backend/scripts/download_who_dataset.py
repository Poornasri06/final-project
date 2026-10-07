import os
import sys
import json
import urllib.request
import ssl

DOCUMENTS_CONFIG = [
    {
        "folder": "01_HOSPITAL_ADULT",
        "filename": "WHO_IMAI_Hospital_Care_Adults.pdf",
        "handle": "10665/70685",
        "title": "IMAI District Clinician Manual: Hospital Care for Adolescents and Adults",
        "category": "Hospital Adult",
        "domain": "Hospital Medicine & Acute Care",
        "author": "World Health Organization",
        "publication_date": "2011",
        "document_type": "Clinical Guideline & Manual",
        "source_url": "https://iris.who.int/handle/10665/70685"
    },
    {
        "folder": "02_HOSPITAL_CHILDREN",
        "filename": "WHO_Pocket_Book_Hospital_Care_Children.pdf",
        "handle": "10665/81170",
        "title": "Pocket Book of Hospital Care for Children: Guidelines for the Management of Common Childhood Illnesses",
        "category": "Hospital Children",
        "domain": "Pediatrics & Child Health",
        "author": "World Health Organization",
        "publication_date": "2013",
        "document_type": "Clinical Practice Guideline",
        "source_url": "https://iris.who.int/handle/10665/81170"
    },
    {
        "folder": "03_EMERGENCY_CRITICAL_CARE",
        "filename": "WHO_SARI_Clinical_Care_Toolkit.pdf",
        "handle": "10665/352851",
        "title": "Clinical Care for Severe Acute Respiratory Infection: Toolkit (COVID-19 Adaptation)",
        "category": "Emergency Critical Care",
        "domain": "Critical Care & Pulmonology",
        "author": "World Health Organization",
        "publication_date": "2022",
        "document_type": "Clinical Care Toolkit",
        "source_url": "https://iris.who.int/handle/10665/352851"
    },
    {
        "folder": "04_TUBERCULOSIS",
        "filename": "WHO_TB_Guidelines.pdf",
        "handle": "10665/353829",
        "title": "WHO Consolidated Guidelines on Tuberculosis: Module 4: Treatment",
        "category": "Tuberculosis",
        "domain": "Infectious Diseases & Mycobacteriology",
        "author": "World Health Organization",
        "publication_date": "2022",
        "document_type": "Consolidated Clinical Guideline",
        "source_url": "https://iris.who.int/handle/10665/353829"
    },
    {
        "folder": "05_HIV",
        "filename": "WHO_HIV_Guidelines.pdf",
        "handle": "10665/246200",
        "title": "Consolidated Guidelines on HIV Prevention, Diagnosis, Treatment and Care for Key Populations",
        "category": "HIV",
        "domain": "Infectious Diseases & Virology",
        "author": "World Health Organization",
        "publication_date": "2016",
        "document_type": "Consolidated Clinical Guideline",
        "source_url": "https://iris.who.int/handle/10665/246200"
    },
    {
        "folder": "06_DIABETES",
        "filename": "WHO_Diabetes_Guidelines.pdf",
        "handle": "10665/331710",
        "title": "HEARTS D: Diagnosis and Management of Type 2 Diabetes",
        "category": "Diabetes",
        "domain": "Endocrinology & Metabolic Health",
        "author": "World Health Organization",
        "publication_date": "2020",
        "document_type": "Technical Package & Clinical Protocol",
        "source_url": "https://iris.who.int/handle/10665/331710"
    },
    {
        "folder": "07_HYPERTENSION",
        "filename": "WHO_Hypertension_Guidelines.pdf",
        "handle": "10665/344424",
        "title": "Guideline for the Pharmacological Treatment of Hypertension in Adults",
        "category": "Hypertension",
        "domain": "Cardiovascular Health & Primary Care",
        "author": "World Health Organization",
        "publication_date": "2021",
        "document_type": "Clinical Practice Guideline",
        "source_url": "https://iris.who.int/handle/10665/344424"
    },
    {
        "folder": "08_NUTRITION",
        "filename": "WHO_Nutrition_Guidelines.pdf",
        "handle": "10665/374925",
        "title": "Carbohydrate Intake for Adults and Children: WHO Guideline Summary",
        "category": "Nutrition",
        "domain": "Public Health Nutrition & Chronic Disease Prevention",
        "author": "World Health Organization",
        "publication_date": "2023",
        "document_type": "Evidence-Based Nutritional Guideline",
        "source_url": "https://iris.who.int/handle/10665/374925"
    }
]

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def resolve_bitstream_url(handle: str) -> str:
    ctx = get_ssl_context()
    # 1. Query PID find
    pid_url = f"https://iris.who.int/server/api/pid/find?id={handle}"
    req = urllib.request.Request(pid_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        item_data = json.loads(r.read().decode())
    
    bundles_href = item_data.get("_links", {}).get("bundles", {}).get("href")
    if not bundles_href:
        raise ValueError(f"No bundles href for handle {handle}")

    # 2. Query Bundles
    req_b = urllib.request.Request(bundles_href, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req_b, context=ctx, timeout=30) as r:
        bundles_data = json.loads(r.read().decode())

    orig_bundle = None
    for b in bundles_data.get("_embedded", {}).get("bundles", []):
        if b.get("name") == "ORIGINAL":
            orig_bundle = b
            break
    if not orig_bundle and bundles_data.get("_embedded", {}).get("bundles"):
        orig_bundle = bundles_data["_embedded"]["bundles"][0]

    bitstreams_href = orig_bundle.get("_links", {}).get("bitstreams", {}).get("href")
    if not bitstreams_href:
        raise ValueError(f"No bitstreams href for bundle in {handle}")

    # 3. Query Bitstreams
    req_bs = urllib.request.Request(bitstreams_href, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req_bs, context=ctx, timeout=30) as r:
        bs_data = json.loads(r.read().decode())

    bitstreams = bs_data.get("_embedded", {}).get("bitstreams", [])
    if not bitstreams:
        raise ValueError(f"No bitstreams found in ORIGINAL bundle for {handle}")

    # Prefer english or main pdf
    selected_bs = None
    for bs in bitstreams:
        name = bs.get("name", "").lower()
        if name.endswith(".pdf") and ("eng" in name or "_en" in name or len(bitstreams) == 1):
            selected_bs = bs
            break
    if not selected_bs:
        for bs in bitstreams:
            if bs.get("name", "").lower().endswith(".pdf"):
                selected_bs = bs
                break
    if not selected_bs:
        selected_bs = bitstreams[0]

    content_url = selected_bs.get("_links", {}).get("content", {}).get("href")
    print(f"  Selected: {selected_bs.get('name')} (size: {selected_bs.get('sizeBytes')} bytes)")
    return content_url

def download_file(url: str, output_path: str):
    ctx = get_ssl_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp, open(output_path, "wb") as out:
        chunk_size = 1024 * 64
        total = 0
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out.write(chunk)
            total += len(chunk)
    return total

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "EVIDA_MEDICAL_DATASET"))
    os.makedirs(base_dir, exist_ok=True)
    print(f"Target dataset directory: {base_dir}")

    results = []
    for doc in DOCUMENTS_CONFIG:
        folder_path = os.path.join(base_dir, doc["folder"])
        os.makedirs(folder_path, exist_ok=True)
        pdf_path = os.path.join(folder_path, doc["filename"])

        print(f"\nProcessing [{doc['folder']}] {doc['filename']}...")
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 10000:
            print(f"  Already exists ({os.path.getsize(pdf_path)} bytes). Skipping download.")
            results.append({"doc": doc, "status": "EXISTS", "size": os.path.getsize(pdf_path)})
            continue

        try:
            print(f"  Resolving bitstream from handle {doc['handle']}...")
            content_url = resolve_bitstream_url(doc["handle"])
            print(f"  Downloading from {content_url}...")
            size = download_file(content_url, pdf_path)
            print(f"  Successfully downloaded: {size} bytes")
            results.append({"doc": doc, "status": "SUCCESS", "size": size})
        except Exception as e:
            print(f"  FAILED: {e}")
            results.append({"doc": doc, "status": "FAILED", "error": str(e)})

    # Write metadata JSON in EVIDA_MEDICAL_DATASET/metadata.json
    meta_path = os.path.join(base_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(DOCUMENTS_CONFIG, f, indent=2)
    print(f"\nSaved dataset metadata to {meta_path}")

    print("\nSummary:")
    for r in results:
        status = r["status"]
        name = r["doc"]["filename"]
        print(f"  {name}: {status}")
