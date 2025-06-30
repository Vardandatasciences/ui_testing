from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('grc', '0002_audit_framework_policy_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='Users',
        ),
        migrations.AlterField(
            model_name='audit',
            name='assignee',
            field=models.ForeignKey(db_column='assignee', on_delete=django.db.models.deletion.CASCADE, related_name='assignee', to='grc.userss'),
        ),
        migrations.AlterField(
            model_name='audit',
            name='auditor',
            field=models.ForeignKey(db_column='auditor', on_delete=django.db.models.deletion.CASCADE, related_name='auditor', to='grc.userss'),
        ),
        migrations.AlterField(
            model_name='audit',
            name='reviewer',
            field=models.ForeignKey(blank=True, db_column='reviewer', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviewer', to='grc.userss'),
        ),
    ] 