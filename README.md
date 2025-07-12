Problem Statement : Skill Swap Platform
Develop a Skill Swap Platform — a mini application that enables users to list their skills and
request others in return

Team Name : Team 1796 (CodeFreaks)

Team Members :

Harshil Mistry (harshilmistry31@gmail.com) - Team Leader

Tarishi Jain (23cs027@charusat.edu.in)

Harsh Dodiya (d24cs119@charusat.edu.in)

Ishita Prajapati (23cs079@charusat.edu.in)

Youtube Presentaion Video : https://www.youtube.com/watch?v=-rAHn2wHWDY

# SkillsBuild - Professional Skill Exchange Platform

A modern web application built with Flask, MySQL, and Tailwind CSS that enables users to exchange skills with each other. Users can offer their expertise and find others who can teach them new skills through a collaborative learning platform.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure registration and login system with profile photo uploads
- **Skill Management**: Add, edit, and manage skills you can offer and skills you want to learn
- **Skill Exchange System**: Send and receive swap requests for skill exchanges
- **User Search**: Find potential skill exchange partners by location, skills, and availability
- **Profile Management**: Comprehensive user profiles with public/private settings
- **Dashboard**: Interactive dashboard with statistics, recent activity, and quick actions

### Advanced Features
- **Swap Request Tracking**: Manage incoming and outgoing swap requests with accept/reject/delete actions
- **Public User Profiles**: View other users' public profiles and their skill exchange statistics
- **Availability Settings**: Set your availability for weekdays, evenings, and weekends
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Real-time Notifications**: Pending request count displayed in navigation

### Technical Features
- **Modern UI**: Professional design using Tailwind CSS with gradients and animations
- **Database Integration**: MySQL database with SQLAlchemy ORM
- **File Upload**: Profile photo upload with BLOB storage
- **Search & Filtering**: Advanced search with multiple criteria
- **API Endpoints**: RESTful APIs for skill management and profile updates

## 🛠 Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with PyMySQL connector
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Authentication**: Flask-Login
- **File Handling**: Werkzeug with BLOB storage
- **ORM**: SQLAlchemy
- **UI Framework**: Tailwind CSS

## 📋 Prerequisites

- Python 3.7+
- MySQL Server
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/harshil-mistry/Odoo-SkilllsBuild
   cd Odoo-SkilllsBuild
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
   - Start the MySQL locally from XAMPP 

5. **Configure the application**
   - Update the database connection string in `app.py` if needed
   - Set your secret key in the environment variables

6. **Initialize the database**
   ```bash
   python setup_database.py
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## 🗄 Database Schema

### Users Table
- `id` (Primary Key)
- `name` (String, Required)
- `email` (String, Unique, Required)
- `password` (String, Required, Hashed)
- `location` (String, Optional)
- `profile_photo` (BLOB, Optional)
- `profile_photo_type` (String, Optional)
- `bio` (Text, Optional)
- `is_public` (Boolean, Default: True)
- `weekdays_available` (Boolean, Default: False)
- `evenings_available` (Boolean, Default: False)
- `weekends_available` (Boolean, Default: False)
- `created_at` (DateTime, Auto-generated)
- `is_active` (Boolean, Default: True)

### Skills Table
- `id` (Primary Key)
- `name` (String, Unique, Required)
- `category` (String, Optional)
- `created_at` (DateTime, Auto-generated)

### Swap Requests Table
- `id` (Primary Key)
- `from_user_id` (Foreign Key to Users)
- `to_user_id` (Foreign Key to Users)
- `skill_offered_id` (Foreign Key to Skills)
- `skill_wanted_id` (Foreign Key to Skills)
- `status` (String: pending/accepted/rejected)
- `created_at` (DateTime, Auto-generated)

### Association Tables
- `user_skills_offered` (Many-to-many relationship)
- `user_skills_wanted` (Many-to-many relationship)

## 📁 Project Structure

```
skillsbuild/
├── app.py                    # Main Flask application
├── setup_database.py         # Database initialization script
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── .gitignore               # Git ignore file
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── landing.html        # Landing page
│   ├── register.html       # Registration page
│   ├── login.html          # Login page
│   ├── dashboard.html      # User dashboard
│   ├── profile.html        # User profile management
│   ├── search.html         # User search and skill exchange
│   ├── swap_requests.html  # Swap request management
│   ├── user_profile.html   # Public user profile view
│   └── 404.html           # Custom 404 error page
└── static/                 # Static files
    └── uploads/            # User uploaded files
