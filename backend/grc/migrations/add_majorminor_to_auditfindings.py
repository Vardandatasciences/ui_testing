from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('grc', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE audit_findings
            ADD COLUMN MajorMinor CHAR(1) NULL;
            """,
            reverse_sql="""
            ALTER TABLE audit_findings
            DROP COLUMN MajorMinor;
            """
        ),
    ] 