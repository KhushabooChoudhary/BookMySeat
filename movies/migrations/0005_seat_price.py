# Generated by Django 5.1.2 on 2025-03-17 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_alter_movie_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='seat',
            name='price',
            field=models.DecimalField(decimal_places=2, default=150.0, max_digits=6),
        ),
    ]
