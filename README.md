# Receipt to Invoice Automation System

End-to-end automation pipeline that converts receipt photos into downloadable invoices using barcode OCR and browser automation.

---

## Overview

This project automates the process of retrieving invoices from retail web portals using receipt images.

Instead of manually logging in and searching for invoices, the system:

1. Takes one or multiple receipt photos as input
2. Extracts the barcode using OCR
3. Logs into the user’s online account via Selenium (ChromeDriver)
4. Automatically retrieves and downloads the corresponding invoice

The goal is to reduce manual effort and demonstrate a real-world automation workflow.

---

## System Architecture

Receipt Image(s)   
        ↓   
Barcode Detection (OCR)   
        ↓   
Extract Identifier   
        ↓   
Automated Login (Selenium)   
        ↓   
Invoice Retrieval   
        ↓   
Download Invoice (PDF)   

---

## Tech Stack

- Python
- OCR / Barcode extraction
- Selenium + ChromeDriver
- File handling & automation scripting

---

## Features

- Barcode detection from receipt images
- Automated browser login
- Automated invoice retrieval
- Multi-image support
- Structured processing pipeline

---

## Project Structure

project-root/   
│   
├── main.py   
├── ocr_module.py   
├── automation_module.py   
├── utils.py   
├── requirements.txt   
└── README.md   


---

## Current Status

Prototype – Work in Progress

✔ Core pipeline implemented  
✔ Barcode reading functional  
✔ Automated invoice retrieval working  

Next Improvements:
- Improve error handling
- Add logging system
- Add configuration file (.env support)
- Dockerize the project
- Add API wrapper (FastAPI)

---

## Security & Privacy

This project is a public technical demonstration.

- No real credentials are stored in the repository
- No private or commercial code is included
- Users must provide their own credentials locally

---

## Why This Project Matters

This project demonstrates:

- End-to-end automation thinking
- OCR integration in real workflows
- Web automation using Selenium
- Pipeline structuring and modular code design

---

## Future Roadmap

- Add structured metadata extraction
- Improve robustness against low-quality images
- Add performance benchmarks

---

## Author

Kevin Lin  
AI Engineer focused on efficient and deployable intelligent systems
