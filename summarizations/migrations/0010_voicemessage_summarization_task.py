# Generated by Django 3.2.9 on 2023-08-11 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('summarizations', '0009_voicemessage_bot_telegram_msg_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='voicemessage',
            name='summarization_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='summarizations.summarizationtask', verbose_name='Задача на суммаризацию'),
        ),
    ]
