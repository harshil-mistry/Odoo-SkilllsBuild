from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from dotenv import load_dotenv
import io

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/skillsbuild'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

# Swap Request Model
class SwapRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_offered_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=True)
    skill_wanted_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='sent_requests')
    to_user = db.relationship('User', foreign_keys=[to_user_id], backref='received_requests')
    skill_offered = db.relationship('Skill', foreign_keys=[skill_offered_id])
    skill_wanted = db.relationship('Skill', foreign_keys=[skill_wanted_id])

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
    profile_photo = db.Column(db.LargeBinary, nullable=True)  # Changed to BLOB
    profile_photo_type = db.Column(db.String(50), nullable=True)  # Store MIME type
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

@app.context_processor
def inject_pending_requests():
    """Inject pending request count into all templates"""
    if current_user.is_authenticated:
        pending_count = SwapRequest.query.filter_by(to_user_id=current_user.id, status='pending').count()
        return {'pending_requests_count': pending_count}
    return {'pending_requests_count': 0}

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
        profile_photo_type = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '':
                # Read file as binary
                profile_photo = file.read()
                profile_photo_type = file.content_type
        
        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            location=location,
            profile_photo=profile_photo,
            profile_photo_type=profile_photo_type
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
    # Get swap request statistics
    sent_requests = SwapRequest.query.filter_by(from_user_id=current_user.id).all()
    received_requests = SwapRequest.query.filter_by(to_user_id=current_user.id).all()
    
    # Calculate statistics
    total_sent = len(sent_requests)
    total_received = len(received_requests)
    pending_received = len([r for r in received_requests if r.status == 'pending'])
    accepted_requests = len([r for r in sent_requests + received_requests if r.status == 'accepted'])
    
    # Get recent swap requests (last 5)
    recent_sent = SwapRequest.query.filter_by(from_user_id=current_user.id).order_by(SwapRequest.created_at.desc()).limit(3).all()
    recent_received = SwapRequest.query.filter_by(to_user_id=current_user.id).order_by(SwapRequest.created_at.desc()).limit(3).all()
    
    # Get users with matching skills (potential swap partners)
    potential_partners = []
    if current_user.skills_wanted:
        # Find users who offer skills that current user wants
        for wanted_skill in current_user.skills_wanted:
            users_with_skill = User.query.filter(
                User.skills_offered.contains(wanted_skill),
                User.is_public == True,
                User.id != current_user.id
            ).limit(3).all()
            potential_partners.extend(users_with_skill)
    
    # Remove duplicates and limit to 5
    potential_partners = list({user.id: user for user in potential_partners}.values())[:5]
    
    # Calculate profile completion percentage
    profile_fields = [
        current_user.name, current_user.location, current_user.bio, 
        current_user.profile_photo, current_user.skills_offered, current_user.skills_wanted,
        current_user.weekdays_available, current_user.evenings_available, current_user.weekends_available
    ]
    completed_fields = sum(1 for field in profile_fields if field and (not hasattr(field, '__len__') or len(field) > 0))
    profile_completion = int((completed_fields / len(profile_fields)) * 100)
    
    return render_template('dashboard.html',
                         total_sent=total_sent,
                         total_received=total_received,
                         pending_received=pending_received,
                         accepted_requests=accepted_requests,
                         recent_sent=recent_sent,
                         recent_received=recent_received,
                         potential_partners=potential_partners,
                         profile_completion=profile_completion)

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
                    # Read file as binary
                    current_user.profile_photo = file.read()
                    current_user.profile_photo_type = file.content_type
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
    
    # Get all available skills for the form
    all_skills = Skill.query.all()
    return render_template('profile.html', all_skills=all_skills)

