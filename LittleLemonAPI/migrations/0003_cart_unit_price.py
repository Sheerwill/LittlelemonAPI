# Generated by Django 4.2.1 on 2023-05-24 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0002_remove_cart_unit_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="unit_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
            preserve_default=False,
        ),
    ]
