# Generated by Django 5.2 on 2025-05-09 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop_app', '0007_machineusage'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='status_text',
            field=models.CharField(default='New', max_length=50),
        ),
    ]
