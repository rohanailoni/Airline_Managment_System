# Generated by Django 3.1.1 on 2020-10-29 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_passengers_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('account_id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('amount', models.FloatField()),
                ('cvv', models.IntegerField()),
                ('expiration_date', models.CharField(max_length=5)),
                ('phone', models.IntegerField()),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
