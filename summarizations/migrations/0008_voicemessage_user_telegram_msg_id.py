# Generated by Django 3.2.9 on 2023-08-11 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summarizations', '0007_auto_20230811_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='voicemessage',
            name='user_telegram_msg_id',
            field=models.PositiveBigIntegerField(default=0, verbose_name='ID сообщения пользователя'),
            preserve_default=False,
        ),
    ]