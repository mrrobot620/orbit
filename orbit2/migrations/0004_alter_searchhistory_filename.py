# Generated by Django 5.0.1 on 2024-01-22 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orbit2', '0003_searchhistory_filename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchhistory',
            name='filename',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
