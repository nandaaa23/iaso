# Generated by Django 4.2.14 on 2024-08-07 08:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polio", "0190_auto_20240807_0829"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chronogramtask",
            name="description",
        ),
        migrations.RemoveField(
            model_name="chronogramtemplatetask",
            name="description",
        ),
        migrations.RenameField(
            model_name="chronogramtask",
            old_name="description_new_en",
            new_name="description_en",
        ),
        migrations.RenameField(
            model_name="chronogramtask",
            old_name="description_new_fr",
            new_name="description_fr",
        ),
        migrations.RenameField(
            model_name="chronogramtemplatetask",
            old_name="description_new_en",
            new_name="description_en",
        ),
        migrations.RenameField(
            model_name="chronogramtemplatetask",
            old_name="description_new_fr",
            new_name="description_fr",
        ),
        migrations.AlterField(
            model_name="chronogramtask",
            name="description_en",
            field=models.TextField(max_length=300, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="chronogramtask",
            name="description_fr",
            field=models.TextField(blank=True, max_length=300, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="chronogramtemplatetask",
            name="description_en",
            field=models.TextField(max_length=300, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="chronogramtemplatetask",
            name="description_fr",
            field=models.TextField(blank=True, max_length=300, verbose_name="description"),
        ),
    ]
