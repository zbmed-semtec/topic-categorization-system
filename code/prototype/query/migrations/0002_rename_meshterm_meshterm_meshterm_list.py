# Generated by Django 4.1.2 on 2022-10-26 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('query', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meshterm',
            old_name='meshterm',
            new_name='meshterm_list',
        ),
    ]