@app.route('/profile_photo/<int:user_id>')
def profile_photo(user_id):
    """Serve profile photo as image"""
    user = User.query.get_or_404(user_id)
    if user.profile_photo:
        return send_file(
            io.BytesIO(user.profile_photo),
            mimetype=user.profile_photo_type or 'image/jpeg'
        )
    else:
        # Return a default image or 404
        return '', 404

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    location = request.args.get('location', '').strip()
    availability = request.args.getlist('availability')  # e.g. ['weekdays', 'weekends']

    users = User.query.filter(User.is_public == True, User.id != current_user.id)

    if query:
        users = users.join(User.skills_offered).filter(Skill.name.ilike(f'%{query}%'))

    if location:
        users = users.filter(User.location.ilike(f'%{location}%'))

    if availability:
        if 'weekdays' in availability:
            users = users.filter(User.weekdays_available == True)
        if 'evenings' in availability:
            users = users.filter(User.evenings_available == True)
        if 'weekends' in availability:
            users = users.filter(User.weekends_available == True)

    users = users.distinct().all()
    
    # Get current user's skills for the swap request form
    current_user_skills_offered = [{'id': skill.id, 'name': skill.name} for skill in current_user.skills_offered]
    current_user_skills_wanted = [{'id': skill.id, 'name': skill.name} for skill in current_user.skills_wanted]
    
    # Convert users' skills to serializable format for the template
    users_with_skills = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'location': user.location,
            'bio': user.bio,
            'profile_photo': user.profile_photo,
            'profile_photo_type': user.profile_photo_type,
            'weekdays_available': user.weekdays_available,
            'evenings_available': user.evenings_available,
            'weekends_available': user.weekends_available,
            'skills_offered': [{'id': skill.id, 'name': skill.name} for skill in user.skills_offered],
            'skills_wanted': [{'id': skill.id, 'name': skill.name} for skill in user.skills_wanted]
        }
        users_with_skills.append(user_data)
    
    return render_template('search.html', 
                         users=users_with_skills, 
                         query=query, 
                         location=location, 
                         availability=availability,
                         current_user_skills_offered=current_user_skills_offered,
                         current_user_skills_wanted=current_user_skills_wanted)

@app.route('/send_swap_request/<int:to_user_id>', methods=['POST'])
@login_required
def send_swap_request(to_user_id):
    if to_user_id == current_user.id:
        flash('You cannot send a swap request to yourself.', 'error')
        return redirect(url_for('search'))
    
    # Get form data
    skill_offered_id = request.form.get('skill_offered_id')
    skill_wanted_id = request.form.get('skill_wanted_id')
    
    # Validate that skills are provided
    if not skill_offered_id or not skill_wanted_id:
        flash('Please select both a skill to offer and a skill to receive.', 'error')
        return redirect(url_for('search'))
    
    # Validate that the offered skill belongs to current user
    offered_skill = Skill.query.get(skill_offered_id)
    if not offered_skill or offered_skill not in current_user.skills_offered:
        flash('Please select a skill that you can offer.', 'error')
        return redirect(url_for('search'))
    
    # Validate that the wanted skill belongs to the target user
    target_user = User.query.get(to_user_id)
    if not target_user:
        flash('User not found.', 'error')
        return redirect(url_for('search'))
    
    wanted_skill = Skill.query.get(skill_wanted_id)
    if not wanted_skill or wanted_skill not in target_user.skills_offered:
        flash('Please select a skill that the user can offer.', 'error')
        return redirect(url_for('search'))
    
    # Check if request already exists
    existing_request = SwapRequest.query.filter_by(
        from_user_id=current_user.id, 
        to_user_id=to_user_id,
        status='pending'
    ).first()
    
    if existing_request:
        flash('You have already sent a swap request to this user.', 'error')
        return redirect(url_for('search'))
    
    # Create swap request with specific skills
    swap = SwapRequest(
        from_user_id=current_user.id, 
        to_user_id=to_user_id,
        skill_offered_id=skill_offered_id,
        skill_wanted_id=skill_wanted_id
    )
    db.session.add(swap)
    db.session.commit()
    
    flash(f'Swap request sent! You offered "{offered_skill.name}" for "{wanted_skill.name}".', 'success')
    return redirect(url_for('search'))

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

