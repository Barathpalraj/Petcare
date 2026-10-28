# Smart Veterinary Clinic & Pet Hospital Management System

A full-stack, responsive, and animated Pet Hospital Management System built with **Flask**, **SQLite**, **Anime.js**, **Chart.js**, and modern CSS.

Designed for comprehensive animal healthcare operations, encompassing outpatient triage, inpatient admissions, electronic health records (EHR), preventative immunizations, surgical scheduling, digital prescriptions, pharmacy inventory, and billing.

---

## Features Matrix

### 1. Multi-Role Authentication & Access Control
- **Executive Admin**: Financial reporting, analytics, staff and doctor roster administration, system settings.
- **Veterinary Doctor**: Clinical consultation queue, patient examination triage, vital sign recording, digital prescription generation, treatment regimens.
- **Reception & Front Desk**: Client onboarding, pet patient admissions, appointment check-ins, invoice settlement, and payment collection.
- **Public Portal**: Hospital overview, clinical departments, board-certified vet profiles, and 24/7 emergency dispatch contact.

### 2. Patient & Client Electronic Health Records (EHR)
- Complete pet profiling: species, breed, gender, age, weight, coat markings, 15-digit RFID microchip tags, and high-visibility allergy warnings.
- Photo upload handling with live client-side image preview.
- Complete chronological medical history, diagnosis logs, and immunization records per patient.

### 3. Preventative Immunization & Vaccine Passport
- Automated calculation of booster deadlines based on vaccine protocols (Rabies 1-Yr, Rabies 3-Yr, DHPP 5-in-1, FVRCP, Bordetella).
- Compliance status tracking: **Up to Date**, **Due Soon**, and **Overdue**.
- Complete historical vaccine administration audit trail.

### 4. Doctor Clinical Consultations & Prescriptions
- Patient vital signs logging: Body Temperature (°C), Heart Rate (bpm), Respiration Rate (rpm), and Weight (kg).
- Integrated prescription builder with dynamic line item addition for drug name, dosage, frequency, and duration.
- Printable prescription slips.

### 5. Pharmacy Dispensary & Inventory Control
- Pharmacological formulary categorized by drug class (Antibiotics, NSAIDs, Parasiticides, Biologics, Corticosteroids).
- Reorder safety levels with automatic low-stock warnings.
- Supplier and pharmaceutical distributor registry.

### 6. Billing, Invoices & Financial Ledger
- Dynamic real-time invoice builder calculating subtotal, customizable sales tax (%), and promotional discounts.
- Printable A4 hospital invoice layout with clinic letterhead.
- Multi-channel payment recording: Cash, Credit/Debit Card, Online Transfer, and Pet Insurance claims.

### 7. Interactive Analytics & Animated UI
- **Anime.js** micro-interactions: staggered entrance animations, KPI counters, toast slide-outs, button shakes on validation errors.
- **Chart.js** data visualizations: species demographic breakdown, appointment status distribution, and pharmacy category distribution.

---

## Directory Structure

```
Smart-Veterinary-Clinic/
├── app.py                     # Core Flask application, routing, auth & DB helpers
├── config.py                  # Application settings, clinic info & file upload rules
├── requirements.txt           # Dependencies (Flask, Werkzeug)
├── README.md                  # System documentation
│
├── database/
│   ├── pet_clinic.sql         # Database schema & sample seed data
│   └── pet_clinic.db          # Auto-initialized SQLite database
│
├── templates/                 # 43 Jinja2 HTML Templates
│   ├── base.html              # Master layout with responsive sidebar & toasts
│   ├── index.html, about.html, services.html, doctors.html, contact.html
│   ├── login.html             # Split-screen auth with 1-click demo logins
│   ├── admin_dashboard.html, staff_dashboard.html, doctor_dashboard.html
│   ├── pets.html, add_pet.html, edit_pet.html, pet_details.html
│   ├── owners.html, add_owner.html, owner_details.html
│   ├── doctors_manage.html, staff_manage.html, users.html
│   ├── appointments.html, add_appointment.html, appointment_details.html
│   ├── consultation.html, diagnosis.html, treatment.html, medical_records.html, prescriptions.html
│   ├── vaccinations.html, add_vaccination.html, vaccination_history.html
│   ├── medicines.html, add_medicine.html, medicine_stock.html, suppliers.html
│   ├── bills.html, create_bill.html, invoice.html, payments.html
│   └── notifications.html, reports.html, analytics.html, settings.html
│
├── static/
│   ├── css/                   # Modular stylesheets (style, dashboard, forms, tables, login, responsive)
│   ├── js/                    # Micro-animations, live calculations & validation
│   └── images/                # Branding assets & placeholders
│
└── uploads/
    └── pet_photos/            # Uploaded pet profile photos
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

> **Note:** The SQLite database (`database/pet_clinic.db`) is automatically initialized and seeded from `database/pet_clinic.sql` on the first run. No manual database setup is required.

---

## Demo Credentials

You can use the 1-click demo chips on the login page (`/login`) or sign in manually with:

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full clinical, financial, and executive access |
| **Doctor** | `doctor` | `doctor123` | Consultations, medical charts, prescriptions |
| **Staff** | `staff` | `staff123` | Client registration, admissions, billing checkout |

---

## License
MIT License. Built for Smart Veterinary Hospitals.
