# Generated by Django 3.2.25 on 2024-04-17 19:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_questionresult_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionresult',
            name='time',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='答题时间'),
            preserve_default=False,
        ),
    ]
