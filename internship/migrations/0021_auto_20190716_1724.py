# Generated by Django 2.2.2 on 2019-07-16 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0020_auto_20190716_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logbook',
            name='week',
            field=models.PositiveIntegerField(),
        ),
    ]