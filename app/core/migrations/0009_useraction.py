# Generated by Django 4.2.22 on 2025-06-06 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_user_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('product_id', models.CharField(max_length=100)),
                ('event_type', models.CharField(choices=[('view', 'View'), ('cart', 'Add to Cart'), ('purchase', 'Purchase'), ('remove_from_cart', 'Remove from Cart')], default='view', max_length=50)),
                ('event_time', models.DateTimeField(auto_now_add=True)),
                ('score', models.FloatField(default=1.0)),
            ],
        ),
    ]
