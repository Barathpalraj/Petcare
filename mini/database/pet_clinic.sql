-- ==========================================================
-- Smart Veterinary Clinic Database Schema
-- Database: pet_clinic
-- Compatible with SQLite and MySQL
-- ==========================================================

PRAGMA foreign_keys = ON;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'staff', -- 'admin', 'doctor', 'staff'
    phone VARCHAR(30),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Owners Table
CREATE TABLE IF NOT EXISTS owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(30) NOT NULL,
    address TEXT,
    city VARCHAR(80),
    emergency_contact VARCHAR(80),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Pets Table
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    name VARCHAR(80) NOT NULL,
    species VARCHAR(50) NOT NULL, -- Dog, Cat, Bird, Rabbit, Reptile, etc.
    breed VARCHAR(80),
    gender VARCHAR(10) DEFAULT 'Unknown', -- Male, Female, Neutered Male, Spayed Female
    date_of_birth DATE,
    age_years INTEGER DEFAULT 0,
    weight REAL DEFAULT 0.0, -- in kg
    color VARCHAR(50),
    microchip_id VARCHAR(100),
    photo VARCHAR(255) DEFAULT 'default_pet.png',
    allergies TEXT,
    medical_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES owners (id) ON DELETE CASCADE
);

-- 4. Doctors Profile Table
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    specialization VARCHAR(120) NOT NULL,
    license_number VARCHAR(80) NOT NULL,
    consultation_fee REAL DEFAULT 50.00,
    experience_years INTEGER DEFAULT 5,
    bio TEXT,
    schedule_days VARCHAR(100) DEFAULT 'Mon,Tue,Wed,Thu,Fri',
    schedule_hours VARCHAR(100) DEFAULT '09:00 AM - 05:00 PM',
    photo VARCHAR(255) DEFAULT 'doctor.jpg',
    available INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 5. Appointments Table
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time VARCHAR(20) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'in_progress', 'completed', 'cancelled'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES owners (id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE
);

-- 6. Medical Records / Consultations Table
CREATE TABLE IF NOT EXISTS medical_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_id INTEGER,
    record_date DATE DEFAULT (DATE('now')),
    symptoms TEXT,
    diagnosis TEXT,
    temperature REAL, -- Celsius
    heart_rate INTEGER, -- bpm
    respiratory_rate INTEGER, -- breaths/min
    weight REAL, -- kg
    treatment_plan TEXT,
    dietary_notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments (id) ON DELETE SET NULL
);

-- 7. Prescriptions Table
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medical_record_id INTEGER,
    pet_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    prescription_date DATE DEFAULT (DATE('now')),
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medical_record_id) REFERENCES medical_records (id) ON DELETE SET NULL,
    FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors (id) ON DELETE CASCADE
);

-- 8. Prescription Line Items
CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    medicine_name VARCHAR(120) NOT NULL,
    dosage VARCHAR(80) NOT NULL,
    frequency VARCHAR(80) NOT NULL,
    duration VARCHAR(80) NOT NULL,
    notes TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions (id) ON DELETE CASCADE
);

-- 9. Vaccinations Table
CREATE TABLE IF NOT EXISTS vaccinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    vaccine_name VARCHAR(100) NOT NULL,
    administered_date DATE NOT NULL,
    next_due_date DATE NOT NULL,
    batch_number VARCHAR(50),
    veterinarian_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'up_to_date', -- 'up_to_date', 'due_soon', 'overdue'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE
);

-- 10. Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(120),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Medicines & Inventory Table
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    generic_name VARCHAR(120),
    category VARCHAR(60) NOT NULL, -- Antibiotic, Painkiller, Vaccine, Antiseptic, Vitamin, etc.
    supplier_id INTEGER,
    unit_price REAL NOT NULL DEFAULT 0.00,
    cost_price REAL DEFAULT 0.00,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    expiry_date DATE,
    unit_type VARCHAR(30) DEFAULT 'Tablets', -- Tablets, Vials, Bottles, Syringes
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL
);

