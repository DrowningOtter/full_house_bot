# Generated by Django 5.0 on 2023-12-30 15:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_video_house'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='question',
            name='video',
        ),
        migrations.AddField(
            model_name='photo',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.question'),
        ),
        migrations.AddField(
            model_name='video',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.question'),
        ),
    ]