# SkillsBuild - Professional Learning Platform

A modern web application built with Flask, MySQL, and Tailwind CSS for skill development and professional learning.

## Features

- **User Authentication**: Secure registration and login system
- **Profile Management**: User profiles with photo uploads and editable information
- **Modern UI**: Professional design using Tailwind CSS
- **Database Integration**: MySQL database with SQLAlchemy ORM
- **File Upload**: Profile photo upload functionality
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Authentication**: Flask-Login
- **File Handling**: Werkzeug
- **ORM**: SQLAlchemy

## Prerequisites

- Python 3.7+
- MySQL Server
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd skillsbuild
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL Database**
   ```sql
   CREATE DATABASE skillsbuild;
   ```

5. **Configure the application**
   - Update the database connection string in `app.py` if needed
   - Set your secret key in the environment variables

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## Database Schema

### Users Table
- `id` (Primary Key)
- `name` (String, Required)
- `email` (String, Unique, Required)
- `password` (String, Required, Hashed)
- `location` (String, Optional)
- `profile_photo` (String, Optional)
- `created_at` (DateTime, Auto-generated)
- `is_active` (Boolean, Default: True)

## Project Structure

```
skillsbuild/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── landing.html    # Landing page
│   ├── register.html   # Registration page
│   ├── login.html      # Login page
│   ├── dashboard.html  # User dashboard
│   └── profile.html    # User profile page
└── static/             # Static files
    └── uploads/        # User uploaded files
```

## Features Overview

### Landing Page
- Professional hero section with call-to-action
- Feature highlights
- Statistics showcase
- Modern gradient design

### User Registration
- Form validation
- Password confirmation
- Profile photo upload
- Email uniqueness check

### User Login
- Secure authentication
- Remember me functionality
- Social login options (UI only)
- Form validation

### Dashboard
- User statistics cards
- Recent activity feed
- Learning progress tracking
- Quick action buttons
- Recommended courses

### Profile Management
- Editable user information
- Profile photo management
- Account statistics
- Account status display

## Security Features

- Password hashing using Werkzeug
- CSRF protection
- Secure file upload handling
- Input validation and sanitization
- Session management

## Customization

### Styling
The application uses Tailwind CSS for styling. You can customize the design by:
- Modifying the Tailwind configuration in `templates/base.html`
- Adding custom CSS classes
- Updating color schemes and components

### Database
To use a different database:
1. Update the `SQLALCHEMY_DATABASE_URI` in `config.py`
2. Install the appropriate database driver
3. Update the requirements.txt file

## Deployment

### Production Setup
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure a reverse proxy (e.g., Nginx)
4. Set up SSL certificates
5. Use environment variables for sensitive data

### Environment Variables
- `SECRET_KEY`: Application secret key
- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Debug mode (True/False)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository. 