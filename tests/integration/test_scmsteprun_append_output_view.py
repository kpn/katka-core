import json
from unittest import mock

from django.test import override_settings

import pytest
from requests import HTTPError


@pytest.mark.django_db
class TestUpdateStatusSCMStepRunView:

    endpoint = "/append-build-info-scm-step-run/"

    def test_update_empty_output_valid(self, client, logged_in_user, scm_step_run):
        url = f"{self.endpoint}{scm_step_run.public_identifier}/"
        data = {"status": "success", "build_result": "success", "build_number": 123, "comment": "test{}}"}

        session = mock.Mock()
        overrides = {
            "PIPELINE_RUNNER_SESSION": session,
            "PIPELINE_RUNNER_BASE_URL": "http://override-url/",
            "PIPELINE_UPDATE_STEP_EP": "updatestep/",
        }

        assert scm_step_run.output == ""

        with override_settings(**overrides):
            response = client.patch(url, data, content_type="application/json")

        assert response.status_code == 200
        assert len(session.method_calls) == 1
        assert session.method_calls[0][1][0] == "http://override-url/updatestep/"
        post = session.method_calls[0][2]["json"]
        assert post["user"] == "test_user"
        assert post["step"]["public_identifier"] == str(scm_step_run.public_identifier)
        assert post["step"]["status"] == "success"
        output = json.loads(post["step"]["output"])
        assert output["build_number"] == 123
        assert output["build_result"] == "success"
        assert output["comment"] == "test{}}"

    def test_update_existing_output_valid(self, client, logged_in_user, my_scm_step_run_with_output):
        url = f"{self.endpoint}{my_scm_step_run_with_output.public_identifier}/"
        data = {"status": "success", "build_result": "success", "build_number": 123, "comment": "test"}

        session = mock.Mock()
        overrides = {
            "PIPELINE_RUNNER_SESSION": session,
            "PIPELINE_RUNNER_BASE_URL": "http://override-url/",
            "PIPELINE_UPDATE_STEP_EP": "updatestep/",
        }

        current_output = json.loads(my_scm_step_run_with_output.output)
        assert current_output["build_result"] == "failed"
        assert current_output["build_number"] == 1

        with override_settings(**overrides):
            response = client.patch(url, data, content_type="application/json")

        assert response.status_code == 200
        assert len(session.method_calls) == 1
        assert session.method_calls[0][1][0] == "http://override-url/updatestep/"
        post = session.method_calls[0][2]["json"]
        assert post["user"] == "test_user"
        assert post["step"]["public_identifier"] == str(my_scm_step_run_with_output.public_identifier)
        assert post["step"]["status"] == "success"
        output = json.loads(post["step"]["output"])
        assert output["build_number"] == 123
        assert output["build_result"] == "success"
        assert output["comment"] == "test"
        assert output["field"] == "test"  # current unrelated field was left intact

    def test_update_invalid_current_output(self, client, logged_in_user, my_scm_step_run_with_broken_output):
        url = f"{self.endpoint}{my_scm_step_run_with_broken_output.public_identifier}/"
        data = {"status": "success", "build_result": "success", "build_number": 123, "comment": "test"}

        session = mock.Mock()
        overrides = {
            "PIPELINE_RUNNER_SESSION": session,
            "PIPELINE_RUNNER_BASE_URL": "http://override-url/",
            "PIPELINE_UPDATE_STEP_EP": "updatestep/",
        }

        with override_settings(**overrides):
            response = client.patch(url, data, content_type="application/json")

        assert response.status_code == 500

    def test_partial_update_no_param(self, client, logged_in_user, scm_step_run):
        url = f"{self.endpoint}{scm_step_run.public_identifier}/"
        data = {}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 400
        assert response.json()["status"][0] == "This field is required."
        assert response.json()["build_result"][0] == "This field is required."
        assert response.json()["build_number"][0] == "This field is required."
        assert response.json()["comment"][0] == "This field is required."

    def test_partial_update_invalid_status(self, client, logged_in_user, scm_step_run):
        url = f"{self.endpoint}{scm_step_run.public_identifier}/"
        data = {"status": "bla"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 400
        assert response.json()["status"][0] == '"bla" is not a valid choice.'

    def test_pipeline_runner_fails(self, client, logged_in_user, scm_step_run):
        url = f"{self.endpoint}{scm_step_run.public_identifier}/"
        data = {"status": "success", "build_result": "success", "build_number": 123, "comment": "test"}

        session = mock.Mock()
        response = mock.Mock()
        response.raise_for_status = mock.Mock(side_effect=HTTPError)
        session.post = mock.Mock(return_value=response)
        overrides = {"PIPELINE_RUNNER_SESSION": session}
        with override_settings(**overrides):
            response = client.patch(url, data, content_type="application/json")

        assert response.status_code == 503
