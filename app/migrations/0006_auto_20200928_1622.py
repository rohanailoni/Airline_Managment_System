# Generated by Django 3.1.1 on 2020-09-28 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20200928_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enquiry',
            name='enquiry_id',
            field=models.CharField(max_length=6, primary_key=True, serialize=False),
        ),
    ]
