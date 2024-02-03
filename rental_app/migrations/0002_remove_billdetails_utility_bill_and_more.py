# Generated by Django 4.2.7 on 2024-02-03 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billdetails',
            name='utility_bill',
        ),
        migrations.AddField(
            model_name='billdetails',
            name='utility_bills_consider_from_date',
            field=models.CharField(default='2024,01,01', max_length=20),
        ),
        migrations.AddField(
            model_name='billdetails',
            name='utility_bills_consider_to_date',
            field=models.CharField(default='2024,01,31', max_length=20),
        ),
    ]