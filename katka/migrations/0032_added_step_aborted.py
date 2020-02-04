# Generated by Django 2.2.7 on 2020-02-03 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("katka", "0031_application_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scmsteprun",
            name="status",
            field=models.CharField(
                choices=[
                    ("not started", "not started"),
                    ("in progress", "in progress"),
                    ("waiting", "waiting"),
                    ("skipped", "skipped"),
                    ("aborted", "aborted"),
                    ("failed", "failed"),
                    ("success", "success"),
                ],
                default="not started",
                max_length=30,
            ),
        ),
    ]