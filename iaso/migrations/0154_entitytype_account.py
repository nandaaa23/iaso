# Generated by Django 3.2.14 on 2022-08-04 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iaso', '0153_auto_20220804_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitytype',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='iaso.account'),
        ),
    ]