-- 12. Invoices / Billing Table
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    owner_id INTEGER NOT NULL,
    pet_id INTEGER NOT NULL,
    appointment_id INTEGER,
    invoice_date DATE DEFAULT (DATE('now')),
    subtotal REAL NOT NULL DEFAULT 0.00,
    tax_amount REAL NOT NULL DEFAULT 0.00,
    discount_amount REAL DEFAULT 0.00,
    total_amount REAL NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- 'paid', 'unpaid', 'partial'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES owners (id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments (id) ON DELETE SET NULL
);

-- 13. Invoice Items Table
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    description VARCHAR(200) NOT NULL,
    item_type VARCHAR(50) DEFAULT 'service', -- 'consultation', 'medicine', 'vaccine', 'treatment', 'service'
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL DEFAULT 0.00,
    total_price REAL NOT NULL DEFAULT 0.00,
    FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
);

-- 14. Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount REAL NOT NULL,
    payment_method VARCHAR(30) NOT NULL DEFAULT 'cash', -- 'cash', 'card', 'online', 'insurance'
    transaction_ref VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
);

-- 15. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(30) DEFAULT 'system', -- 'appointment', 'vaccination', 'stock', 'billing', 'system'
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================
-- Initial Seed Data
-- ==========================================================

-- Insert Users (Password is 'admin123', 'doctor123', 'staff123' respectively hashed or plain fallback)
INSERT OR IGNORE INTO users (id, username, email, password_hash, full_name, role, phone) VALUES
(1, 'admin', 'admin@vetclinic.com', 'scrypt:32768:8:1$pGg2P35hY6K1dM1o$3ce84fb12b508fec2db87d7b2db84e6012351ab669a74421bda078e6e5a61fc04f44760cae803d36e885d5ce6dfdf9bb4a9d7cefc99d0e149f1a26d7f9b8098c', 'Dr. Sarah Jenkins (Chief Admin)', 'admin', '+1 (555) 019-2831'),
(2, 'doctor', 'doctor@vetclinic.com', 'scrypt:32768:8:1$pGg2P35hY6K1dM1o$3ce84fb12b508fec2db87d7b2db84e6012351ab669a74421bda078e6e5a61fc04f44760cae803d36e885d5ce6dfdf9bb4a9d7cefc99d0e149f1a26d7f9b8098c', 'Dr. Alex Rivera (Senior Vet)', 'doctor', '+1 (555) 019-5482'),
(3, 'staff', 'staff@vetclinic.com', 'scrypt:32768:8:1$pGg2P35hY6K1dM1o$3ce84fb12b508fec2db87d7b2db84e6012351ab669a74421bda078e6e5a61fc04f44760cae803d36e885d5ce6dfdf9bb4a9d7cefc99d0e149f1a26d7f9b8098c', 'Emily Watson (Reception)', 'staff', '+1 (555) 019-9912');

-- Insert Doctors Profile
INSERT OR IGNORE INTO doctors (id, user_id, specialization, license_number, consultation_fee, experience_years, bio, schedule_days, schedule_hours) VALUES
(1, 1, 'Chief Surgeon & Feline Specialist', 'VET-CA-9921', 65.00, 12, 'Dr. Jenkins has over 12 years of clinical excellence specializing in feline and canine internal medicine and soft-tissue surgery.', 'Mon,Tue,Wed,Thu,Fri', '08:30 AM - 04:30 PM'),
(2, 2, 'Canine Orthopedics & General Care', 'VET-CA-8840', 55.00, 8, 'Dr. Rivera is dedicated to comprehensive pet wellness, preventive treatments, and advanced canine orthopedic therapies.', 'Mon,Wed,Thu,Fri,Sat', '09:00 AM - 05:00 PM');

