# Generated by Django 3.1.1 on 2020-10-21 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_orders_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='items_json',
            field=models.CharField(max_length=5000, null=True),
        ),
    ]