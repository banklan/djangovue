# Generated by Django 3.0.6 on 2020-05-15 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0002_auto_20200506_1134'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['created']},
        ),
    ]