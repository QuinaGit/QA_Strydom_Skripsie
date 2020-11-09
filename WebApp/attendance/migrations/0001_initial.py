# Generated by Django 3.1.1 on 2020-11-04 10:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sessions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('scan_count', models.PositiveIntegerField()),
                ('session_id', models.CharField(max_length=50)),
                ('lecturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Attendance_Logs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('usnumber', models.PositiveIntegerField()),
                ('date', models.DateTimeField()),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.sessions')),
            ],
        ),
    ]
