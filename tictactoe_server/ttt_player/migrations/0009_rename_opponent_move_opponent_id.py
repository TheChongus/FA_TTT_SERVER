# Generated by Django 5.0.4 on 2024-04-16 22:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ttt_player', '0008_rename_opponent_move_opponent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='move',
            old_name='opponent',
            new_name='opponent_id',
        ),
    ]
