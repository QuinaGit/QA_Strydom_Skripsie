# Generated by Django 3.1.1 on 2020-11-04 16:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_device'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='last_upload',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]