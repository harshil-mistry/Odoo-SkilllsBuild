#!/usr/bin/env python3
"""
Database migration script for SkillsBuild application.
This script adds missing columns to existing tables.
"""

import mysql.connector
from mysql.connector import Error
import sys

def migrate_database():
    """Add missing columns to existing tables."""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update this if you have a password set
            database='skillsbuild'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check and add missing columns to user table
            columns_to_add = [
                ("bio", "TEXT"),
                ("is_public", "BOOLEAN DEFAULT TRUE"),
                ("weekdays_available", "BOOLEAN DEFAULT FALSE"),
                ("evenings_available", "BOOLEAN DEFAULT FALSE"),
                ("weekends_available", "BOOLEAN DEFAULT FALSE")
            ]
            
            for column_name, column_definition in columns_to_add:
                try:
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {column_name} {column_definition}")
                    print(f"✅ Added column '{column_name}' to user table.")
                except mysql.connector.Error as e:
                    if e.errno == 1060:  # Duplicate column name error
                        print(f"ℹ️ Column '{column_name}' already exists in user table.")
                    else:
                        print(f"❌ Error adding column '{column_name}': {e}")
            
            connection.commit()
            print("✅ Database migration completed successfully!")
            
    except Error as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ Database connection closed.")

def verify_migration():
    """Verify that all required columns exist."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update this if you have a password set
            database='skillsbuild'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Get all columns from user table
            cursor.execute("DESCRIBE user")
            columns = [column[0] for column in cursor.fetchall()]
            
            required_columns = [
                'id', 'name', 'email', 'password', 'location', 'profile_photo',
                'bio', 'is_public', 'weekdays_available', 'evenings_available', 
                'weekends_available', 'created_at', 'is_active'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns are present in user table.")
                return True
                
    except Error as e:
        print(f"❌ Error verifying migration: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Migrating SkillsBuild database...")
    print("=" * 50)
    
    # Run migration
    migrate_database()
    
    print("\n" + "=" * 50)
    print("🧪 Verifying migration...")
    
    # Verify migration
    if verify_migration():
        print("\n🎉 Database migration completed successfully!")
        print("\nYou can now run the Flask application: python app.py")
    else:
        print("\n❌ Database migration failed. Please check the errors above.")
        sys.exit(1) 