# Generated by Django 3.1.1 on 2020-09-30 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment_id',
            field=models.CharField(max_length=5, primary_key=True, serialize=False),
        ),
    ]
