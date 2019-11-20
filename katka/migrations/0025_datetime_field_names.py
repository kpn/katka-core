# Generated by Django 2.2.7 on 2019-11-05 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("katka", "0024_scmsteprun_started_ended"),
    ]

    operations = [
        migrations.RenameField(model_name="application", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="application", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="applicationmetadata", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="applicationmetadata", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="credential", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="credential", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="credentialsecret", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="credentialsecret", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="project", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="project", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="scmpipelinerun", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="scmpipelinerun", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="scmrelease", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="scmrelease", old_name="ended", new_name="ended_at",),
        migrations.RenameField(model_name="scmrelease", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="scmrelease", old_name="started", new_name="started_at",),
        migrations.RenameField(model_name="scmrepository", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="scmrepository", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="scmservice", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="scmservice", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="scmsteprun", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="scmsteprun", old_name="ended", new_name="ended_at",),
        migrations.RenameField(model_name="scmsteprun", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="team", old_name="created", new_name="created_at",),
        migrations.RenameField(model_name="team", old_name="modified", new_name="modified_at",),
        migrations.RenameField(model_name="scmsteprun", old_name="started", new_name="started_at",),
    ]
