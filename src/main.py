# uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

from enum import Enum
import json
from typing import List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from pyzbar.pyzbar import decode
from PIL import Image
import io
from pathlib import Path

from .autofill_Auchan import autofill_auchan
from .autofill_Carrefour import autofill_carrefour
from .merge_pdf import merge_and_delete_pdfs

from .config import INVOICES_DIR, MERGED_DIR, MERGED_FILE_NAME, CHROME_VERSION_MAIN
from .profiles_loader import load_profile

app = FastAPI(title="Receipt → Invoice Automation")
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "src" / "static")), name="static")
PROFILES_EXAMPLE_PATH = BASE_DIR / "profiles.json"


class Store(str, Enum):
    auchan = "auchan"
    carrefour = "carrefour"


@app.get("/")
def home():
    with open("src/static/web") as f:
        return HTMLResponse(content=f.read())


@app.post("/upload")
async def upload_tickets(
    store: Store = Form(...),
    profile: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # 1) OCR / barcode extraction
    barcodes: list[str] = []
    failed_files: list[str] = []

    for file in files:
        contents = await file.read()
        try:
            image = Image.open(io.BytesIO(contents))
        except Exception:
            failed_files.append(file.filename)
            continue

        codes = decode(image)
        if not codes:
            failed_files.append(file.filename)
            continue

        barcode = codes[0].data.decode("utf-8", errors="ignore")
        barcodes.append(barcode)

    if not barcodes:
        raise HTTPException(
            status_code=422,
            detail={"message": "No barcodes detected", "failed_files": failed_files}
        )

    # 2) Load user profile (no hardcoded personal data in code)
    try:
        status = load_profile(profile)  # expects profiles.json
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3) Run automation + merge (blocking) in a threadpool
    async def run_pipeline():
        if store == Store.auchan:
            autofill_auchan(barcodes=barcodes, status=status, chrome_version_main=CHROME_VERSION_MAIN)
        else:
            autofill_carrefour(barcodes=barcodes, status=status, chrome_version_main=CHROME_VERSION_MAIN)

        merge_and_delete_pdfs(
            str(INVOICES_DIR),
            str(MERGED_DIR),
            MERGED_FILE_NAME
        )

    await run_in_threadpool(lambda: __import__("asyncio").run(run_pipeline()))

    merged_path = MERGED_DIR / MERGED_FILE_NAME
    if not merged_path.exists():
        raise HTTPException(status_code=500, detail="Merged PDF not found after processing")

    return JSONResponse({
        "store": store.value,
        "profile": profile,
        "barcodes_found": barcodes,
        "failed_files": failed_files,
        "merged_pdf": str(merged_path)
    })

@app.get("/profiles")
def list_profiles():
    if not PROFILES_EXAMPLE_PATH.exists():
        raise HTTPException(status_code=404, detail="profiles.json not found")

    data = json.loads(PROFILES_EXAMPLE_PATH.read_text(encoding="utf-8"))
    # retourne juste les noms de profils (keys)
    return {"profiles": list(data.keys())}

@app.get("/download")
def download_merged():
    merged_path = MERGED_DIR / MERGED_FILE_NAME
    if not merged_path.exists():
        raise HTTPException(status_code=404, detail="Merged PDF not found")
    return FileResponse(path=str(merged_path), filename=MERGED_FILE_NAME, media_type="application/pdf")