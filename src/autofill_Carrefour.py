from __future__ import annotations

import time
import glob
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from .config import FAILED_BARCODES_FILE, INVOICES_DIR
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def _wait_click(driver, by, value, timeout: int = 15):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    el.click()
    return el


def _wait_send_keys(driver, by, value, text: str, timeout: int = 15, clear: bool = True):
    el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    if clear:
        try:
            el.clear()
        except Exception:
            pass
    el.send_keys(text)
    return el


def _find_latest_new_pdf(download_dir: Path, before: set[Path], timeout: int = 30) -> Path:
    """
    Wait until a new PDF appears in download_dir compared to 'before'.
    Returns the newest downloaded file.
    """
    start = time.time()
    while time.time() - start < timeout:
        current = {Path(p) for p in glob.glob(str(download_dir / "*.pdf"))}
        new_files = current - before
        if new_files:
            return max(new_files, key=lambda p: p.stat().st_ctime)
        time.sleep(0.5)
    raise RuntimeError("No new PDF file detected (download may have failed).")


def autofill_carrefour(
    barcodes: List[str],
    status: Dict[str, str],
    *,
    max_attempts: int = 3,
    chrome_version_main: Optional[int] = None,
    headless: bool = False,
) -> Dict[str, object]:
    """
    Automates Carrefour invoice retrieval from barcodes.

    Required status keys:
      address, zipCode, city, siret, vat
    """
    download_dir = INVOICES_DIR
    failed_barcodes_file = FAILED_BARCODES_FILE
    download_dir.mkdir(parents=True, exist_ok=True)
    failed_barcodes_file.parent.mkdir(parents=True, exist_ok=True)

    required_keys = ["address", "zipCode", "city", "siret", "vat"]
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
                print(f"[Carrefour] Attempt {attempt}/{max_attempts} for barcode: {barcode}")

                options = uc.ChromeOptions()

                # Make downloads go to our folder
                prefs = {
                    "download.default_directory": str(download_dir.resolve()),
                    "plugins.always_open_pdf_externally": True,
                }
                options.add_experimental_option("prefs", prefs)

                if headless:
                    options.add_argument("--headless=new")

                before_pdfs = {Path(p) for p in glob.glob(str(download_dir / "*.pdf"))}

                if chrome_version_main is None:
                    driver = uc.Chrome(options=options)
                else:
                    driver = uc.Chrome(options=options, version_main=chrome_version_main)

                driver.get("https://www.carrefour.fr/services/facture")

                # Cookies accept (sometimes not present)
                try:
                    _wait_click(driver, By.ID, "onetrust-accept-btn-handler", timeout=5)
                except Exception:
                    pass

                # Start button (your original used class 'c-button__loader__container')
                # We keep it but wait properly:
                _wait_click(driver, By.CLASS_NAME, "c-button__loader__container", timeout=15)

                # Select "entreprise"
                _wait_click(driver, By.ID, "entreprise", timeout=15)

                # NOTE: Your code sends siret into companyName (we keep your behavior)
                _wait_send_keys(driver, By.NAME, "companyName", status["siret"], timeout=15)

                _wait_send_keys(driver, By.NAME, "ticketNumber", barcode, timeout=15)

                _wait_click(driver, By.XPATH, "//button[contains(., 'Valider')]", timeout=20)

                _wait_click(driver, By.XPATH, "//button[contains(., 'Confirmer mes infos')]", timeout=20)

                # Fill company details
                _wait_send_keys(driver, By.NAME, "address", status["address"], timeout=15)
                _wait_send_keys(driver, By.NAME, "postalCode", status["zipCode"], timeout=15)
                _wait_send_keys(driver, By.NAME, "city", status["city"], timeout=15)
                _wait_send_keys(driver, By.NAME, "companyIdentifier", status["siret"], timeout=15)
                _wait_send_keys(driver, By.NAME, "companyVatNumber", status["vat"], timeout=15)

                # Download (button or link depending on UI)
                try:
                    _wait_click(driver, By.XPATH, "//button[contains(., 'Télécharger ma facture')]", timeout=20)
                except Exception:
                    try:
                        _wait_click(driver, By.LINK_TEXT, "Télécharger ma facture", timeout=20)
                    except Exception as e:
                        raise RuntimeError("Could not find download button/link") from e

                latest_file = _find_latest_new_pdf(download_dir, before_pdfs, timeout=40)

                new_name = download_dir / f"facture_{facture_count}.pdf"
                shutil.move(str(latest_file), str(new_name))

                print(f"[Carrefour] Saved invoice: {new_name.name}")
                downloaded_files.append(str(new_name))
                facture_count += 1
                success = True
                break

            except Exception as e:
                print(f"[Carrefour] Error attempt {attempt} for {barcode}: {e}")

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