```

## 🎯 Features Overview

### Landing Page
- Professional hero section with call-to-action
- Feature highlights showcasing skill exchange benefits
- Statistics showcase
- Modern gradient design with animations

### User Registration & Authentication
- Form validation with real-time feedback
- Password confirmation
- Profile photo upload with BLOB storage
- Email uniqueness validation
- Secure password hashing

### Dashboard
- **Statistics Cards**: Total sent/received requests, pending requests, accepted exchanges
- **Recent Activity**: Latest swap requests sent and received
- **Potential Partners**: Users with matching skills for exchanges
- **Profile Completion**: Progress indicator for profile completion
- **Quick Actions**: Direct links to search, profile, and swap requests
- **Tips Section**: Helpful suggestions for using the platform

### Profile Management
- **Editable Information**: Name, location, bio, availability settings
- **Profile Photo**: Upload and manage profile pictures
- **Privacy Settings**: Toggle public/private profile visibility
- **Skill Management**: Add/remove skills offered and wanted
- **Availability Settings**: Set availability for weekdays, evenings, weekends

### Skill Exchange System
- **Skill Search**: Find users by skills, location, and availability
- **Swap Requests**: Send detailed swap requests with specific skills
- **Request Management**: Accept, reject, or delete swap requests
- **Request Tracking**: View all sent and received requests with status

### User Search & Discovery
- **Advanced Search**: Filter by skills, location, and availability
- **User Cards**: Display user information with profile photos
- **Skill Exchange Modal**: Select specific skills for exchange
- **Public Profiles**: View detailed user profiles and statistics

### Responsive Design
- **Mobile Navigation**: Hamburger menu for mobile devices
- **Adaptive Layouts**: Responsive grids and typography
- **Touch-Friendly**: Optimized for touch interactions
- **Cross-Device**: Works seamlessly on desktop, tablet, and mobile

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface using Tailwind CSS
- **Responsive Layout**: Mobile-first design approach
- **Interactive Elements**: Hover effects, transitions, and animations
- **Flash Messages**: User feedback for actions and errors
- **Loading States**: Visual feedback for async operations
- **Accessibility**: Semantic HTML and keyboard navigation

## 🔧 API Endpoints

### Skills Management
- `GET /api/skills` - Get all available skills
- `POST /api/skills` - Create a new skill
- `GET /api/profile/skills` - Get user's current skills
- `POST /api/profile/skills` - Update user's skills

### User Management
- `GET /profile_photo/<user_id>` - Serve user profile photos
- `GET /user/<user_id>` - View public user profile

### Swap Requests
- `POST /send_swap_request/<user_id>` - Send a swap request
- `POST /accept_swap_request/<request_id>` - Accept a request
- `POST /reject_swap_request/<request_id>` - Reject a request
- `POST /delete_swap_request/<request_id>` - Delete a request

## 🆘 Support

For support and questions:
- Open an issue in the repository
- Check the documentation
- Review the code comments

## 🔄 Recent Updates

- **Responsive Design**: All templates now fully responsive for mobile devices
- **Enhanced Dashboard**: Added statistics, recent activity, and potential partners
- **Swap Request System**: Complete skill exchange functionality with tracking
- **User Search**: Advanced search with filters and skill selection
- **Profile Management**: Comprehensive profile editing with skills and availability
- **Custom 404 Page**: User-friendly error handling
- **Mobile Navigation**: Hamburger menu for mobile devices
- **Performance Optimizations**: Improved database queries and frontend performance 
