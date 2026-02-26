from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Load configuration from .env file
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "data/invoices")
MERGED_DIR_PATH = os.getenv("MERGED_DIR", "data/merged_pdf")
MERGED_FILE_NAME = os.getenv("MERGED_FILE_NAME", "merged_invoices.pdf")
FAILED_BARCODES_FILE_PATH = os.getenv("FAILED_BARCODES_FILE", "data/failed_barcodes.txt")
CHROME_VERSION_MAIN = int(os.getenv("CHROME_VERSION_MAIN", "145"))

# Create full paths
INVOICES_DIR = Path(BASE_DIR / DOWNLOAD_DIR)
MERGED_DIR = Path(BASE_DIR / MERGED_DIR_PATH)
FAILED_BARCODES_FILE = Path(BASE_DIR / FAILED_BARCODES_FILE_PATH)

# Create directories if they don't exist
INVOICES_DIR.mkdir(parents=True, exist_ok=True)
MERGED_DIR.mkdir(parents=True, exist_ok=True)
FAILED_BARCODES_FILE.parent.mkdir(parents=True, exist_ok=True)