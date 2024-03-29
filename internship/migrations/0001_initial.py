# Generated by Django 2.2.2 on 2019-06-23 06:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('course_name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('dept_code', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='Department code')),
                ('dept_name', models.CharField(max_length=50, verbose_name='Department name')),
            ],
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('staff_no', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=200)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('adm', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=200)),
                ('admission_year', models.DateField()),
                ('course_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=50)),
                ('county', models.CharField(max_length=50)),
                ('town', models.CharField(max_length=50)),
                ('building', models.CharField(max_length=50)),
                ('industrial_supervisor', models.CharField(max_length=50)),
                ('start_date', models.DateField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Student')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_content', models.TextField()),
                ('sent_on', models.DateTimeField(auto_now=True)),
                ('read_status', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Logbook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('date', models.DateField(auto_now=True)),
                ('work_done', models.TextField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Student')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='department',
            field=models.ForeignKey(on_delete=True, to='internship.Department'),
        ),
        migrations.CreateModel(
            name='Coordinator',
            fields=[
                ('staff_no', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=200)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=50)),
                ('branch', models.CharField(blank=True, max_length=50, null=True)),
                ('PO_BOX', models.CharField(blank=True, max_length=50, null=True, verbose_name='P.O BOX')),
                ('application_date', models.DateField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Student')),
            ],
        ),
        migrations.CreateModel(
            name='AllocatedSupervisor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Student')),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Supervisor')),
            ],
        ),
    ]
