from django.utils.dateparse import parse_datetime

import pytest
from katka import constants
from katka.models import SCMRelease
from katka.signals import close_release_if_pipeline_finished


@pytest.mark.django_db
class TestCloseRelease:
    @staticmethod
    def _assert_release_success_with_name(name):
        assert SCMRelease.objects.count() == 1
        release = SCMRelease.objects.first()
        assert release.name == name
        assert release.status == constants.RELEASE_STATUS_SUCCESS
        assert release.started_at is not None
        assert release.ended_at is not None

    @staticmethod
    def _assert_release_has_status(status):
        assert SCMRelease.objects.count() == 1
        release = SCMRelease.objects.first()
        assert release.status == status

    @staticmethod
    def _assert_release_has_start_and_end_date(started_at=None, ended_at=None):
        assert SCMRelease.objects.count() == 1
        release = SCMRelease.objects.first()
        if started_at:
            assert release.started_at == parse_datetime(started_at)
        else:
            assert release.started_at is None

        if ended_at:
            assert release.ended_at == parse_datetime(ended_at)
        else:
            assert release.ended_at is None

    def test_do_nothing_if_pipeline_run_status_not_finished(self, scm_pipeline_run, scm_release_with_pipeline_run):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_IN_PROGRESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        # nothing has changed
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

    def test_all_steps_are_success_but_no_start_tag_found(
        self, scm_pipeline_run, scm_release_with_pipeline_run, scm_step_run_success_list
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

    def test_all_steps_are_success_but_no_end_tag_found(
        self, scm_pipeline_run, scm_release_with_pipeline_run, scm_step_run_success_list_with_start_tag
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

    def test_all_steps_are_success_but_no_open_release_found(self, scm_pipeline_run_with_no_open_release):

        result_status = close_release_if_pipeline_finished(scm_pipeline_run_with_no_open_release)
        assert result_status is None

    def test_all_steps_are_success_with_start_and_end_tag(
        self, scm_release_with_pipeline_run, scm_pipeline_run, scm_step_run_success_list_with_start_end_tags
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status == constants.PIPELINE_STATUS_SUCCESS

        self._assert_release_success_with_name("1.0.0")
        self._assert_release_has_start_and_end_date("2018-11-11 08:45:30+00:00", "2018-11-11 09:15:41+00:00")

    def test_one_failed_step_between_start_end_tags(
        self, scm_pipeline_run, scm_release_with_pipeline_run, scm_step_run_one_failed_step_list_with_start_end_tags
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_FAILED
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status == constants.RELEASE_STATUS_FAILED

        self._assert_release_has_status(constants.RELEASE_STATUS_FAILED)
        self._assert_release_has_start_and_end_date("2018-11-11 08:45:30+00:00", "2018-11-11 09:15:41+00:00")

    def test_one_failed_step_before_start_tag(
        self, scm_pipeline_run, scm_release_with_pipeline_run, scm_step_run_one_failed_step_before_start_tag
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_FAILED
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)
        self._assert_release_has_start_and_end_date(None, None)

    def test_one_failed_step_after_end_tag(
        self, scm_pipeline_run, scm_release_with_pipeline_run, scm_step_run_one_failed_step_after_end_tag
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_FAILED
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status == constants.RELEASE_STATUS_SUCCESS
        self._assert_release_success_with_name("1.0.0")
        self._assert_release_has_start_and_end_date("2018-11-11 08:45:30+00:00", "2018-11-11 09:15:41+00:00")

    def test_fails_if_version_not_present_in_context(
        self, scm_pipeline_run, scm_release_with_pipeline_run, scm_step_run_without_version_output
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)
        self._assert_release_has_start_and_end_date(None, None)

    def test_output_with_broken_json_does_not_break_release(
        self, scm_pipeline_run, scm_release_with_pipeline_run, scm_step_run_with_broken_output
    ):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status == constants.PIPELINE_STATUS_SUCCESS

        self._assert_release_success_with_name("1.0.0")
        self._assert_release_has_start_and_end_date("2018-11-11 08:45:30+00:00", "2018-11-11 09:15:41+00:00")
