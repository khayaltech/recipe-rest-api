# Generated by Django 3.2.15 on 2022-08-21 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='time_in_minutes',
            field=models.IntegerField(null=True),
        ),
    ]