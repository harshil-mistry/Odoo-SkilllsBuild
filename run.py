#!/usr/bin/env python3
"""
Run script for SkillsBuild Flask application.
This script starts the Flask development server.
"""

import os
import sys
from app import app

def main():
    """Main function to run the Flask application."""
    print("🚀 Starting SkillsBuild application...")
    print("=" * 50)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    # Check if database is accessible
    try:
        from app import db
        with app.app_context():
            db.engine.connect()
        print("✅ Database connection verified.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please run 'python setup_database.py' first to set up the database.")
        sys.exit(1)
    
    print("✅ Starting Flask development server...")
    print("🌐 Application will be available at: http://localhost:5000")
    print("📝 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

if __name__ == "__main__":
    main() 