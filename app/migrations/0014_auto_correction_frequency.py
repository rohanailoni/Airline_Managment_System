# Generated by Django 3.1.1 on 2020-10-01 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20200930_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='auto_correction',
            name='frequency',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
