# Generated by Django 3.2.22 on 2023-11-22 14:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polio", "0152_notification_notificationimport"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="vdpv_nucleotide_diff_sabin2",
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
