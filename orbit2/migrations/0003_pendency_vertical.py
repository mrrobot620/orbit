# Generated by Django 5.0.1 on 2024-01-16 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orbit2', '0002_alter_pendency_brand_alter_pendency_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendency',
            name='vertical',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
