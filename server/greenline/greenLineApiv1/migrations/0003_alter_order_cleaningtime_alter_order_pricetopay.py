# Generated by Django 5.1 on 2024-09-03 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greenLineApiv1', '0002_alter_order_pricetopay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cleaningTime',
            field=models.TimeField(default='00:00:00'),
        ),
        migrations.AlterField(
            model_name='order',
            name='priceToPay',
            field=models.FloatField(default=0),
        ),
    ]
