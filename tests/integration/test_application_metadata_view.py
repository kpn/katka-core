from uuid import UUID

import pytest
from katka import models


@pytest.mark.django_db
class TestApplicationMetadataList:
    def test_authenticated(self, client, logged_in_user, application, metadata):
        response = client.get(f"/applications/{application.public_identifier}/metadata/")
        assert response.status_code == 200
        parsed = response.json()
        assert len(parsed) == 1
        metadata = parsed[0]
        assert metadata["key"] == "ci"
        assert metadata["value"] == "the-team"
        assert UUID(metadata["application"]) == application.public_identifier


@pytest.mark.django_db
class TestApplicationMetadataGet:
    def test_unauthenticated(self, client, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}"
        response = client.get(url)
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}/"
        response = client.get(url)
        assert response.status_code == 200
        metadata = response.json()
        assert metadata["key"] == "ci"
        assert metadata["value"] == "the-team"
        assert UUID(metadata["application"]) == application.public_identifier

    def test_non_existent_application(self, client, logged_in_user, application, metadata):
        url = f"/applications/00000000-0000-0000-0000-000000000000/metadata/{metadata.key}/"
        response = client.get(url)
        assert response.status_code == 404

    def test_non_existent_key(self, client, logged_in_user, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/wrong_key/"
        response = client.get(url)
        assert response.status_code == 404

    def test_not_my_metadata(self, client, logged_in_user, not_my_application, not_my_metadata):
        url = f"/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/"
        response = client.get(url)
        assert response.status_code == 404

    def test_excludes_inactive(self, client, logged_in_user, application, deactivated_metadata):
        url = f"/applications/{application.public_identifier}/metadata/{deactivated_metadata.key}/"
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestApplicationMetadataDelete:
    def test_unauthenticated(self, client, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}"
        response = client.delete(url)
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}/"
        response = client.delete(url)
        assert response.status_code == 204
        s = models.ApplicationMetadata.objects.get(key=metadata.key, application=application)
        assert s.deleted is True

    def test_non_existent(self, client, logged_in_user, application, metadata):
        before_count = models.ApplicationMetadata.objects.count()
        url = f"/applications/00000000-0000-0000-0000-000000000000/metadata/{metadata.key}/"
        response = client.delete(url)
        assert response.status_code == 404
        assert models.ApplicationMetadata.objects.count() == before_count

    def test_deactivated(self, client, logged_in_user, deactivated_metadata):
        url = f"/applications/{deactivated_metadata.application.public_identifier}/metadata/{deactivated_metadata.key}/"
        response = client.delete(url)
        assert response.status_code == 404
        s = models.ApplicationMetadata.objects.get(
            key=deactivated_metadata.key, application=deactivated_metadata.application
        )
        assert s.deleted is True

    def test_not_my_metadata(self, client, logged_in_user, not_my_application, not_my_metadata):
        url = f"/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/"
        response = client.delete(url)
        assert response.status_code == 404
        s = models.ApplicationMetadata.objects.get(key=not_my_metadata.key, application=not_my_application)
        assert s.deleted is False


@pytest.mark.django_db
class TestApplicationMetadataUpdate:
    def test_unauthenticated(self, client, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}"
        data = {"key": "a_key", "value": "v1"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}/"
        data = {"key": metadata.key, "value": "new value"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 200
        s = models.ApplicationMetadata.objects.get(key=metadata.key, application=application)
        assert s.value == "new value"

    def test_non_existent_application(self, client, logged_in_user, application, metadata):
        url = f"/applications/00000000-0000-0000-0000-000000000000/metadata/{metadata.key}/"
        data = {"key": "a_key", "value": "v1"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_non_existent_key(self, client, logged_in_user, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/wrong_key/"
        data = {"key": "a_key", "value": "v1"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_deactivated(self, client, logged_in_user, deactivated_metadata):
        url = f"/applications/{deactivated_metadata.application.public_identifier}/metadata/{deactivated_metadata.key}/"
        data = {"key": deactivated_metadata.key, "value": "v1"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.ApplicationMetadata.objects.get(
            key=deactivated_metadata.key, application=deactivated_metadata.application
        )
        assert s.value == "the-team-2"

    def test_not_my_metadata(self, client, logged_in_user, not_my_application, not_my_metadata):
        url = f"/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/"
        data = {"key": not_my_metadata.key, "value": "v1"}
        response = client.put(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.ApplicationMetadata.objects.get(key=not_my_metadata.key, application=not_my_application)
        assert s.value == "the-team-not-mine"


@pytest.mark.django_db
class TestApplicationMetadataPartialUpdate:
    def test_unauthenticated(self, client, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}"
        data = {"value": "v1"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_authenticated(self, client, logged_in_user, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/{metadata.key}/"
        data = {"value": "new value"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 200
        s = models.ApplicationMetadata.objects.get(key=metadata.key, application=application)
        assert s.value == "new value"

    def test_non_existent_application(self, client, logged_in_user, application, metadata):
        url = f"/applications/00000000-0000-0000-0000-000000000000/metadata/{metadata.key}/"
        data = {"value": "v1"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_non_existent_key(self, client, logged_in_user, application, metadata):
        url = f"/applications/{application.public_identifier}/metadata/wrong_key/"
        data = {"value": "v1"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404

    def test_deactivated(self, client, logged_in_user, deactivated_metadata):
        url = f"/applications/{deactivated_metadata.application.public_identifier}/metadata/{deactivated_metadata.key}/"
        data = {"value": "v1"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.ApplicationMetadata.objects.get(
            key=deactivated_metadata.key, application=deactivated_metadata.application
        )
        assert s.value == "the-team-2"

    def test_not_my_metadata(self, client, logged_in_user, not_my_application, not_my_metadata):
        url = f"/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/"
        data = {"value": "v1"}
        response = client.patch(url, data, content_type="application/json")
        assert response.status_code == 404
        s = models.ApplicationMetadata.objects.get(key=not_my_metadata.key, application=not_my_application)
        assert s.value == "the-team-not-mine"


@pytest.mark.django_db
class TestApplicationMetadataCreate:
    def test_unauthenticated(self, client, team, application):
        url = f"/applications/{application.public_identifier}/metadata/"
        data = {"key": "a_key", "value": "v1"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 403

    def test_authenticated(self, client, logged_in_user, team, application):
        url = f"/applications/{application.public_identifier}/metadata/"
        data = {"key": "a_key", "value": "v1"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 201
        s = models.ApplicationMetadata.objects.get(key="a_key", application=application)
        assert s.value == "v1"

    def test_non_existent_application(self, client, logged_in_user, team, application):
        url = f"/applications/00000000-0000-0000-0000-000000000000/metadata/"
        data = {"key": "a_key", "value": "v1"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 403

    def test_deactivated(self, client, logged_in_user, team, deactivated_application):
        before_count = models.ApplicationMetadata.objects.count()
        url = f"/applications/{deactivated_application.public_identifier}/metadata/"
        data = {"key": "a_key", "value": "v1"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 403
        assert models.ApplicationMetadata.objects.count() == before_count

    def test_not_my_metadata(self, client, logged_in_user, team, not_my_application):
        before_count = models.ApplicationMetadata.objects.count()
        url = f"/applications/{not_my_application.public_identifier}/metadata/"
        data = {"key": "a_key", "value": "v1"}
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == 403
        assert models.ApplicationMetadata.objects.count() == before_count
