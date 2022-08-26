# Generated by Django 2.2.16 on 2022-08-25 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20220825_1854'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='favourites',
            constraint=models.UniqueConstraint(fields=('favourit_recipe', 'user'), name='unique_favourite'),
        ),
        migrations.AddConstraint(
            model_name='shopping_cart',
            constraint=models.UniqueConstraint(fields=('buy_recipe', 'user'), name='unique_buy_recipe'),
        ),
    ]
