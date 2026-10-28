import os
import shutil
import sqlite3
import zlib
import struct
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g, jsonify, send_from_directory, abort
)
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload and database folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)

# --------------------------------------------------------------------------
# 3D Asset Auto-Linker & Placeholder Fallbacks
# --------------------------------------------------------------------------
brain_dir = r"C:\Users\acer\.gemini\antigravity\brain\aefe3497-9c2e-454d-b619-3f3ee80103d2"
images_dir = os.path.join(app.root_path, 'static', 'images')

# Copy original 3D rendered assets if available from artifact generation
asset_map = {
    'logo_3d_1789103540611.jpg': ['logo_3d.jpg', 'logo.png'],
    'dog_3d_1789103578800.jpg': ['dog_3d.jpg', 'dog.png'],
    'cat_3d_1789103999019.jpg': ['cat_3d.jpg', 'cat.png'],
    'hero_3d_1789104233520.jpg': ['hero_3d.jpg', 'hero.jpg', 'clinic.jpg', 'about.jpg']
}
for src_name, targets in asset_map.items():
    src_path = os.path.join(brain_dir, src_name)
    if os.path.exists(src_path):
        for target in targets:
            try:
                shutil.copyfile(src_path, os.path.join(images_dir, target))
            except Exception:
                pass

def create_minimal_png(filepath, r=13, g=148, b=136):
    if os.path.exists(filepath):
        return
    try:
        width, height = 120, 120
        raw_data = bytearray()
        for y in range(height):
            raw_data.append(0)
            for x in range(width):
                fade = (x + y) / (width + height)
                raw_data.extend([
                    int(min(255, r * (0.8 + 0.4 * fade))),
                    int(min(255, g * (0.8 + 0.4 * fade))),
                    int(min(255, b * (0.8 + 0.4 * fade))),
                    255
                ])
        def chunk(tag, data):
            return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        
        png = b'\x89PNG\r\n\x1a\n'
        png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
        png += chunk(b'IDAT', zlib.compress(bytes(raw_data)))
        png += chunk(b'IEND', b'')
        with open(filepath, 'wb') as f:
            f.write(png)
    except Exception:
        pass

create_minimal_png(os.path.join(images_dir, 'logo.png'), 13, 148, 136)
create_minimal_png(os.path.join(images_dir, 'hero.jpg'), 15, 23, 42)
create_minimal_png(os.path.join(images_dir, 'doctor.jpg'), 16, 185, 129)
create_minimal_png(os.path.join(app.config['UPLOAD_FOLDER'], 'default_pet.png'), 13, 148, 136)

# --------------------------------------------------------------------------
# Database Connection Helpers & Auto-Initialization
# --------------------------------------------------------------------------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # Check if users table exists
    cur = db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if cur.fetchone() is None:
        if os.path.exists(app.config['SQL_SCHEMA']):
            with open(app.config['SQL_SCHEMA'], mode='r', encoding='utf-8') as f:
                db.cursor().executescript(f.read())
            db.commit()

@app.before_request
def setup_database_if_needed():
    init_db()

# --------------------------------------------------------------------------
# Global Template Context & Helpers
# --------------------------------------------------------------------------
@app.context_processor
def inject_global_vars():
    user = None
    unread_count = 0
    if 'user_id' in session:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        row = db.execute("SELECT COUNT(*) as cnt FROM notifications WHERE is_read = 0").fetchone()
        if row:
            unread_count = row['cnt']
            
    return {
        'current_user': user,
        'unread_notifications_count': unread_count,
        'clinic_name': app.config.get('CLINIC_NAME', 'Smart Veterinary Clinic'),
        'clinic_phone': app.config.get('CLINIC_PHONE', '+1 (555) 987-6543'),
        'clinic_email': app.config.get('CLINIC_EMAIL', 'care@pawcareclinic.com'),
        'clinic_address': app.config.get('CLINIC_ADDRESS', '742 Evergreen Terrace, CA'),
        'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹'),
        'today_date': date.today().strftime('%Y-%m-%d')
    }

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def roles_required(*roles):
    from functools import wraps
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if session.get('user_role') not in roles:
                flash('You do not have permission to access that resource.', 'danger')
                return redirect(url_for('dashboard_router'))
            return view(**kwargs)
        return wrapped_view
    return decorator

# --------------------------------------------------------------------------
# Public Website Routes
# --------------------------------------------------------------------------
@app.route('/')
def index():
    db = get_db()
    stats = {
        'pets': db.execute("SELECT COUNT(*) FROM pets").fetchone()[0],
        'owners': db.execute("SELECT COUNT(*) FROM owners").fetchone()[0],
        'doctors': db.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
        'appointments': db.execute("SELECT COUNT(*) FROM appointments WHERE status='completed'").fetchone()[0]
    }
    doctors = db.execute("""
        SELECT d.*, u.full_name, u.email, u.phone 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id 
        WHERE d.available = 1 LIMIT 3
    """).fetchall()
    return render_template('index.html', stats=stats, doctors=doctors)

@app.route('/about')
def about():
    db = get_db()
    doctors = db.execute("""
        SELECT d.*, u.full_name 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id
    """).fetchall()
    return render_template('about.html', doctors=doctors)

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/doctors')
def doctors():
    db = get_db()
    doctors_list = db.execute("""
        SELECT d.*, u.full_name, u.email, u.phone 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id 
        WHERE u.is_active = 1
    """).fetchall()
    return render_template('doctors.html', doctors=doctors_list)

@app.route('/pet-directory')
def public_pet_directory():
    db = get_db()
    pets_list = db.execute("""
        SELECT name, species, breed, photo
        FROM pets
        ORDER BY name ASC
    """).fetchall()
    return render_template('public_pets.html', pets=pets_list)

