# Generated by Django 3.1.1 on 2020-09-28 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_city_code_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leg',
            name='id',
        ),
        migrations.AlterField(
            model_name='leg',
            name='leg_id',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
    ]
