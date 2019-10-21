import pytest
from katka import constants
from katka.models import SCMRelease
from katka.signals import close_release_if_pipeline_finished


@pytest.mark.django_db
class TestCloseRelease:

    @staticmethod
    def _assert_release_has_status(status):
        assert SCMRelease.objects.count() == 1
        release = SCMRelease.objects.first()
        assert release.status == status

    def test_do_nothing_if_pipeline_run_status_not_finished(self, scm_pipeline_run):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_IN_PROGRESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        # nothing has changed
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

    def test_all_steps_are_success_but_no_start_tag_found(self, scm_pipeline_run, scm_step_run_success_list):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

    def test_all_steps_are_success_but_no_end_tag_found(self, scm_pipeline_run,
                                                        scm_step_run_success_list_with_start_tag):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

    def test_all_steps_are_success_but_no_open_release_found(self, scm_pipeline_run_with_no_open_release):

        result_status = close_release_if_pipeline_finished(scm_pipeline_run_with_no_open_release)
        assert result_status is None

    def test_all_steps_are_success_with_start_and_end_tag(self, scm_pipeline_run,
                                                          scm_step_run_success_list_with_start_end_tags):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_SUCCESS
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status == constants.PIPELINE_STATUS_SUCCESS

        self._assert_release_has_status(constants.RELEASE_STATUS_SUCCESS)

    def test_one_failed_step_between_start_end_tags(self, scm_pipeline_run,
                                                    scm_step_run_one_failed_step_list_with_start_end_tags):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_FAILED
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status == constants.RELEASE_STATUS_FAILED

        self._assert_release_has_status(constants.RELEASE_STATUS_FAILED)

    def test_one_failed_step_before_start_tag(self, scm_pipeline_run,
                                              scm_step_run_one_failed_step_before_start_tag):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_FAILED
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status is None

        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

    def test_one_failed_step_after_end_tag(self, scm_pipeline_run,
                                           scm_step_run_one_failed_step_after_end_tag):
        self._assert_release_has_status(constants.RELEASE_STATUS_IN_PROGRESS)

        scm_pipeline_run.status = constants.PIPELINE_STATUS_FAILED
        result_status = close_release_if_pipeline_finished(scm_pipeline_run)
        assert result_status == constants.RELEASE_STATUS_SUCCESS

        self._assert_release_has_status(constants.RELEASE_STATUS_SUCCESS)
