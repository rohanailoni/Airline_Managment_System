# Generated by Django 3.1.1 on 2020-10-22 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_shortcuts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leg1',
            name='leg_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.leg'),
        ),
        migrations.CreateModel(
            name='price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('miles', models.IntegerField(default=100)),
                ('percent', models.IntegerField()),
                ('flight_leg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.leg')),
            ],
        ),
    ]
