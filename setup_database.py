#!/usr/bin/env python3
"""
Database setup script for SkillsBuild application.
This script creates the database and tables if they don't exist.
"""

import mysql.connector
from mysql.connector import Error
import sys

def create_database():
    """Drop and recreate the skillsbuild database from scratch."""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Update this if you have a password set
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Drop database if exists
            cursor.execute("DROP DATABASE IF EXISTS skillsbuild")
            print("🗑️ Dropped existing database 'skillsbuild'.")
            
            # Create fresh database
            cursor.execute("CREATE DATABASE skillsbuild")
            print("✅ Created fresh database 'skillsbuild'.")
            
            # Use the database
            cursor.execute("USE skillsbuild")
            
            # Create skills table
            create_skills_table = """
            CREATE TABLE IF NOT EXISTS skill (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                category VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_skills_table)
            print("✅ Skills table created successfully or already exists.")
            
            # Create users table with BLOB profile photo
            create_users_table = """
            CREATE TABLE user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                location VARCHAR(100),
                profile_photo LONGBLOB,
                profile_photo_type VARCHAR(50),
                bio TEXT,
                is_public BOOLEAN DEFAULT TRUE,
                weekdays_available BOOLEAN DEFAULT FALSE,
                evenings_available BOOLEAN DEFAULT FALSE,
                weekends_available BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            """
            cursor.execute(create_users_table)
            print("✅ Users table created successfully or already exists.")
            
            # Create association tables for many-to-many relationships
            create_user_skills_offered_table = """
            CREATE TABLE user_skills_offered (
                user_id INT,
                skill_id INT,
                PRIMARY KEY (user_id, skill_id),
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skill(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_user_skills_offered_table)
            print("✅ User skills offered table created successfully.")
            
            create_user_skills_wanted_table = """
            CREATE TABLE user_skills_wanted (
                user_id INT,
                skill_id INT,
                PRIMARY KEY (user_id, skill_id),
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skill(id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_user_skills_wanted_table)
            print("✅ User skills wanted table created successfully.")
            
            # Create swap requests table
            create_swap_requests_table = """
            CREATE TABLE swap_request (
                id INT AUTO_INCREMENT PRIMARY KEY,
                from_user_id INT NOT NULL,
                to_user_id INT NOT NULL,
                skill_offered_id INT,
                skill_wanted_id INT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (to_user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (skill_offered_id) REFERENCES skill(id) ON DELETE SET NULL,
                FOREIGN KEY (skill_wanted_id) REFERENCES skill(id) ON DELETE SET NULL
            )
            """
            cursor.execute(create_swap_requests_table)
            print("✅ Swap requests table created successfully.")
            
            # Insert some sample skills
            sample_skills = [
                ("Python", "Programming"),
                ("JavaScript", "Programming"),
                ("React", "Frontend"),
                ("Node.js", "Backend"),
                ("SQL", "Database"),
                ("MongoDB", "Database"),
                ("Docker", "DevOps"),
                ("AWS", "Cloud"),
                ("Machine Learning", "AI/ML"),
                ("Data Analysis", "Data Science"),
                ("UI/UX Design", "Design"),
                ("Project Management", "Management"),
                ("Agile", "Methodology"),
                ("Git", "Version Control"),
                ("REST API", "Backend")
            ]
            
            for skill_name, category in sample_skills:
                try:
                    cursor.execute("INSERT INTO skill (name, category) VALUES (%s, %s)", (skill_name, category))
                except mysql.connector.IntegrityError:
                    # Skill already exists, skip
                    pass
            
            print("✅ Sample skills added to database.")
            
            connection.commit()
            print("✅ Database setup completed successfully!")
            
    except Error as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ Database connection closed.")

def test_connection():
    """Test the database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update this if you have a password set
            database='skillsbuild'
        )
        
        if connection.is_connected():
            print("✅ Database connection test successful!")
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up SkillsBuild database...")
    print("=" * 50)
    
    # Create database and tables
    create_database()
    
    print("\n" + "=" * 50)
    print("🧪 Testing database connection...")
    
    # Test connection
    if test_connection():
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Install Python dependencies: pip install -r requirements.txt")
        print("2. Run the Flask application: python app.py")
        print("3. Open your browser and go to: http://localhost:5000")
    else:
        print("\n❌ Database setup failed. Please check your MySQL configuration.")
        sys.exit(1) 