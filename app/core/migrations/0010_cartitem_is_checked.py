# Generated by Django 4.2.22 on 2025-06-22 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_useraction'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='is_checked',
            field=models.BooleanField(default=False),
        ),
    ]
