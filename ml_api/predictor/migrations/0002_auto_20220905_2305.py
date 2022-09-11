# Generated by Django 3.2.15 on 2022-09-05 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelsink',
            name='algorithm',
            field=models.CharField(blank=True, default=None, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='modelsink',
            name='status',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='modelsink',
            name='url_encoder',
            field=models.URLField(blank=True, default=None, max_length=1000, null=True),
        ),
    ]