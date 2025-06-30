from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('grc', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE audit
                ADD COLUMN Report TEXT NULL;
            """,
            reverse_sql="""
                ALTER TABLE audit
                DROP COLUMN Report;
            """
        ),
    ] 