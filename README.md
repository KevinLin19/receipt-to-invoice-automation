# Receipt → Invoice Automation

End-to-end automation system that converts receipt images into downloadable invoices using barcode OCR and browser automation.

---

## Overview

This project automates the retrieval of professional invoices from retail web portals (e.g., Auchan, Carrefour) based on receipt photos.

Instead of manually:

- logging into the portal
- entering receipt details
- filling company information
- downloading each invoice

the system performs the full workflow automatically.

It is designed as a practical demonstration of real-world automation using OCR + Selenium + API architecture.

---

## System Architecture

1. **Receipt Image(s)**  
   → Input photos of purchase receipts

2. **Barcode Detection (OCR)**  
   → Extract barcode data from the image

3. **Identifier Extraction**  
   → Parse receipt number or transaction ID

4. **Automated Login (Selenium)**  
   → Authenticate on the web portal

5. **Invoice Retrieval**  
   → Locate matching invoice

6. **Invoice Download (PDF)**  
   → Save invoice locally

---

## Tech Stack

- **Python 3.11**
- **FastAPI** (API layer)
- **Selenium + undetected_chromedriver**
- **pyzbar** (barcode decoding)
- **Pillow** (image processing)
- **pypdf / PyPDF2** (PDF merging)
- **python-dotenv** (environment configuration)

---

## Project Structure

receipt-to-invoice-automation/   
│   
├── src/   
│ ├── static/   
│ │ └── web.html   
│ ├── main.py   
│ ├── autofill_Auchan.py   
│ ├── autofill_Carrefour.py   
│ ├── config.py   
│ ├── profiles_loader.py   
│ └── merge_pdf.py   
│   
├── profiles.example.json   
├── .env.example   
├── requirements.txt   
└── README.md   

---

## Setup

1. Create virtual environment
   python -m venv .venv

2. Activate environment
   source .venv/bin/activate (Mac/Linux)
   .venv\Scripts\Activate (Windows)

3. Install dependencies
   pip install -r requirements.txt

4. Profile Configuration
   create profile.json file by following the profile.example.json

5. Environment Variables
   copy .env.example → .env
   change environment variables as needed

6. Run the Application
   uvicorn src.main:app --reload
   
---

## Current Status

Prototype – Functional

✔ FastAPI upload endpoint  
✔ Barcode extraction working  
✔ Automated form filling (Auchan / Carrefour)  
✔ PDF download + merge  

---

## Possible Improvements

- Asynchronous job queue (non-blocking API)
- Better logging and monitoring
- Automatic Chrome version detection
- Docker containerization
- Unit testing for OCR + utilities
- Retry strategy improvements

---

## What This Project Demonstrates

- End-to-end automation design
- OCR integration in real workflows
- Secure configuration management
- Structured FastAPI backend
- Browser automation engineering
- Modular and reusable code architecture

---

## Author

Kevin Lin  
AI Engineer – Automation & Intelligent Systems  
