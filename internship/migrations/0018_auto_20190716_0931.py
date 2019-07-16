# Generated by Django 2.2.2 on 2019-07-16 06:31

import django.core.validators
from django.db import migrations, models
import internship.models


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0017_allocatedsupervisor_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='start_date',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(2019), internship.models.max_value_current_year]),
        ),
    ]