# Generated by Django 3.1.1 on 2020-10-28 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_passengers_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='passengers',
            name='transaction',
            field=models.CharField(default='#TRA00000', max_length=15),
            preserve_default=False,
        ),
    ]