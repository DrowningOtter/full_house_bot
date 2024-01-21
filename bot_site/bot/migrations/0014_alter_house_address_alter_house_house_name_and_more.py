# Generated by Django 5.0 on 2024-01-20 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0013_alter_house_house_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='address',
            field=models.CharField(max_length=100, verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='house',
            name='house_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='House name'),
        ),
        migrations.AlterField(
            model_name='house',
            name='house_number',
            field=models.PositiveIntegerField(verbose_name='House number'),
        ),
    ]