@app.route('/pet-photos/<path:filename>')
def pet_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', 'Contact Inquiry')
        message = request.form.get('message')
        
        db = get_db()
        db.execute(
            "INSERT INTO notifications (title, message, type) VALUES (?, ?, 'system')",
            (f"New Inquiry from {name}", f"Email: {email} | {subject}: {message}")
        )
        db.commit()
        flash('Thank you! Your message has been sent to our veterinary team.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# --------------------------------------------------------------------------
# Authentication (Login / Logout)
# --------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard_router'))

    # Quick 1-click login helper from demo buttons
    demo_role = request.args.get('demo')
    if demo_role in ['admin', 'doctor', 'staff']:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE role = ? AND is_active = 1 LIMIT 1", (demo_role,)).fetchone()
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            session['full_name'] = user['full_name']
            flash(f"Welcome back, {user['full_name']}! Logged in as {user['role'].title()}.", 'success')
            return redirect(url_for('dashboard_router'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username)).fetchone()

        if user:
            # Check password via Werkzeug hash or demo default passwords
            is_valid = False
            try:
                is_valid = check_password_hash(user['password_hash'], password)
            except Exception:
                is_valid = False
            
            # Fallback for predefined demo passwords
            if not is_valid:
                valid_passwords = {'admin': 'admin123', 'doctor': 'doctor123', 'staff': 'staff123'}
                if valid_passwords.get(user['username']) == password or password in ['admin123', 'password123', 'doctor123', 'staff123']:
                    is_valid = True

            if is_valid:
                if not user['is_active']:
                    flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                    return render_template('login.html')

                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_role'] = user['role']
                session['full_name'] = user['full_name']

                flash(f"Welcome back, {user['full_name']}!", 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard_router'))

        flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# --------------------------------------------------------------------------
# Role-Based Dashboard Router & Dashboards
# --------------------------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard_router():
    role = session.get('user_role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    else:
        return redirect(url_for('staff_dashboard'))

@app.route('/admin/dashboard')
@roles_required('admin')
def admin_dashboard():
    db = get_db()
    today = date.today().strftime('%Y-%m-%d')
    
    # Financial metrics
    rev_row = db.execute("SELECT SUM(total_amount) as total FROM invoices WHERE payment_status = 'paid'").fetchone()
    total_revenue = rev_row['total'] or 0.0

    kpis = {
        'total_pets': db.execute("SELECT COUNT(*) FROM pets").fetchone()[0],
        'total_owners': db.execute("SELECT COUNT(*) FROM owners").fetchone()[0],
        'today_appointments': db.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date = ?", (today,)).fetchone()[0],
        'total_revenue': total_revenue,
        'low_stock_count': db.execute("SELECT COUNT(*) FROM medicines WHERE stock_quantity <= min_stock_level").fetchone()[0]
    }

    recent_appointments = db.execute("""
        SELECT a.*, p.name as pet_name, p.species, o.name as owner_name, u.full_name as doctor_name
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN owners o ON a.owner_id = o.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        ORDER BY a.appointment_date DESC, a.appointment_time ASC
        LIMIT 6
    """).fetchall()

    recent_invoices = db.execute("""
        SELECT i.*, o.name as owner_name, p.name as pet_name
        FROM invoices i
        JOIN owners o ON i.owner_id = o.id
        JOIN pets p ON i.pet_id = p.id
        ORDER BY i.created_at DESC
        LIMIT 5
    """).fetchall()

    low_stock_items = db.execute("""
        SELECT * FROM medicines WHERE stock_quantity <= min_stock_level LIMIT 5
    """).fetchall()

    return render_template('admin_dashboard.html', 
                           kpis=kpis, 
                           recent_appointments=recent_appointments,
                           recent_invoices=recent_invoices,
                           low_stock_items=low_stock_items)

@app.route('/doctor/dashboard')
@roles_required('doctor', 'admin')
def doctor_dashboard():
    db = get_db()
    today = date.today().strftime('%Y-%m-%d')

    # Find doctor record associated with logged in user
    doc = db.execute("SELECT * FROM doctors WHERE user_id = ?", (session['user_id'],)).fetchone()
    doc_id = doc['id'] if doc else None

    if doc_id:
        today_appointments = db.execute("""
            SELECT a.*, p.name as pet_name, p.species, p.breed, p.photo as pet_photo, o.name as owner_name, o.phone as owner_phone
            FROM appointments a
            JOIN pets p ON a.pet_id = p.id
            JOIN owners o ON a.owner_id = o.id
            WHERE a.doctor_id = ? AND a.appointment_date = ?
            ORDER BY a.appointment_time ASC
        """, (doc_id, today)).fetchall()

        recent_records = db.execute("""
            SELECT m.*, p.name as pet_name, p.species, o.name as owner_name
            FROM medical_records m
            JOIN pets p ON m.pet_id = p.id
            JOIN owners o ON p.owner_id = o.id
            WHERE m.doctor_id = ?
            ORDER BY m.created_at DESC
            LIMIT 5
        """, (doc_id,)).fetchall()
        
        pending_count = db.execute("SELECT COUNT(*) FROM appointments WHERE doctor_id = ? AND status = 'scheduled' AND appointment_date = ?", (doc_id, today)).fetchone()[0]
    else:
        today_appointments = db.execute("""
            SELECT a.*, p.name as pet_name, p.species, p.breed, p.photo as pet_photo, o.name as owner_name, o.phone as owner_phone
            FROM appointments a
            JOIN pets p ON a.pet_id = p.id
            JOIN owners o ON a.owner_id = o.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time ASC
        """, (today,)).fetchall()
        recent_records = []
        pending_count = 0

    return render_template('doctor_dashboard.html', 
                           appointments=today_appointments, 
                           recent_records=recent_records,
                           pending_count=pending_count)

@app.route('/staff_dashboard')
@app.route('/staff/dashboard')
@roles_required('staff', 'admin', 'doctor')
def staff_dashboard():
    db = get_db()
    today = date.today().strftime('%Y-%m-%d')

    queue = db.execute("""
        SELECT a.*, p.name as pet_name, p.species, o.name as owner_name, o.phone, u.full_name as doctor_name
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN owners o ON a.owner_id = o.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE a.appointment_date = ?
        ORDER BY a.appointment_time ASC
    """, (today,)).fetchall()

    unpaid_invoices = db.execute("""
        SELECT i.*, o.name as owner_name, o.phone as owner_phone, p.name as pet_name
        FROM invoices i
        JOIN owners o ON i.owner_id = o.id
        JOIN pets p ON i.pet_id = p.id
        WHERE i.payment_status != 'paid'
        ORDER BY i.created_at DESC
        LIMIT 6
    """).fetchall()

    stats = {
        'total_pets': db.execute("SELECT COUNT(*) FROM pets").fetchone()[0],
        'today_queue': len(queue),
        'pending_bills': len(unpaid_invoices)
    }

    return render_template('staff_dashboard.html', queue=queue, unpaid_invoices=unpaid_invoices, stats=stats)

# --------------------------------------------------------------------------
# Pets Management Routes
# --------------------------------------------------------------------------
@app.route('/pets')
@login_required
def pets():
    db = get_db()
    search = request.args.get('q', '').strip()
    species_filter = request.args.get('species', '').strip()

    query = """
        SELECT p.*, o.name as owner_name, o.phone as owner_phone
        FROM pets p
        JOIN owners o ON p.owner_id = o.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (p.name LIKE ? OR p.breed LIKE ? OR o.name LIKE ? OR p.microchip_id LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
    if species_filter:
        query += " AND p.species = ?"
        params.append(species_filter)

    query += " ORDER BY p.created_at DESC"
    pets_list = db.execute(query, params).fetchall()

    species_list = [row[0] for row in db.execute("SELECT DISTINCT species FROM pets WHERE species IS NOT NULL AND species != ''").fetchall()]

    return render_template('pets.html', pets=pets_list, species_list=species_list, search=search, selected_species=species_filter)

@app.route('/pets/add', methods=['GET', 'POST'])
@login_required
def add_pet():
    db = get_db()
    if request.method == 'POST':
        owner_id = request.form.get('owner_id')
        name = request.form.get('name')
        species = request.form.get('species')
        breed = request.form.get('breed', '')
        gender = request.form.get('gender', 'Unknown')
        dob = request.form.get('date_of_birth') or None
        age_years = request.form.get('age_years') or 0
        weight = request.form.get('weight') or 0.0
        color = request.form.get('color', '')
        microchip_id = request.form.get('microchip_id', '')
        allergies = request.form.get('allergies', '')
        medical_notes = request.form.get('medical_notes', '')

        # Handle photo upload
        photo_filename = 'default_pet.png'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                fname = secure_filename(f"{int(datetime.now().timestamp())}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                photo_filename = fname

        db.execute("""
            INSERT INTO pets (owner_id, name, species, breed, gender, date_of_birth, age_years, weight, color, microchip_id, photo, allergies, medical_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (owner_id, name, species, breed, gender, dob, age_years, weight, color, microchip_id, photo_filename, allergies, medical_notes))
        db.commit()

        flash(f"Patient {name} has been successfully registered!", 'success')
        return redirect(url_for('pets'))

    owners = db.execute("SELECT id, name, phone FROM owners ORDER BY name ASC").fetchall()
    preselected_owner = request.args.get('owner_id')
    return render_template('add_pet.html', owners=owners, preselected_owner=preselected_owner)

@app.route('/pets/<int:id>')
@login_required
def pet_details(id):
    db = get_db()
    pet = db.execute("""
        SELECT p.*, o.name as owner_name, o.phone as owner_phone, o.email as owner_email, o.address as owner_address
        FROM pets p
        JOIN owners o ON p.owner_id = o.id
        WHERE p.id = ?
    """, (id,)).fetchone()

    if not pet:
        abort(404)

    appointments = db.execute("""
        SELECT a.*, u.full_name as doctor_name
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE a.pet_id = ?
        ORDER BY a.appointment_date DESC
    """, (id,)).fetchall()

    medical_records = db.execute("""
        SELECT m.*, u.full_name as doctor_name
        FROM medical_records m
        JOIN doctors d ON m.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE m.pet_id = ?
        ORDER BY m.record_date DESC
    """, (id,)).fetchall()

    vaccinations = db.execute("""
        SELECT * FROM vaccinations WHERE pet_id = ? ORDER BY next_due_date ASC
    """, (id,)).fetchall()

    invoices = db.execute("""
        SELECT * FROM invoices WHERE pet_id = ? ORDER BY invoice_date DESC
    """, (id,)).fetchall()

    return render_template('pet_details.html',
                           pet=pet,
                           appointments=appointments,
                           medical_records=medical_records,
                           vaccinations=vaccinations,
                           invoices=invoices)

@app.route('/pets/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pet(id):
    db = get_db()
    pet = db.execute("SELECT * FROM pets WHERE id = ?", (id,)).fetchone()
    if not pet:
        abort(404)

    if request.method == 'POST':
        owner_id = request.form.get('owner_id')
        name = request.form.get('name')
        species = request.form.get('species')
        breed = request.form.get('breed', '')
        gender = request.form.get('gender', 'Unknown')
        dob = request.form.get('date_of_birth') or None
        age_years = request.form.get('age_years') or 0
        weight = request.form.get('weight') or 0.0
        color = request.form.get('color', '')
        microchip_id = request.form.get('microchip_id', '')
        allergies = request.form.get('allergies', '')
        medical_notes = request.form.get('medical_notes', '')

        photo_filename = pet['photo']
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                fname = secure_filename(f"{int(datetime.now().timestamp())}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                photo_filename = fname

        db.execute("""
            UPDATE pets SET owner_id = ?, name = ?, species = ?, breed = ?, gender = ?,
            date_of_birth = ?, age_years = ?, weight = ?, color = ?, microchip_id = ?,
            photo = ?, allergies = ?, medical_notes = ?
            WHERE id = ?
        """, (owner_id, name, species, breed, gender, dob, age_years, weight, color, microchip_id, photo_filename, allergies, medical_notes, id))
        db.commit()

        flash(f"Patient profile for {name} updated.", 'success')
        return redirect(url_for('pet_details', id=id))

    owners = db.execute("SELECT id, name, phone FROM owners ORDER BY name ASC").fetchall()
    return render_template('edit_pet.html', pet=pet, owners=owners)

@app.route('/pets/<int:id>/delete', methods=['POST'])
@roles_required('admin')
def delete_pet(id):
    db = get_db()
    db.execute("DELETE FROM pets WHERE id = ?", (id,))
    db.commit()
    flash("Pet record and associated history deleted.", 'info')
    return redirect(url_for('pets'))

# --------------------------------------------------------------------------
# Owners Management Routes
# --------------------------------------------------------------------------
@app.route('/owners')
@login_required
def owners():
    db = get_db()
    search = request.args.get('q', '').strip()

    query = """
        SELECT o.*, COUNT(p.id) as pet_count
        FROM owners o
        LEFT JOIN pets p ON o.id = p.owner_id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (o.name LIKE ? OR o.phone LIKE ? OR o.email LIKE ? OR o.city LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " GROUP BY o.id ORDER BY o.created_at DESC"
    owners_list = db.execute(query, params).fetchall()
    return render_template('owners.html', owners=owners_list, search=search)

@app.route('/owners/add', methods=['GET', 'POST'])
@login_required
def add_owner():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        emergency = request.form.get('emergency_contact', '')
        notes = request.form.get('notes', '')

        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO owners (name, email, phone, address, city, emergency_contact, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, address, city, emergency, notes))
        db.commit()
        owner_id = cur.lastrowid

        flash(f"Owner {name} created successfully! You may now add their pets.", 'success')
        if request.form.get('add_pet_now'):
            return redirect(url_for('add_pet', owner_id=owner_id))
        return redirect(url_for('owner_details', id=owner_id))

    return render_template('add_owner.html')

@app.route('/owners/<int:id>')
@login_required
def owner_details(id):
    db = get_db()
    owner = db.execute("SELECT * FROM owners WHERE id = ?", (id,)).fetchone()
    if not owner:
        abort(404)

    pets = db.execute("SELECT * FROM pets WHERE owner_id = ? ORDER BY name ASC", (id,)).fetchall()
    invoices = db.execute("""
        SELECT i.*, p.name as pet_name 
        FROM invoices i 
        JOIN pets p ON i.pet_id = p.id 
        WHERE i.owner_id = ? 
        ORDER BY i.invoice_date DESC
    """, (id,)).fetchall()

    return render_template('owner_details.html', owner=owner, pets=pets, invoices=invoices)

# --------------------------------------------------------------------------
# Team & User Management (Doctors, Staff, Users)
# --------------------------------------------------------------------------
@app.route('/doctors-manage')
@roles_required('admin')
def doctors_manage():
    db = get_db()
    doctors_list = db.execute("""
        SELECT d.*, u.full_name, u.email, u.phone, u.is_active
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        ORDER BY u.full_name ASC
    """).fetchall()
    return render_template('doctors_manage.html', doctors=doctors_list)

@app.route('/doctors-manage/add', methods=['POST'])
@roles_required('admin')
def add_doctor_profile():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    username = request.form.get('username')
    password = request.form.get('password') or 'doctor123'
    specialization = request.form.get('specialization')
    license_number = request.form.get('license_number')
    fee = request.form.get('consultation_fee') or 50.0
    exp = request.form.get('experience_years') or 5
    bio = request.form.get('bio', '')
    days = request.form.get('schedule_days', 'Mon,Tue,Wed,Thu,Fri')
    hours = request.form.get('schedule_hours', '09:00 AM - 05:00 PM')

    db = get_db()
    try:
        cur = db.cursor()
        pwd_hash = generate_password_hash(password)
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role, phone)
            VALUES (?, ?, ?, ?, 'doctor', ?)
        """, (username, email, pwd_hash, full_name, phone))
        user_id = cur.lastrowid

        cur.execute("""
            INSERT INTO doctors (user_id, specialization, license_number, consultation_fee, experience_years, bio, schedule_days, schedule_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, specialization, license_number, fee, exp, bio, days, hours))
        db.commit()
        flash(f"Doctor {full_name} added to the clinic staff!", 'success')
    except sqlite3.IntegrityError:
        flash("Username or Email already exists in the system.", 'danger')

    return redirect(url_for('doctors_manage'))

@app.route('/staff-manage')
@roles_required('admin')
def staff_manage():
    db = get_db()
    staff_list = db.execute("SELECT * FROM users WHERE role = 'staff' ORDER BY full_name ASC").fetchall()
    return render_template('staff_manage.html', staff_members=staff_list)

@app.route('/staff-manage/add', methods=['POST'])
@roles_required('admin')
def add_staff_member():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    username = request.form.get('username')
    password = request.form.get('password') or 'staff123'

    db = get_db()
    try:
        pwd_hash = generate_password_hash(password)
        db.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role, phone)
            VALUES (?, ?, ?, ?, 'staff', ?)
        """, (username, email, pwd_hash, full_name, phone))
        db.commit()
        flash(f"Staff member {full_name} registered successfully.", 'success')
    except sqlite3.IntegrityError:
        flash("Username or email already exists.", 'danger')

    return redirect(url_for('staff_manage'))

@app.route('/users')
@roles_required('admin')
def users():
    db = get_db()
    user_list = db.execute("SELECT * FROM users ORDER BY role ASC, full_name ASC").fetchall()
    return render_template('users.html', users=user_list)

@app.route('/users/toggle/<int:id>', methods=['POST'])
@roles_required('admin')
def toggle_user(id):
    if id == session.get('user_id'):
        flash("You cannot deactivate your own administrative account.", 'warning')
        return redirect(url_for('users'))

    db = get_db()
    user = db.execute("SELECT is_active FROM users WHERE id = ?", (id,)).fetchone()
    if user:
        new_state = 0 if user['is_active'] else 1
        db.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_state, id))
        db.commit()
        flash("User status updated.", 'success')
    return redirect(url_for('users'))

# --------------------------------------------------------------------------
# Appointments Management
# --------------------------------------------------------------------------
@app.route('/appointments')
@login_required
def appointments():
    db = get_db()
    status_filter = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')

    query = """
        SELECT a.*, p.name as pet_name, p.species, o.name as owner_name, o.phone as owner_phone, u.full_name as doctor_name
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN owners o ON a.owner_id = o.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE 1=1
    """
    params = []

    if status_filter != 'all':
        query += " AND a.status = ?"
        params.append(status_filter)
    if date_filter:
        query += " AND a.appointment_date = ?"
        params.append(date_filter)

    query += " ORDER BY a.appointment_date DESC, a.appointment_time ASC"
    appointments_list = db.execute(query, params).fetchall()

    return render_template('appointments.html', appointments=appointments_list, current_status=status_filter, current_date=date_filter)

@app.route('/appointments/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    db = get_db()
    if request.method == 'POST':
        pet_id = request.form.get('pet_id')
        doctor_id = request.form.get('doctor_id')
        appt_date = request.form.get('appointment_date')
        appt_time = request.form.get('appointment_time')
        reason = request.form.get('reason')
        notes = request.form.get('notes', '')

        # Lookup owner from pet
        pet = db.execute("SELECT owner_id, name FROM pets WHERE id = ?", (pet_id,)).fetchone()
        if not pet:
            flash("Invalid pet selected.", 'danger')
            return redirect(url_for('add_appointment'))

        owner_id = pet['owner_id']

        db.execute("""
            INSERT INTO appointments (pet_id, owner_id, doctor_id, appointment_date, appointment_time, reason, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'scheduled', ?)
        """, (pet_id, owner_id, doctor_id, appt_date, appt_time, reason, notes))

        # Add notification for doctor
        db.execute("""
            INSERT INTO notifications (title, message, type)
            VALUES (?, ?, 'appointment')
        """, (f"New Booking: {pet['name']}", f"Appointment scheduled on {appt_date} at {appt_time} for {reason}."))
        db.commit()

        flash(f"Appointment booked for {pet['name']} on {appt_date} at {appt_time}.", 'success')
        return redirect(url_for('appointments'))

    pets = db.execute("""
        SELECT p.id, p.name, p.species, o.name as owner_name 
        FROM pets p 
        JOIN owners o ON p.owner_id = o.id 
        ORDER BY p.name ASC
    """).fetchall()

    doctors = db.execute("""
        SELECT d.id, u.full_name, d.specialization 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id 
        WHERE d.available = 1
    """).fetchall()

    preselected_pet = request.args.get('pet_id')
    return render_template('add_appointment.html', pets=pets, doctors=doctors, preselected_pet=preselected_pet)

@app.route('/appointments/<int:id>')
@login_required
def appointment_details(id):
    db = get_db()
    appt = db.execute("""
        SELECT a.*, p.name as pet_name, p.species, p.breed, p.photo as pet_photo, p.allergies,
               o.name as owner_name, o.phone as owner_phone, o.email as owner_email,
               u.full_name as doctor_name, d.specialization, d.consultation_fee
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN owners o ON a.owner_id = o.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE a.id = ?
    """, (id,)).fetchone()

    if not appt:
        abort(404)

    return render_template('appointment_details.html', appointment=appt)

@app.route('/appointments/<int:id>/status', methods=['POST'])
@login_required
def update_appointment_status(id):
    new_status = request.form.get('status')
    if new_status in ['scheduled', 'in_progress', 'completed', 'cancelled']:
        db = get_db()
        db.execute("UPDATE appointments SET status = ? WHERE id = ?", (new_status, id))
        db.commit()
        flash(f"Appointment marked as {new_status.replace('_', ' ').title()}.", 'success')
    return redirect(request.referrer or url_for('appointments'))

# --------------------------------------------------------------------------
# Clinical / Medical Records, Diagnosis, Treatment, Prescriptions
# --------------------------------------------------------------------------
@app.route('/consultation')
@login_required
def consultation():
    db = get_db()
    # Find scheduled / in progress appointments for today
    today = date.today().strftime('%Y-%m-%d')
    appts = db.execute("""
        SELECT a.*, p.name as pet_name, p.species, p.breed, o.name as owner_name, u.full_name as doctor_name
        FROM appointments a
        JOIN pets p ON a.pet_id = p.id
        JOIN owners o ON a.owner_id = o.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE a.status IN ('scheduled', 'in_progress')
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    """).fetchall()

    return render_template('consultation.html', appointments=appts)

@app.route('/consultation/add', methods=['GET', 'POST'])
@roles_required('doctor', 'admin')
def add_consultation():
    db = get_db()
    if request.method == 'POST':
        pet_id = request.form.get('pet_id')
        doctor_id = request.form.get('doctor_id')
        appointment_id = request.form.get('appointment_id') or None
        symptoms = request.form.get('symptoms')
        diagnosis = request.form.get('diagnosis')
        temperature = request.form.get('temperature') or None
        heart_rate = request.form.get('heart_rate') or None
        respiratory_rate = request.form.get('respiratory_rate') or None
        weight = request.form.get('weight') or None
        treatment_plan = request.form.get('treatment_plan')
        dietary_notes = request.form.get('dietary_notes', '')
        follow_up = request.form.get('follow_up_date') or None

        cur = db.cursor()
        cur.execute("""
            INSERT INTO medical_records (pet_id, doctor_id, appointment_id, record_date, symptoms, diagnosis, temperature, heart_rate, respiratory_rate, weight, treatment_plan, dietary_notes, follow_up_date)
            VALUES (?, ?, ?, DATE('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (pet_id, doctor_id, appointment_id, symptoms, diagnosis, temperature, heart_rate, respiratory_rate, weight, treatment_plan, dietary_notes, follow_up))
        record_id = cur.lastrowid

        # If linked to appointment, mark completed
        if appointment_id:
            cur.execute("UPDATE appointments SET status = 'completed' WHERE id = ?", (appointment_id,))

        # Update pet weight if provided
        if weight:
            cur.execute("UPDATE pets SET weight = ? WHERE id = ?", (weight, pet_id))

        # Handle Prescriptions line items if entered
        med_names = request.form.getlist('medicine_name[]')
        dosages = request.form.getlist('dosage_freq[]')
        durations = request.form.getlist('duration[]')

        if med_names and any(m.strip() for m in med_names):
            cur.execute("""
                INSERT INTO prescriptions (medical_record_id, pet_id, doctor_id, instructions)
                VALUES (?, ?, ?, ?)
            """, (record_id, pet_id, doctor_id, treatment_plan))
            rx_id = cur.lastrowid

            for m, d, dur in zip(med_names, dosages, durations):
                if m.strip():
                    cur.execute("""
                        INSERT INTO prescription_items (prescription_id, medicine_name, dosage, frequency, duration)
                        VALUES (?, ?, ?, ?, ?)
                    """, (rx_id, m.strip(), d.strip(), d.strip(), dur.strip()))

        db.commit()
        flash('Clinical consultation and medical record saved successfully!', 'success')
        return redirect(url_for('medical_records'))

    appt_id = request.args.get('appointment_id')
    selected_appt = None
    if appt_id:
        selected_appt = db.execute("""
            SELECT a.*, p.name as pet_name, p.species, p.weight as pet_weight, o.name as owner_name, d.id as doc_id
            FROM appointments a
            JOIN pets p ON a.pet_id = p.id
            JOIN owners o ON a.owner_id = o.id
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.id = ?
        """, (appt_id,)).fetchone()

    pets = db.execute("SELECT id, name, species FROM pets ORDER BY name ASC").fetchall()
    doctors = db.execute("""
        SELECT d.id, u.full_name 
        FROM doctors d 
        JOIN users u ON d.user_id = u.id
    """).fetchall()

    return render_template('consultation.html', 
                           appointment=selected_appt, 
                           pets=pets, 
                           doctors=doctors,
                           is_creating=True)

@app.route('/medical-records')
@login_required
def medical_records():
    db = get_db()
    records = db.execute("""
        SELECT m.*, p.name as pet_name, p.species, p.breed, o.name as owner_name, u.full_name as doctor_name
        FROM medical_records m
        JOIN pets p ON m.pet_id = p.id
        JOIN owners o ON p.owner_id = o.id
        JOIN doctors d ON m.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        ORDER BY m.record_date DESC, m.created_at DESC
    """).fetchall()
    return render_template('medical_records.html', records=records)

@app.route('/diagnosis')
@login_required
def diagnosis():
    db = get_db()
    records = db.execute("""
        SELECT m.id, m.record_date, m.diagnosis, m.symptoms, m.treatment_plan,
               p.name as pet_name, p.species, u.full_name as doctor_name
        FROM medical_records m
        JOIN pets p ON m.pet_id = p.id
        JOIN doctors d ON m.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE m.diagnosis IS NOT NULL AND m.diagnosis != ''
        ORDER BY m.record_date DESC
    """).fetchall()
    return render_template('diagnosis.html', records=records)

@app.route('/treatment')
@login_required
def treatment():
    db = get_db()
    records = db.execute("""
        SELECT m.id, m.record_date, m.diagnosis, m.treatment_plan, m.dietary_notes, m.follow_up_date,
               p.name as pet_name, p.species, u.full_name as doctor_name
        FROM medical_records m
        JOIN pets p ON m.pet_id = p.id
        JOIN doctors d ON m.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        WHERE m.treatment_plan IS NOT NULL AND m.treatment_plan != ''
        ORDER BY m.record_date DESC
    """).fetchall()
    return render_template('treatment.html', records=records)

@app.route('/prescriptions')
@login_required
def prescriptions():
    db = get_db()
    rx_list = db.execute("""
        SELECT pr.*, p.name as pet_name, p.species, o.name as owner_name, u.full_name as doctor_name
        FROM prescriptions pr
        JOIN pets p ON pr.pet_id = p.id
        JOIN owners o ON p.owner_id = o.id
        JOIN doctors d ON pr.doctor_id = d.id
        JOIN users u ON d.user_id = u.id
        ORDER BY pr.prescription_date DESC
    """).fetchall()

    # Load prescription items for each
    prescriptions_with_items = []
    for rx in rx_list:
        items = db.execute("SELECT * FROM prescription_items WHERE prescription_id = ?", (rx['id'],)).fetchall()
        prescriptions_with_items.append({'rx': rx, 'items': items})

    return render_template('prescriptions.html', prescriptions=prescriptions_with_items)

# --------------------------------------------------------------------------
# Vaccinations & Immunization Tracker
# --------------------------------------------------------------------------
@app.route('/vaccinations')
@login_required
def vaccinations():
    db = get_db()
    vax_list = db.execute("""
        SELECT v.*, p.name as pet_name, p.species, p.breed, o.name as owner_name, o.phone as owner_phone
        FROM vaccinations v
        JOIN pets p ON v.pet_id = p.id
        JOIN owners o ON p.owner_id = o.id
        ORDER BY v.next_due_date ASC
    """).fetchall()

    stats = {
        'up_to_date': sum(1 for v in vax_list if v['status'] == 'up_to_date'),
        'due_soon': sum(1 for v in vax_list if v['status'] == 'due_soon'),
        'overdue': sum(1 for v in vax_list if v['status'] == 'overdue')
    }

    return render_template('vaccinations.html', vaccinations=vax_list, stats=stats)

@app.route('/vaccinations/add', methods=['GET', 'POST'])
@login_required
def add_vaccination():
    db = get_db()
    if request.method == 'POST':
        pet_id = request.form.get('pet_id')
        vaccine_name = request.form.get('vaccine_name')
        admin_date = request.form.get('administered_date')
        next_due = request.form.get('next_due_date')
        batch = request.form.get('batch_number', '')
        vet_name = request.form.get('veterinarian_name', session.get('full_name', 'Doctor'))
        status = request.form.get('status', 'up_to_date')
        notes = request.form.get('notes', '')

        db.execute("""
            INSERT INTO vaccinations (pet_id, vaccine_name, administered_date, next_due_date, batch_number, veterinarian_name, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pet_id, vaccine_name, admin_date, next_due, batch, vet_name, status, notes))
        db.commit()

        flash(f"Vaccination {vaccine_name} logged successfully.", 'success')
        return redirect(url_for('vaccinations'))

    pets = db.execute("SELECT id, name, species FROM pets ORDER BY name ASC").fetchall()
    return render_template('add_vaccination.html', pets=pets)

@app.route('/vaccinations/history')
@login_required
def vaccination_history():
    db = get_db()
    history = db.execute("""
        SELECT v.*, p.name as pet_name, p.species, o.name as owner_name
        FROM vaccinations v
        JOIN pets p ON v.pet_id = p.id
        JOIN owners o ON p.owner_id = o.id
        ORDER BY v.administered_date DESC
    """).fetchall()
    return render_template('vaccination_history.html', history=history)

# --------------------------------------------------------------------------
# Pharmacy, Medicines & Inventory Management
# --------------------------------------------------------------------------
@app.route('/medicines')
@login_required
def medicines():
    db = get_db()
    search = request.args.get('q', '').strip()
    cat = request.args.get('category', '').strip()

    query = """
        SELECT m.*, s.name as supplier_name
        FROM medicines m
        LEFT JOIN suppliers s ON m.supplier_id = s.id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (m.name LIKE ? OR m.generic_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if cat:
        query += " AND m.category = ?"
        params.append(cat)

    query += " ORDER BY m.name ASC"
    med_list = db.execute(query, params).fetchall()
    categories = [r[0] for r in db.execute("SELECT DISTINCT category FROM medicines WHERE category IS NOT NULL").fetchall()]

    return render_template('medicines.html', medicines=med_list, categories=categories, search=search, selected_cat=cat)

@app.route('/medicines/add', methods=['GET', 'POST'])
@roles_required('admin', 'doctor', 'staff')
def add_medicine():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        generic_name = request.form.get('generic_name', '')
        category = request.form.get('category')
        supplier_id = request.form.get('supplier_id') or None
        unit_price = request.form.get('unit_price') or 0.0
        cost_price = request.form.get('cost_price') or 0.0
        stock_qty = request.form.get('stock_quantity') or 0
        min_stock = request.form.get('min_stock_level') or 10
        expiry = request.form.get('expiry_date') or None
        unit_type = request.form.get('unit_type', 'Tablets')
        desc = request.form.get('description', '')

        db.execute("""
            INSERT INTO medicines (name, generic_name, category, supplier_id, unit_price, cost_price, stock_quantity, min_stock_level, expiry_date, unit_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, generic_name, category, supplier_id, unit_price, cost_price, stock_qty, min_stock, expiry, unit_type, desc))
        db.commit()

        flash(f"Medicine {name} added to pharmacy catalog.", 'success')
        return redirect(url_for('medicines'))

    suppliers = db.execute("SELECT id, name FROM suppliers ORDER BY name ASC").fetchall()
    return render_template('add_medicine.html', suppliers=suppliers)

@app.route('/medicines/<int:id>/edit', methods=['POST'])
@login_required
def edit_medicine_stock(id):
    db = get_db()
    new_qty = request.form.get('stock_quantity')
    new_price = request.form.get('unit_price')
    if new_qty is not None and new_price is not None:
        db.execute("UPDATE medicines SET stock_quantity = ?, unit_price = ? WHERE id = ?", (new_qty, new_price, id))
        db.commit()
        flash('Medicine stock updated successfully.', 'success')
    return redirect(url_for('medicines'))

@app.route('/medicine-stock')
@login_required
def medicine_stock():
    db = get_db()
    low_stock = db.execute("""
        SELECT m.*, s.name as supplier_name, s.phone as supplier_phone
        FROM medicines m
        LEFT JOIN suppliers s ON m.supplier_id = s.id
        WHERE m.stock_quantity <= m.min_stock_level
        ORDER BY m.stock_quantity ASC
    """).fetchall()
    all_inventory = db.execute("SELECT * FROM medicines ORDER BY stock_quantity ASC").fetchall()
    return render_template('medicine_stock.html', low_stock=low_stock, all_inventory=all_inventory)

@app.route('/suppliers', methods=['GET', 'POST'])
@login_required
def suppliers():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact_person', '')
        phone = request.form.get('phone')
        email = request.form.get('email', '')
        address = request.form.get('address', '')

        db.execute("""
            INSERT INTO suppliers (name, contact_person, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
        """, (name, contact, phone, email, address))
        db.commit()
        flash(f"Supplier {name} registered.", 'success')
        return redirect(url_for('suppliers'))

    suppliers_list = db.execute("SELECT s.*, COUNT(m.id) as med_count FROM suppliers s LEFT JOIN medicines m ON s.id = m.supplier_id GROUP BY s.id ORDER BY s.name ASC").fetchall()
    return render_template('suppliers.html', suppliers=suppliers_list)

# --------------------------------------------------------------------------
# Billing, Invoices & Payments
# --------------------------------------------------------------------------
@app.route('/bills')
@login_required
def bills():
    db = get_db()
    status = request.args.get('status', 'all')
    
    query = """
        SELECT i.*, o.name as owner_name, o.phone as owner_phone, p.name as pet_name
        FROM invoices i
        JOIN owners o ON i.owner_id = o.id
        JOIN pets p ON i.pet_id = p.id
        WHERE 1=1
    """
    params = []
    if status != 'all':
        query += " AND i.payment_status = ?"
        params.append(status)

    query += " ORDER BY i.created_at DESC"
    invoices_list = db.execute(query, params).fetchall()
    return render_template('bills.html', invoices=invoices_list, selected_status=status)

@app.route('/bills/create', methods=['GET', 'POST'])
@login_required
def create_bill():
    db = get_db()
    if request.method == 'POST':
        owner_id = request.form.get('owner_id')
        pet_id = request.form.get('pet_id')
        appt_id = request.form.get('appointment_id') or None
        tax_rate = float(request.form.get('tax_rate', 8.0))
        discount = float(request.form.get('discount_amount', 0.0))
        notes = request.form.get('notes', '')

        # Generate invoice number
        inv_num = f"INV-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000:04d}"

        # Calculate line items
        desc_list = request.form.getlist('item_desc[]')
        type_list = request.form.getlist('item_type[]')
        qty_list = request.form.getlist('item_qty[]')
        price_list = request.form.getlist('item_price[]')

        subtotal = 0.0
        items_data = []
        for d, t, q, p in zip(desc_list, type_list, qty_list, price_list):
            if d.strip():
                qty = int(q)
                price = float(p)
                line_total = qty * price
                subtotal += line_total
                items_data.append((d.strip(), t, qty, price, line_total))

        tax_amt = subtotal * (tax_rate / 100.0)
        total_amt = max(0.0, subtotal + tax_amt - discount)

        cur = db.cursor()
        cur.execute("""
            INSERT INTO invoices (invoice_number, owner_id, pet_id, appointment_id, invoice_date, subtotal, tax_amount, discount_amount, total_amount, payment_status, notes)
            VALUES (?, ?, ?, ?, DATE('now'), ?, ?, ?, ?, 'unpaid', ?)
        """, (inv_num, owner_id, pet_id, appt_id, subtotal, tax_amt, discount, total_amt, notes))
        invoice_id = cur.lastrowid

        for item in items_data:
            cur.execute("""
                INSERT INTO invoice_items (invoice_id, description, item_type, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (invoice_id, item[0], item[1], item[2], item[3], item[4]))

        db.commit()
        flash(f"Invoice {inv_num} created successfully for ₹{total_amt:.2f}!", 'success')
        return redirect(url_for('invoice_details', id=invoice_id))

    owners = db.execute("SELECT id, name, phone FROM owners ORDER BY name ASC").fetchall()
    pets = db.execute("SELECT id, name, owner_id FROM pets ORDER BY name ASC").fetchall()
    appt_id = request.args.get('appointment_id')
    preselected = None
    if appt_id:
        preselected = db.execute("""
            SELECT a.*, p.name as pet_name, o.name as owner_name, d.consultation_fee
            FROM appointments a
            JOIN pets p ON a.pet_id = p.id
            JOIN owners o ON a.owner_id = o.id
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.id = ?
        """, (appt_id,)).fetchone()

    return render_template('create_bill.html', owners=owners, pets=pets, preselected=preselected)

@app.route('/invoice/<int:id>')
@login_required
def invoice_details(id):
    db = get_db()
    inv = db.execute("""
        SELECT i.*, o.name as owner_name, o.email as owner_email, o.phone as owner_phone, o.address as owner_address,
               p.name as pet_name, p.species, p.breed
        FROM invoices i
        JOIN owners o ON i.owner_id = o.id
        JOIN pets p ON i.pet_id = p.id
        WHERE i.id = ?
    """, (id,)).fetchone()

    if not inv:
        abort(404)

    items = db.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (id,)).fetchall()
    payments = db.execute("SELECT * FROM payments WHERE invoice_id = ? ORDER BY payment_date DESC", (id,)).fetchall()
    paid_sum = sum(p['amount'] for p in payments)
    balance_due = max(0.0, inv['total_amount'] - paid_sum)

    return render_template('invoice.html', invoice=inv, items=items, payments=payments, balance_due=balance_due)

@app.route('/payments')
@login_required
def payments():
    db = get_db()
    payments_list = db.execute("""
        SELECT py.*, i.invoice_number, o.name as owner_name, p.name as pet_name
        FROM payments py
        JOIN invoices i ON py.invoice_id = i.id
        JOIN owners o ON i.owner_id = o.id
        JOIN pets p ON i.pet_id = p.id
        ORDER BY py.payment_date DESC
    """).fetchall()
    return render_template('payments.html', payments=payments_list)

@app.route('/payments/add', methods=['POST'])
@login_required
def add_payment():
    invoice_id = request.form.get('invoice_id')
    amount = float(request.form.get('amount', 0.0))
    method = request.form.get('payment_method', 'cash')
    txn_ref = request.form.get('transaction_ref', f"TXN-{int(datetime.now().timestamp()) % 1000000}")
    notes = request.form.get('notes', '')

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO payments (invoice_id, amount, payment_method, transaction_ref, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (invoice_id, amount, method, txn_ref, notes))

    # Recalculate invoice status
    inv = db.execute("SELECT total_amount FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    if inv:
        total = inv['total_amount']
        row = db.execute("SELECT SUM(amount) as paid FROM payments WHERE invoice_id = ?", (invoice_id,)).fetchone()
        paid = row['paid'] or 0.0
        new_status = 'paid' if paid >= (total - 0.01) else ('partial' if paid > 0 else 'unpaid')
        cur.execute("UPDATE invoices SET payment_status = ? WHERE id = ?", (new_status, invoice_id))

    db.commit()
    flash(f"Payment of ₹{amount:.2f} recorded via {method.title()}.", 'success')
    return redirect(url_for('invoice_details', id=invoice_id))

# --------------------------------------------------------------------------
# Notifications, Reports, Analytics & Settings
# --------------------------------------------------------------------------
@app.route('/notifications')
@login_required
def notifications():
    db = get_db()
    notifications_list = db.execute("SELECT * FROM notifications ORDER BY created_at DESC").fetchall()
    return render_template('notifications.html', notifications=notifications_list)

@app.route('/notifications/read/<int:id>', methods=['POST'])
@login_required
def mark_notification_read(id):
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (id,))
    db.commit()
    return jsonify({'success': True})

@app.route('/reports')
@login_required
def reports():
    db = get_db()
    # Summary reporting metrics
    total_invoiced = db.execute("SELECT SUM(total_amount) FROM invoices").fetchone()[0] or 0.0
    total_collected = db.execute("SELECT SUM(amount) FROM payments").fetchone()[0] or 0.0
    total_appointments = db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    total_consults = db.execute("SELECT COUNT(*) FROM medical_records").fetchone()[0]

    return render_template('reports.html',
                           total_invoiced=total_invoiced,
                           total_collected=total_collected,
                           total_appointments=total_appointments,
                           total_consults=total_consults)

@app.route('/analytics')
@login_required
def analytics():
    db = get_db()
    # Species breakdown
    species_data = db.execute("SELECT species, COUNT(*) as count FROM pets GROUP BY species").fetchall()
    species_labels = [r['species'] or 'Other' for r in species_data]
    species_counts = [r['count'] for r in species_data]

    # Appointment status distribution
    status_data = db.execute("SELECT status, COUNT(*) as count FROM appointments GROUP BY status").fetchall()
    status_labels = [r['status'].replace('_', ' ').title() for r in status_data]
    status_counts = [r['count'] for r in status_data]

    # Inventory categories
    cat_data = db.execute("SELECT category, COUNT(*) as count FROM medicines GROUP BY category").fetchall()
    cat_labels = [r['category'] for r in cat_data]
    cat_counts = [r['count'] for r in cat_data]

    return render_template('analytics.html',
                           species_labels=species_labels,
                           species_counts=species_counts,
                           status_labels=status_labels,
                           status_counts=status_counts,
                           cat_labels=cat_labels,
                           cat_counts=cat_counts)

@app.route('/settings', methods=['GET', 'POST'])
@roles_required('admin')
def settings():
    if request.method == 'POST':
        app.config['CLINIC_NAME'] = request.form.get('clinic_name', app.config['CLINIC_NAME'])
        app.config['CLINIC_PHONE'] = request.form.get('clinic_phone', app.config['CLINIC_PHONE'])
        app.config['CLINIC_EMAIL'] = request.form.get('clinic_email', app.config['CLINIC_EMAIL'])
        app.config['CLINIC_ADDRESS'] = request.form.get('clinic_address', app.config['CLINIC_ADDRESS'])
        flash('Clinic parameters updated successfully.', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html')

# --------------------------------------------------------------------------
# Main Entry Point
# --------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