-- Insert Suppliers
INSERT OR IGNORE INTO suppliers (id, name, contact_person, phone, email, address) VALUES
(1, 'Zoetis Animal Health Logistics', 'Marcus Vance', '+1 (800) 366-5288', 'orders@zoetis-vet.com', '100 Campus Dr, Florham Park, NJ'),
(2, 'Boehringer Ingelheim Vet Supplies', 'Clara Hughes', '+1 (800) 325-9167', 'sales@boehringer-vet.com', '3239 Satellite Blvd, Duluth, GA'),
(3, 'Covetrus Global Pharmaceuticals', 'David Kim', '+1 (888) 280-2221', 'support@covetrus.com', '7000 Cardinal Pl, Dublin, OH');

-- Insert Medicines
INSERT OR IGNORE INTO medicines (id, name, generic_name, category, supplier_id, unit_price, cost_price, stock_quantity, min_stock_level, expiry_date, unit_type, description) VALUES
(1, 'Amoxicillin 250mg', 'Amoxicillin Trihydrate', 'Antibiotic', 1, 14.50, 7.20, 150, 25, '2027-11-30', 'Tablets', 'Broad spectrum bacterial antibiotic for canines and felines.'),
(2, 'Rimadyl 75mg', 'Carprofen', 'Painkiller / NSAID', 1, 28.00, 15.00, 80, 20, '2027-08-15', 'Chewables', 'Non-steroidal anti-inflammatory for joint pain and post-op relief.'),
(3, 'NexGard Spectra', 'Afoxolaner & Milbemycin Oxime', 'Parasiticide', 2, 35.00, 21.00, 45, 15, '2028-01-20', 'Chewables', 'Comprehensive flea, tick, and worm treatment for dogs.'),
(4, 'Nobivac Rabies 1-Yr', 'Inactivated Rabies Virus', 'Vaccine', 3, 22.00, 9.50, 60, 20, '2027-05-10', 'Vials', 'Annual preventive rabies vaccine for dogs and cats.'),
(5, 'Prednisolone 5mg', 'Prednisolone', 'Corticosteroid', 3, 12.00, 5.00, 12, 15, '2026-12-01', 'Tablets', 'Anti-inflammatory and immunosuppressive medication (Low Stock).');

-- Insert Owners
INSERT OR IGNORE INTO owners (id, name, email, phone, address, city, emergency_contact, notes) VALUES
(1, 'Jessica Miller', 'jessica.m@gmail.com', '+1 (555) 234-8891', '124 Blossom Hill Rd', 'Springfield', '+1 (555) 991-0021', 'Very prompt, prefers morning slots.'),
(2, 'Robert Downey', 'robert.d@outlook.com', '+1 (555) 456-1123', '88 Maple Grove Ave', 'Springfield', '+1 (555) 887-2234', 'Owner of two Golden Retrievers.'),
(3, 'Sophia Chen', 'sophia.c@techmail.com', '+1 (555) 789-9944', '502 Pinehurst Blvd', 'Springfield', '+1 (555) 667-3341', 'Allergic to specific cat dander shampoos.');

-- Insert Pets
INSERT OR IGNORE INTO pets (id, owner_id, name, species, breed, gender, date_of_birth, age_years, weight, color, microchip_id, photo, allergies, medical_notes) VALUES
(1, 1, 'Bella', 'Dog', 'Golden Retriever', 'Female', '2022-04-15', 3, 28.5, 'Golden Cream', '985141001294821', 'dog.png', 'None reported', 'Mild seasonal ear itching, otherwise very healthy.'),
(2, 2, 'Oliver', 'Cat', 'British Shorthair', 'Male', '2021-08-20', 4, 5.2, 'Blue Grey', '985141009831722', 'cat.png', 'Sensitive to poultry proteins', 'Indoor cat, up to date on vaccines.'),
(3, 3, 'Rocky', 'Dog', 'German Shepherd', 'Neutered Male', '2020-01-10', 5, 34.0, 'Black & Tan', '985141006543211', 'dog.png', 'Penicillin sensitivity', 'Undergoing hip joint supplement therapy.');

