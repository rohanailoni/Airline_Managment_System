# Generated by Django 3.1.1 on 2020-09-28 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200928_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='city_code',
            name='country',
            field=models.CharField(default='United Arab Emirates', max_length=200),
        ),
    ]
