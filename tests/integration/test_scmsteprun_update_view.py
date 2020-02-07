from unittest import mock

from django.test import override_settings

import pytest
from requests import HTTPError


@pytest.mark.django_db
class TestUpdateStatusSCMStepRunView:
    def test_partial_update_status_valid(self, client, logged_in_user, scm_step_run):
        url = f"/update-scm-step-run/{scm_step_run.public_identifier}/"
        data = {"status": "success"}

        session = mock.Mock()
        overrides = {"PIPELINE_RUNNER_SESSION": session}
        with override_settings(**overrides):
            response = client.patch(url, data, content_type="application/json")

        assert response.status_code == 200
        assert len(session.method_calls) == 1
        post = session.method_calls[0][2]["json"]
        assert post["user"] == "test_user"
        assert post["step"]["public_identifier"] == scm_step_run.public_identifier
        assert post["step"]["status"] == "success"

    def test_partial_update_no_param(self, client, logged_in_user, scm_step_run):
        url = f"/update-scm-step-run/{scm_step_run.public_identifier}/"
        data = {}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 400
        assert response.json()["status"][0] == "This field is required."

    def test_partial_update_invalid_status(self, client, logged_in_user, scm_step_run):
        url = f"/update-scm-step-run/{scm_step_run.public_identifier}/"
        data = {"status": "bla"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 400
        assert response.json()["status"][0] == '"bla" is not a valid choice.'

    def test_pipeline_runner_fails(self, client, logged_in_user, scm_step_run):
        url = f"/update-scm-step-run/{scm_step_run.public_identifier}/"
        data = {"status": "success"}

        session = mock.Mock()
        response = mock.Mock()
        response.raise_for_status = mock.Mock(side_effect=HTTPError)
        session.post = mock.Mock(return_value=response)
        overrides = {"PIPELINE_RUNNER_SESSION": session}
        with override_settings(**overrides):
            response = client.patch(url, data, content_type="application/json")

        assert response.status_code == 503