-- Insert Appointments
INSERT OR IGNORE INTO appointments (id, pet_id, owner_id, doctor_id, appointment_date, appointment_time, reason, status, notes) VALUES
(1, 1, 1, 1, DATE('now'), '10:00 AM', 'Routine Annual Wellness Checkup & Rabies Booster', 'scheduled', 'Owner requested weight monitoring check.'),
(2, 2, 2, 2, DATE('now'), '11:30 AM', 'Lethargy and mild vomiting since yesterday evening', 'in_progress', 'Priority patient for abdominal palpation.'),
(3, 3, 3, 1, DATE('now', '+1 day'), '02:15 PM', 'Orthopedic Follow-up & Joint Mobility Assessment', 'scheduled', 'Reviewing response to Rimadyl therapy.');

-- Insert Medical Records
INSERT OR IGNORE INTO medical_records (id, pet_id, doctor_id, appointment_id, record_date, symptoms, diagnosis, temperature, heart_rate, respiratory_rate, weight, treatment_plan, follow_up_date) VALUES
(1, 1, 1, 1, DATE('now', '-30 days'), 'Slight head shaking, brownish ear discharge', 'Mild Otitis Externa (Bacterial)', 38.6, 92, 24, 28.2, 'Clean ears thoroughly. Administer topical antifungal/antibacterial drops for 10 days.', DATE('now', '+10 days'));

-- Insert Vaccinations
INSERT OR IGNORE INTO vaccinations (id, pet_id, vaccine_name, administered_date, next_due_date, batch_number, veterinarian_name, status, notes) VALUES
(1, 1, 'DHPP (Distemper, Parvo)', DATE('now', '-11 months'), DATE('now', '+1 month'), 'B-9982-A', 'Dr. Sarah Jenkins', 'due_soon', 'Annual booster due next month.'),
(2, 2, 'FVRCP (Feline Viral Rhinotracheitis)', DATE('now', '-6 months'), DATE('now', '+6 months'), 'F-4412-C', 'Dr. Alex Rivera', 'up_to_date', 'Administered without any adverse reactions.'),
(3, 3, 'Rabies (3-Year)', DATE('now', '-37 months'), DATE('now', '-1 month'), 'R-1102-Z', 'Dr. Sarah Jenkins', 'overdue', 'Overdue for Rabies vaccination booster.');

-- Insert Invoices
INSERT OR IGNORE INTO invoices (id, invoice_number, owner_id, pet_id, appointment_id, invoice_date, subtotal, tax_amount, discount_amount, total_amount, payment_status, notes) VALUES
(1, 'INV-2026-001', 1, 1, 1, DATE('now'), 93.00, 7.44, 0.00, 100.44, 'paid', 'Wellness check and medication paid in full via Credit Card.'),
(2, 'INV-2026-002', 2, 2, 2, DATE('now'), 85.00, 6.80, 5.00, 86.80, 'unpaid', 'Consultation and lab tests pending owner settlement.');

-- Insert Invoice Items
INSERT OR IGNORE INTO invoice_items (id, invoice_id, description, item_type, quantity, unit_price, total_price) VALUES
(1, 1, 'Comprehensive Doctor Consultation', 'consultation', 1, 65.00, 65.00),
(2, 1, 'Amoxicillin 250mg (Course)', 'medicine', 2, 14.00, 28.00),
(3, 2, 'Urgent Triage Consultation', 'consultation', 1, 55.00, 55.00),
(4, 2, 'Rimadyl 75mg Chewables', 'medicine', 1, 30.00, 30.00);

-- Insert Payments
INSERT OR IGNORE INTO payments (id, invoice_id, amount, payment_method, transaction_ref, notes) VALUES
(1, 1, 100.44, 'card', 'TXN-99812401', 'Visa ending in 4102');

-- Insert Notifications
INSERT OR IGNORE INTO notifications (id, title, message, type, is_read) VALUES
(1, 'Low Medicine Stock Alert', 'Prednisolone 5mg has only 12 tablets remaining (below threshold 15).', 'stock', 0),
(2, 'Vaccination Booster Overdue', 'Rocky (Owner: Sophia Chen) is overdue for Rabies vaccine.', 'vaccination', 0),
(3, 'Today''s Appointment Queue', 'You have 3 patient appointments scheduled for today.', 'appointment', 0);
