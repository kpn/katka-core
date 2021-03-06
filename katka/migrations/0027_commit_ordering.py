# Generated by Django 2.2.6 on 2019-11-13 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("katka", "0026_scmsteprun_step_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="scmpipelinerun",
            name="first_parent_hash",
            field=models.CharField(
                blank=True,
                help_text="Commit hash of first parent commit, to determine order of commits. First commit has none.",
                max_length=64,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="scmpipelinerun",
            name="status",
            field=models.CharField(
                choices=[
                    ("initializing", "initializing"),
                    ("queued", "queued"),
                    ("in progress", "in progress"),
                    ("failed", "failed"),
                    ("success", "success"),
                    ("skipped", "skipped"),
                ],
                default="initializing",
                max_length=30,
            ),
        ),
    ]