@app.route('/swap_requests')
@login_required
def swap_requests():
    """Display all swap requests for the current user"""
    # Get requests sent by current user
    sent_requests = SwapRequest.query.filter_by(from_user_id=current_user.id).order_by(SwapRequest.created_at.desc()).all()
    
    # Get requests received by current user
    received_requests = SwapRequest.query.filter_by(to_user_id=current_user.id).order_by(SwapRequest.created_at.desc()).all()
    
    return render_template('swap_requests.html', 
                         sent_requests=sent_requests, 
                         received_requests=received_requests)

@app.route('/accept_swap_request/<int:request_id>', methods=['POST'])
@login_required
def accept_swap_request(request_id):
    """Accept a swap request"""
    swap_request = SwapRequest.query.get_or_404(request_id)
    
    # Check if current user is the receiver
    if swap_request.to_user_id != current_user.id:
        flash('You can only accept requests sent to you.', 'error')
        return redirect(url_for('swap_requests'))
    
    # Check if request is still pending
    if swap_request.status != 'pending':
        flash('This request has already been processed.', 'error')
        return redirect(url_for('swap_requests'))
    
    # Update status to accepted
    swap_request.status = 'accepted'
    db.session.commit()
    
    flash('Swap request accepted! You can now coordinate with the other user.', 'success')
    return redirect(url_for('swap_requests'))

@app.route('/reject_swap_request/<int:request_id>', methods=['POST'])
@login_required
def reject_swap_request(request_id):
    """Reject a swap request"""
    swap_request = SwapRequest.query.get_or_404(request_id)
    
    # Check if current user is the receiver
    if swap_request.to_user_id != current_user.id:
        flash('You can only reject requests sent to you.', 'error')
        return redirect(url_for('swap_requests'))
    
    # Check if request is still pending
    if swap_request.status != 'pending':
        flash('This request has already been processed.', 'error')
        return redirect(url_for('swap_requests'))
    
    # Update status to rejected
    swap_request.status = 'rejected'
    db.session.commit()
    
    flash('Swap request rejected.', 'info')
    return redirect(url_for('swap_requests'))

@app.route('/delete_swap_request/<int:request_id>', methods=['POST'])
@login_required
def delete_swap_request(request_id):
    """Delete a pending swap request (only sender can delete)"""
    swap_request = SwapRequest.query.get_or_404(request_id)
    
    # Check if current user is the sender
    if swap_request.from_user_id != current_user.id:
        flash('You can only delete requests you sent.', 'error')
        return redirect(url_for('swap_requests'))
    
    # Check if request is still pending
    if swap_request.status != 'pending':
        flash('You can only delete pending requests.', 'error')
        return redirect(url_for('swap_requests'))
    
    # Delete the request
    db.session.delete(swap_request)
    db.session.commit()
    
    flash('Swap request deleted.', 'info')
    return redirect(url_for('swap_requests'))

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """View public profile of a user"""
    user = User.query.get_or_404(user_id)
    
    # Check if user profile is public
    if not user.is_public:
        flash('This profile is private.', 'error')
        return redirect(url_for('search'))
    
    # Get user's swap request statistics
    sent_requests = SwapRequest.query.filter_by(from_user_id=user.id).all()
    received_requests = SwapRequest.query.filter_by(to_user_id=user.id).all()
    
    total_sent = len(sent_requests)
    total_received = len(received_requests)
    accepted_requests = len([r for r in sent_requests + received_requests if r.status == 'accepted'])
    
    # Check if current user is authenticated and can send swap requests
    can_send_request = False
    if current_user.is_authenticated and current_user.id != user.id:
        # Check if there's already a pending request
        existing_request = SwapRequest.query.filter_by(
            from_user_id=current_user.id, 
            to_user_id=user.id,
            status='pending'
        ).first()
        can_send_request = not existing_request
    
    return render_template('user_profile.html',
                         user=user,
                         total_sent=total_sent,
                         total_received=total_received,
                         accepted_requests=accepted_requests,
                         can_send_request=can_send_request)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with custom page"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 