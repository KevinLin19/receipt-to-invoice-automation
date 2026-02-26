from __future__ import annotations

import os
import time
import glob
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import INVOICES_DIR, FAILED_BARCODES_FILE
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _wait_click(driver, by, value, timeout: int = 15):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    el.click()
    return el


def _wait_send_keys(driver, by, value, text: str, timeout: int = 15):
    el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    el.clear()
    el.send_keys(text)
    return el


def _find_latest_new_pdf(download_dir: Path, before: set[Path], timeout: int = 30) -> Path:
    """
    Waits until a new PDF appears in download_dir compared to 'before'.
    Returns the newest downloaded file.
    """
    start = time.time()
    while time.time() - start < timeout:
        current = {Path(p) for p in glob.glob(str(download_dir / "*.pdf"))}
        new_files = current - before
        if new_files:
            # Choose the newest among new files
            return max(new_files, key=lambda p: p.stat().st_ctime)
        time.sleep(0.5)
    raise RuntimeError("No new PDF file detected (download may have failed).")


def autofill_auchan(
    barcodes: List[str],
    status: Dict[str, str],
    *,
    max_attempts: int = 3,
    chrome_version_main: Optional[int] = None,
    headless: bool = False,
) -> Dict[str, object]:
    """
    Automates Auchan invoice retrieval from barcodes.

    Parameters
    ----------
    barcodes : list[str]
        List of receipt barcodes.
    status : dict
        Company / contact info used to fill the form.
        Required keys: siret, companyName, address, zipCode, city, vat, name, contactEmail
    max_attempts : int
        Retry per barcode.
    chrome_version_main : Optional[int]
        Pin Chrome major version if needed. Prefer None for portability.
    headless : bool
        Run Chrome headless (may break downloads on some setups).

    Returns
    -------
    dict with:
        - downloaded: list of saved pdf paths
        - failed: list of barcodes that failed
    """
    download_dir = INVOICES_DIR
    failed_barcodes_file = FAILED_BARCODES_FILE
    download_dir.mkdir(parents=True, exist_ok=True)
    failed_barcodes_file.parent.mkdir(parents=True, exist_ok=True)

    required_keys = ["siret", "companyName", "address", "zipCode", "city", "vat", "name", "contactEmail"]
    missing = [k for k in required_keys if k not in status or not status[k]]
    if missing:
        raise ValueError(f"Missing required status fields: {missing}")

    downloaded_files: List[str] = []
    failed: List[str] = []

    facture_count = 1

    for barcode in barcodes:
        success = False

        for attempt in range(1, max_attempts + 1):
            driver = None
            try:
                print(f"[Auchan] Attempt {attempt}/{max_attempts} for barcode: {barcode}")

                options = uc.ChromeOptions()
                prefs = {
                    "download.default_directory": str(download_dir.resolve()),
                    "plugins.always_open_pdf_externally": True,
                }
                options.add_experimental_option("prefs", prefs)

                if headless:
                    # Headless downloads can be tricky; keep it optional.
                    options.add_argument("--headless=new")

                # Snapshot existing PDFs before starting this attempt
                before_pdfs = {Path(p) for p in glob.glob(str(download_dir / "*.pdf"))}

                if chrome_version_main is None:
                    driver = uc.Chrome(options=options)
                else:
                    driver = uc.Chrome(options=options, version_main=chrome_version_main)

                driver.get("https://www.auchan.fr/facture")

                # Cookies accept (may not always appear)
                try:
                    _wait_click(driver, By.ID, "onetrust-accept-btn-handler", timeout=5)
                except Exception:
                    pass

                _wait_click(driver, By.LINK_TEXT, "Commencer")

                _wait_send_keys(driver, By.ID, "barcode", barcode)

                # "Suivant"
                btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn")))
                if btn.text.strip().lower() == "suivant":
                    btn.click()

                _wait_click(driver, By.LINK_TEXT, "Un professionnel")

                _wait_click(driver, By.ID, "businessValue")
                _wait_click(driver, By.CSS_SELECTOR, 'li.business-type[data-businessid="PRIVATE_COMPANY"]')

                btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn")))
                if btn.text.strip().lower() == "suivant":
                    btn.click()

                _wait_click(driver, By.ID, "typeId")
                _wait_click(driver, By.CSS_SELECTOR, 'li.identification-type[data-typeid="SIRET"]')

                btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn")))
                if btn.text.strip().lower() == "suivant":
                    btn.click()

                _wait_send_keys(driver, By.ID, "siret", status["siret"])

                btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn")))
                if btn.text.strip().lower() == "suivant":
                    btn.click()

                # Company/contact form
                _wait_send_keys(driver, By.ID, "companyName", status["companyName"])
                _wait_send_keys(driver, By.ID, "companyAddress", status["address"])
                _wait_send_keys(driver, By.ID, "zipCode", status["zipCode"])
                _wait_send_keys(driver, By.ID, "city", status["city"])
                _wait_send_keys(driver, By.ID, "vat", status["vat"])
                _wait_send_keys(driver, By.ID, "contactName", status["name"])
                _wait_send_keys(driver, By.ID, "contactEmail", status["contactEmail"])

                btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn")))
                if btn.text.strip().lower() == "valider":
                    btn.click()

                # Submit
                _wait_click(driver, By.XPATH, '//button[@type="submit"]')

                # Download link
                _wait_click(driver, By.LINK_TEXT, "Télécharger", timeout=20)

                # Wait for a new PDF to appear
                latest_file = _find_latest_new_pdf(download_dir, before_pdfs, timeout=40)

                new_name = download_dir / f"facture_{facture_count}.pdf"
                shutil.move(str(latest_file), str(new_name))

                print(f"[Auchan] Saved invoice: {new_name.name}")
                downloaded_files.append(str(new_name))
                facture_count += 1
                success = True
                break  # stop retry loop

            except Exception as e:
                print(f"[Auchan] Error attempt {attempt} for {barcode}: {e}")

            finally:
                if driver is not None:
                    try:
                        driver.quit()
                    except Exception:
                        pass

        if not success:
            failed.append(barcode)
            try:
                with failed_barcodes_file.open("a", encoding="utf-8") as f:
                    f.write(barcode + "\n")
            except Exception:
                pass

    return {"downloaded": downloaded_files, "failed": failed}