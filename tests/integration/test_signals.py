from django.test import override_settings

import mock
import pytest
from katka import constants
from katka.fields import username_on_model
from katka.models import SCMPipelineRun, SCMStepRun


@pytest.mark.django_db
class TestSCMStepsRunSignals:
    def test_steps_updated(self, scm_step_run, scm_pipeline_run):
        assert scm_pipeline_run.steps_total == 1
        assert scm_pipeline_run.steps_completed == 0
        assert scm_pipeline_run.modified_username == 'initial'
        assert scm_step_run.status == constants.STEP_STATUS_NOT_STARTED

        scm_step_run.status = constants.STEP_STATUS_SUCCESS
        with username_on_model(SCMStepRun, 'signal_tester'):
            scm_step_run.save()

        assert scm_pipeline_run.steps_total == 1
        assert scm_pipeline_run.steps_completed == 1
        assert scm_pipeline_run.modified_username == 'signal_tester'


@pytest.mark.django_db
class TestSCMPipelineRunSignals:
    def test_notify_post(self, scm_step_run, scm_pipeline_run):
        session = mock.MagicMock()
        overrides = {
            'PIPELINE_CHANGE_NOTIFICATION_SESSION': session,
            'PIPELINE_CHANGE_NOTIFICATION_URL': 'http://override-url/',
        }
        with override_settings(**overrides):
            with username_on_model(SCMPipelineRun, 'signal_tester'):
                scm_pipeline_run.status = constants.PIPELINE_STATUS_IN_PROGRESS
                scm_pipeline_run.save()

            with username_on_model(SCMStepRun, 'signal_tester'):
                scm_step_run.status = constants.STEP_STATUS_IN_PROGRESS
                scm_step_run.save()

                scm_step_run.status = constants.STEP_STATUS_FAILED
                scm_step_run.save()

            # should be called twice:
            # - once for the status update of the pipeline (from initializing to "in progress"), and
            # - once because the number of completed steps changed
            # but not a third time, because:
            # - the step status changed from non-final ("not started") to non-final ("in progress") so the
            #   number of completed steps in the pipeline did not change
            assert session.post.call_args_list == [
                mock.call('http://override-url/', json={'public_identifier': str(scm_pipeline_run.public_identifier)}),
                mock.call('http://override-url/', json={'public_identifier': str(scm_pipeline_run.public_identifier)}),
            ]

    def test_initializing(self, scm_step_run, scm_pipeline_run):
        session = mock.MagicMock()
        overrides = {
            'PIPELINE_CHANGE_NOTIFICATION_SESSION': session,
            'PIPELINE_CHANGE_NOTIFICATION_URL': 'http://override-url/',
        }
        with override_settings(**overrides):
            with username_on_model(SCMStepRun, 'signal_tester'):
                scm_step_run.status = constants.STEP_STATUS_IN_PROGRESS
                scm_step_run.save()

                scm_step_run.status = constants.STEP_STATUS_FAILED
                scm_step_run.save()

            # should not be called because the pipeline is still initializing
            assert session.post.call_args_list == []
