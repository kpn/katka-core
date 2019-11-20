from uuid import UUID

import pytest


@pytest.mark.django_db
class TestSCMServiceViewSet:
    def test_list_unauthenticated(self, client, scm_service):
        response = client.get("/scm-services/")
        assert response.status_code == 403

    def test_list(self, client, logged_in_user, scm_service):
        response = client.get("/scm-services/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        assert parsed[0]["scm_service_type"] == "bitbucket"
        assert parsed[0]["server_url"] == "www.example.com"
        UUID(parsed[0]["public_identifier"])  # should not raise

    def test_list_excludes_inactive(self, client, logged_in_user, deactivated_scm_service):
        response = client.get("/scm-services/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 0

    def test_get(self, client, logged_in_user, scm_service):
        response = client.get(f"/scm-services/{scm_service.public_identifier}/")
        assert response.status_code == 200
        parsed = response.json()
        assert parsed["scm_service_type"] == "bitbucket"
        assert parsed["server_url"] == "www.example.com"
        UUID(parsed["public_identifier"])  # should not raise

    def test_get_excludes_inactive(self, client, logged_in_user, deactivated_scm_service):
        response = client.get(f"/scm-services/{deactivated_scm_service.public_identifier}/")
        assert response.status_code == 404

    def test_delete_not_allowed(self, client, logged_in_user, scm_service):
        response = client.delete(f"/scm-services/{scm_service.public_identifier}/")
        assert response.status_code == 405

    def test_update_not_allowed(self, client, logged_in_user, scm_service):
        data = {"scm_service_type": "git", "server_url": "www.example.org"}
        response = client.put(f"/scm-services/{scm_service.public_identifier}/", data, content_type="application/json")
        assert response.status_code == 405

    def test_partial_update_not_allowed(self, client, logged_in_user, scm_service):
        data = {"scm_service_type": "git"}
        response = client.patch(
            f"/scm-services/{scm_service.public_identifier}/", data, content_type="application/json"
        )
        assert response.status_code == 405

    def test_create_not_allowed(self, client, logged_in_user, scm_service):
        data = {"scm_service_type": "bitbucket", "server_url": "www.example.com"}
        response = client.post(f"/scm-services/", data, content_type="application/json")
        assert response.status_code == 405
