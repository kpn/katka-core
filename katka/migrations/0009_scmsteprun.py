# Generated by Django 2.1.7 on 2019-02-20 06:55

import uuid

import django.db.models.deletion
from django.db import migrations, models

import katka.fields


class Migration(migrations.Migration):

    dependencies = [
        ("katka", "0008_scmpipelinerun"),
    ]

    operations = [
        migrations.CreateModel(
            name="SCMStepRun",
            fields=[
                ("created", models.DateTimeField(auto_now_add=True)),
                ("created_username", katka.fields.AutoUsernameField(max_length=50)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("modified_username", katka.fields.AutoUsernameField(max_length=50)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "public_identifier",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("slug", katka.fields.KatkaSlugField(max_length=30)),
                ("name", models.CharField(max_length=100)),
                ("stage", models.CharField(max_length=100)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("failed", "failed"),
                            ("success", "success"),
                            ("in progress", "in progress"),
                            ("blocked", "blocked"),
                            ("skipped", "skipped"),
                        ],
                        default="in progress",
                        max_length=30,
                    ),
                ),
                ("output", models.TextField(blank=True)),
                (
                    "scm_pipeline_run",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="katka.SCMPipelineRun"),
                ),
            ],
            options={"abstract": False,},
        ),
    ]
