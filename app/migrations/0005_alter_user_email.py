# Generated by Django 3.2.25 on 2024-04-17 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_user_tel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(default='123@123.123', max_length=128, verbose_name='邮箱'),
        ),
    ]
