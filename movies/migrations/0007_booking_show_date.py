# Generated by Django 5.1.2 on 2025-03-18 10:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0006_theater_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='show_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
