# Generated by Django 3.2.25 on 2024-04-16 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20240416_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='words',
            field=models.CharField(default='我思故我在', max_length=255, verbose_name='个性前面'),
        ),
    ]
