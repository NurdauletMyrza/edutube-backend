# Generated by Django 5.1.6 on 2025-02-18 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('student', 'Student'), ('teacher', 'Teacher')], max_length=20, null=True),
        ),
    ]
