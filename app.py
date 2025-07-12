from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/skillsbuild'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Association tables for many-to-many relationships
user_skills_offered = db.Table('user_skills_offered',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

user_skills_wanted = db.Table('user_skills_wanted',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

# Skill Model
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Skill {self.name}>'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Availability fields
    weekdays_available = db.Column(db.Boolean, default=False)
    evenings_available = db.Column(db.Boolean, default=False)
    weekends_available = db.Column(db.Boolean, default=False)
    
    # Relationships
    skills_offered = db.relationship('Skill', secondary=user_skills_offered, 
                                   backref=db.backref('users_offering', lazy='dynamic'))
    skills_wanted = db.relationship('Skill', secondary=user_skills_wanted, 
                                  backref=db.backref('users_wanting', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        location = request.form.get('location', '')
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        # Handle profile photo upload
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_photo = filename
        
        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            location=location,
            profile_photo=profile_photo
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location', '')
        bio = request.form.get('bio', '')
        is_public = request.form.get('is_public') == 'on'
        
        # Availability
        weekdays_available = request.form.get('weekdays_available') == 'on'
        evenings_available = request.form.get('evenings_available') == 'on'
        weekends_available = request.form.get('weekends_available') == 'on'
        
        if name:
            current_user.name = name
            current_user.location = location
            current_user.bio = bio
            current_user.is_public = is_public
            current_user.weekdays_available = weekdays_available
            current_user.evenings_available = evenings_available
            current_user.weekends_available = weekends_available
            
            # Handle profile photo update
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    current_user.profile_photo = filename
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
    
    # Get all available skills for the form
    all_skills = Skill.query.all()
    return render_template('profile.html', all_skills=all_skills)

@app.route('/api/skills', methods=['GET'])
@login_required
def get_skills():
    """Get all available skills for autocomplete"""
    skills = Skill.query.all()
    return jsonify([{'id': skill.id, 'name': skill.name, 'category': skill.category} for skill in skills])

@app.route('/api/skills', methods=['POST'])
@login_required
def create_skill():
    """Create a new skill"""
    data = request.get_json()
    skill_name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    
    if not skill_name:
        return jsonify({'error': 'Skill name is required'}), 400
    
    # Check if skill already exists
    existing_skill = Skill.query.filter_by(name=skill_name).first()
    if existing_skill:
        return jsonify({'id': existing_skill.id, 'name': existing_skill.name, 'category': existing_skill.category})
    
    # Create new skill
    new_skill = Skill(name=skill_name, category=category)
    db.session.add(new_skill)
    db.session.commit()
    
    return jsonify({'id': new_skill.id, 'name': new_skill.name, 'category': new_skill.category})

@app.route('/api/profile/skills', methods=['POST'])
@login_required
def update_profile_skills():
    """Update user's skills offered and wanted"""
    data = request.get_json()
    skills_offered_ids = data.get('skills_offered', [])
    skills_wanted_ids = data.get('skills_wanted', [])
    
    # Clear existing skills
    current_user.skills_offered.clear()
    current_user.skills_wanted.clear()
    
    # Add new skills offered
    for skill_id in skills_offered_ids:
        skill = Skill.query.get(skill_id)
        if skill:
            current_user.skills_offered.append(skill)
    
    # Add new skills wanted
    for skill_id in skills_wanted_ids:
        skill = Skill.query.get(skill_id)
        if skill:
            current_user.skills_wanted.append(skill)
    
    db.session.commit()
    return jsonify({'message': 'Skills updated successfully'})

@app.route('/api/profile/skills', methods=['GET'])
@login_required
def get_profile_skills():
    """Get user's current skills"""
    return jsonify({
        'skills_offered': [{'id': skill.id, 'name': skill.name} for skill in current_user.skills_offered],
        'skills_wanted': [{'id': skill.id, 'name': skill.name} for skill in current_user.skills_wanted]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 