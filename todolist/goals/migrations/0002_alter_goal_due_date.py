# Generated by Django 4.1.2 on 2022-10-24 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дедлайн'),
        ),
    ]