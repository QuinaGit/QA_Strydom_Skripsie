# Generated by Django 3.1.1 on 2020-09-21 13:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0002_lecturer_web_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance_logs',
            name='lecturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Lecturer',
        ),
    ]