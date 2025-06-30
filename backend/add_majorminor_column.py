import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Now we can use Django models
from django.db import connection

def add_majorminor_column():
    print("Attempting to add MajorMinor column to audit_findings table...")
    
    with connection.cursor() as cursor:
        # Check if the column already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_NAME = 'audit_findings' 
            AND COLUMN_NAME = 'MajorMinor'
        """)
        
        column_exists = cursor.fetchone()[0] > 0
        
        if column_exists:
            print("MajorMinor column already exists in audit_findings table.")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE audit_findings
                ADD COLUMN MajorMinor CHAR(1) NULL;
            """)
            print("MajorMinor column added successfully to audit_findings table.")

if __name__ == "__main__":
    add_majorminor_column()
    print("Script completed.") 