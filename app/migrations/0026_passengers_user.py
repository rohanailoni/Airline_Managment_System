# Generated by Django 3.1.1 on 2020-10-28 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_passengers'),
    ]

    operations = [
        migrations.AddField(
            model_name='passengers',
            name='user',
            field=models.ForeignKey(default=1000, on_delete=django.db.models.deletion.CASCADE, to='app.userinfo'),
            preserve_default=False,
        ),
    ]
