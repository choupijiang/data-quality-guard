#!/usr/bin/env python3
"""
Create default admin user script
This script creates the default system admin user with username 'admin' and password 'admin123'
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import User, UserRole
from app.core.security import get_password_hash

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("Admin user already exists")
            return
        
        # Create admin user directly with a simple password hash
        # Using a basic approach for now
        import hashlib
        password = "admin123"
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            role=UserRole.SYSTEM_ADMIN
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Created default admin user: {admin_user.username} with role {admin_user.role}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating default admin user...")
    create_default_admin()
    print("Done!")