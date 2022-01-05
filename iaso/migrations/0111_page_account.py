# Generated by Django 3.1.14 on 2022-01-05 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iaso', '0110_make_readonlyrole'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='iaso.account'),
        ),
    ]
