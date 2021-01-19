# Generated by Django 3.0.7 on 2021-01-19 14:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("iaso", "0074_remove_task_task_name")]

    operations = [
        migrations.AddField(
            model_name="task",
            name="queue_answer",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        )
    ]
