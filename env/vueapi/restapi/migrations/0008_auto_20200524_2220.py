# Generated by Django 3.0.6 on 2020-05-24 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0007_auto_20200524_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.DecimalField(decimal_places=1, max_digits=2),
        ),
    ]