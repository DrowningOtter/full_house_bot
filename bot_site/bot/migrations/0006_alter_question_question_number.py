# Generated by Django 5.0 on 2023-12-30 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_question_question_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_number',
            field=models.PositiveIntegerField(default=5),
        ),
    ]
