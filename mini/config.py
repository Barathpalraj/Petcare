import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-vet-clinic-super-secret-key-2026'
    DATABASE = os.path.join(BASE_DIR, 'database', 'pet_clinic.db')
    SQL_SCHEMA = os.path.join(BASE_DIR, 'database', 'pet_clinic.sql')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'pet_photos')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    CLINIC_NAME = "PawCare Smart Veterinary Clinic & Hospital"
    CLINIC_PHONE = "+1 (555) 987-6543"
    CLINIC_EMAIL = "care@pawcareclinic.com"
    CLINIC_ADDRESS = "742 Evergreen Terrace, Animal Health District, CA 90210"
    CURRENCY_SYMBOL = "₹"
