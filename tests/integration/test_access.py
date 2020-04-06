import pytest
from tests.integration.conftest import anonymous_client, scoped_client, sys_user_client, user_client


@pytest.mark.django_db
class TestList:
    @pytest.mark.parametrize(
        ("client_ctx_manager", "url", "http_status", "expected_length"),
        [
            (anonymous_client, "/applications/", 403, None),
            (anonymous_client, "/applications/{application.public_identifier}/metadata/", 403, None),
            (anonymous_client, "/teams/", 403, None),
            (anonymous_client, "/projects/", 403, None),
            (anonymous_client, "/credentials/", 403, None),
            (anonymous_client, "/credentials/{credential.public_identifier}/secrets/", 403, None),
            (anonymous_client, "/scm-services/", 403, None),
            (anonymous_client, "/scm-repositories/", 403, None),
            (anonymous_client, "/scm-pipeline-runs/", 403, None),
            (anonymous_client, "/scm-step-runs/", 403, None),
            (anonymous_client, "/scm-releases/", 403, None),
            (user_client, "/applications/", 200, 2),
            (user_client, "/applications/{application.public_identifier}/metadata/", 200, 1),
            (user_client, "/teams/", 200, 2),
            (user_client, "/projects/", 200, 2),
            (user_client, "/credentials/", 200, 3),  # 3 because of my_other_teams_credential
            (user_client, "/credentials/{credential.public_identifier}/secrets/", 200, 1),  # only one per credential
            (user_client, "/scm-services/", 200, 2),
            (user_client, "/scm-repositories/", 200, 2),
            (user_client, "/scm-pipeline-runs/", 200, 4),
            (user_client, "/scm-step-runs/", 200, 2),
            (user_client, "/scm-releases/", 200, 2),
            (sys_user_client, "/applications/", 200, 2),
            (sys_user_client, "/applications/{application.public_identifier}/metadata/", 200, 1),
            (sys_user_client, "/teams/", 200, 2),
            (sys_user_client, "/projects/", 200, 2),
            (sys_user_client, "/credentials/", 200, 3),  # 3 because of my_other_teams_credential
            (
                sys_user_client,
                "/credentials/{credential.public_identifier}/secrets/",
                200,
                1,
            ),  # only one per credential
            (sys_user_client, "/scm-services/", 200, 2),
            (sys_user_client, "/scm-repositories/", 200, 2),
            (sys_user_client, "/scm-pipeline-runs/", 200, 4),
            (sys_user_client, "/scm-step-runs/", 200, 2),
            (sys_user_client, "/scm-releases/", 200, 2),
            (scoped_client, "/applications/", 200, 3),
            (scoped_client, "/applications/{application.public_identifier}/metadata/", 200, 1,),
            (scoped_client, "/teams/", 200, 3),
            (scoped_client, "/projects/", 200, 3),
            (scoped_client, "/credentials/", 200, 4),  # 4 because of my_other_teams_credential
            (scoped_client, "/credentials/{credential.public_identifier}/secrets/", 200, 1),  # only one per credential
            (scoped_client, "/scm-services/", 200, 2),
            (scoped_client, "/scm-repositories/", 200, 3),
            (scoped_client, "/scm-pipeline-runs/", 200, 5),
            (scoped_client, "/scm-step-runs/", 200, 3),
            (scoped_client, "/scm-releases/", 200, 3),
        ],
    )
    def test_list(self, client_ctx_manager, url, http_status, expected_length, most_models):
        with client_ctx_manager() as client:
            url = url.format(**most_models)
            response = client.get(url)
            assert response.status_code == http_status
            if expected_length is not None:
                parsed = response.json()
                assert len(parsed) == expected_length


@pytest.mark.django_db
class TestGet:
    @pytest.mark.parametrize(
        ("client_ctx_manager", "url", "http_status"),
        [
            (anonymous_client, "/applications/{application.public_identifier}/", 403),
            (anonymous_client, "/applications/unknown/", 403),
            (anonymous_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 403),
            (anonymous_client, "/teams/{team.public_identifier}/", 403),
            (anonymous_client, "/projects/{project.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 403),
            (anonymous_client, "/scm-services/{service.public_identifier}/", 403),
            (anonymous_client, "/scm-repositories/{repository.public_identifier}/", 403),
            (anonymous_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 403),
            (anonymous_client, "/scm-step-runs/{step_run.public_identifier}/", 403),
            (anonymous_client, "/scm-releases/{release.public_identifier}/", 403),
            (user_client, "/applications/{application.public_identifier}/", 200),
            (user_client, "/applications/unknown/", 404),
            (user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 200),
            (user_client, "/teams/{team.public_identifier}/", 200),
            (user_client, "/projects/{project.public_identifier}/", 200),
            (user_client, "/credentials/{credential.public_identifier}/", 200),
            (user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 200),
            (user_client, "/scm-services/{service.public_identifier}/", 200),
            (user_client, "/scm-repositories/{repository.public_identifier}/", 200),
            (user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 200),
            (user_client, "/scm-step-runs/{step_run.public_identifier}/", 200),
            (user_client, "/scm-releases/{release.public_identifier}/", 200),
            # check user_client, but this time with everything that does not belong to that user
            (user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (user_client, "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/", 404),
            (user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (user_client, "/scm-releases/{not_my_release.public_identifier}/", 404),
            (sys_user_client, "/applications/{application.public_identifier}/", 200),
            (sys_user_client, "/applications/unknown/", 404),
            (sys_user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 200),
            (sys_user_client, "/teams/{team.public_identifier}/", 200),
            (sys_user_client, "/projects/{project.public_identifier}/", 200),
            (sys_user_client, "/credentials/{credential.public_identifier}/", 200),
            (sys_user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 200),
            (sys_user_client, "/scm-services/{service.public_identifier}/", 200),
            (sys_user_client, "/scm-repositories/{repository.public_identifier}/", 200),
            (sys_user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 200),
            (sys_user_client, "/scm-step-runs/{step_run.public_identifier}/", 200),
            (sys_user_client, "/scm-releases/{release.public_identifier}/", 200),
            # check sys_user_client, but this time with everything that does not belong to that user
            (sys_user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (
                sys_user_client,
                "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/",
                404,
            ),
            (sys_user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (sys_user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (sys_user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (sys_user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (sys_user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (sys_user_client, "/scm-releases/{not_my_release.public_identifier}/", 404),
            (scoped_client, "/applications/{application.public_identifier}/", 200),
            (scoped_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 200),
            (scoped_client, "/teams/{team.public_identifier}/", 200),
            (scoped_client, "/projects/{project.public_identifier}/", 200),
            (scoped_client, "/credentials/{credential.public_identifier}/", 200),
            (scoped_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 200),
            (scoped_client, "/scm-services/{service.public_identifier}/", 200),
            (scoped_client, "/scm-repositories/{repository.public_identifier}/", 200),
            (scoped_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 200),
            (scoped_client, "/scm-step-runs/{step_run.public_identifier}/", 200),
            (scoped_client, "/scm-releases/{release.public_identifier}/", 200),
        ],
    )
    def test_get(self, client_ctx_manager, url, http_status, most_models):
        with client_ctx_manager() as client:
            url = url.format(**most_models)
            response = client.get(url)
            assert response.status_code == http_status


@pytest.mark.django_db
class TestDelete:
    @pytest.mark.parametrize(
        ("client_ctx_manager", "url", "http_status"),
        [
            (anonymous_client, "/applications/{application.public_identifier}/", 403),
            (anonymous_client, "/applications/unknown/", 403),
            (anonymous_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 403),
            (anonymous_client, "/teams/{team.public_identifier}/", 403),
            (anonymous_client, "/projects/{project.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 403),
            (anonymous_client, "/scm-services/{service.public_identifier}/", 403),
            (anonymous_client, "/scm-repositories/{repository.public_identifier}/", 403),
            (anonymous_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 403),
            (anonymous_client, "/scm-step-runs/{step_run.public_identifier}/", 403),
            (anonymous_client, "/scm-releases/{release.public_identifier}/", 403),
            (user_client, "/applications/{application.public_identifier}/", 204),
            (user_client, "/applications/unknown/", 404),
            (user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 204),
            (user_client, "/teams/{team.public_identifier}/", 204),
            (user_client, "/projects/{project.public_identifier}/", 204),
            (user_client, "/credentials/{credential.public_identifier}/", 204),
            (user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 204),
            (user_client, "/scm-services/{service.public_identifier}/", 405),
            (user_client, "/scm-repositories/{repository.public_identifier}/", 204),
            (user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 204),
            (user_client, "/scm-step-runs/{step_run.public_identifier}/", 204),
            (user_client, "/scm-releases/{release.public_identifier}/", 405),
            # check user_client, but this time with everything that does not belong to that user
            (user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (user_client, "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/", 404),
            (user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (user_client, "/scm-releases/{not_my_release.public_identifier}/", 405),
            (sys_user_client, "/applications/{application.public_identifier}/", 204),
            (sys_user_client, "/applications/unknown/", 404),
            (sys_user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 204),
            (sys_user_client, "/teams/{team.public_identifier}/", 204),
            (sys_user_client, "/projects/{project.public_identifier}/", 204),
            (sys_user_client, "/credentials/{credential.public_identifier}/", 204),
            (sys_user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 204),
            (sys_user_client, "/scm-services/{service.public_identifier}/", 405),
            (sys_user_client, "/scm-repositories/{repository.public_identifier}/", 204),
            (sys_user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 204),
            (sys_user_client, "/scm-step-runs/{step_run.public_identifier}/", 204),
            (sys_user_client, "/scm-releases/{release.public_identifier}/", 405),
            # check sys_user_client, but this time with everything that does not belong to that user
            (sys_user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (
                sys_user_client,
                "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/",
                404,
            ),
            (sys_user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (sys_user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (sys_user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (sys_user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (sys_user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (sys_user_client, "/scm-releases/{not_my_release.public_identifier}/", 405),
            (scoped_client, "/applications/{application.public_identifier}/", 204),
            (scoped_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 204),
            (scoped_client, "/teams/{team.public_identifier}/", 204),
            (scoped_client, "/projects/{project.public_identifier}/", 204),
            (scoped_client, "/credentials/{credential.public_identifier}/", 204),
            (scoped_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 204),
            (scoped_client, "/scm-services/{service.public_identifier}/", 405),
            (scoped_client, "/scm-repositories/{repository.public_identifier}/", 204),
            (scoped_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 204),
            (scoped_client, "/scm-step-runs/{step_run.public_identifier}/", 204),
            (scoped_client, "/scm-releases/{release.public_identifier}/", 405),
        ],
    )
    def test_delete(self, client_ctx_manager, url, http_status, most_models):
        with client_ctx_manager() as client:
            url = url.format(**most_models)
            response = client.delete(url)
            assert response.status_code == http_status


@pytest.mark.django_db
class TestUpdate:
    @pytest.mark.parametrize(
        ("client_ctx_manager", "url", "http_status"),
        [
            (anonymous_client, "/applications/{application.public_identifier}/", 403),
            (anonymous_client, "/applications/unknown/", 403),
            (anonymous_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 403),
            (anonymous_client, "/teams/{team.public_identifier}/", 403),
            (anonymous_client, "/projects/{project.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 403),
            (anonymous_client, "/scm-services/{service.public_identifier}/", 403),
            (anonymous_client, "/scm-repositories/{repository.public_identifier}/", 403),
            (anonymous_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 403),
            (anonymous_client, "/scm-step-runs/{step_run.public_identifier}/", 403),
            (anonymous_client, "/scm-releases/{release.public_identifier}/", 403),
            # since the put has incomplete data, we expect a 400 when we are allowed, not a 200 like with patch
            (user_client, "/applications/{application.public_identifier}/", 400),
            (user_client, "/applications/unknown/", 404),
            (user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 400),
            (user_client, "/teams/{team.public_identifier}/", 400),
            (user_client, "/projects/{project.public_identifier}/", 400),
            (user_client, "/credentials/{credential.public_identifier}/", 400),
            (user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 400),
            (user_client, "/scm-services/{service.public_identifier}/", 405),
            (user_client, "/scm-repositories/{repository.public_identifier}/", 400),
            (user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 400),
            (user_client, "/scm-step-runs/{step_run.public_identifier}/", 400),
            (user_client, "/scm-releases/{release.public_identifier}/", 405),
            # check user_client, but this time with everything that does not belong to that user
            (user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (user_client, "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/", 404),
            (user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (user_client, "/scm-releases/{not_my_release.public_identifier}/", 405),
            # since the put has incomplete data, we expect a 400 when we are allowed, not a 200 like with patch
            (sys_user_client, "/applications/{application.public_identifier}/", 400),
            (sys_user_client, "/applications/unknown/", 404),
            (sys_user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 400),
            (sys_user_client, "/teams/{team.public_identifier}/", 400),
            (sys_user_client, "/projects/{project.public_identifier}/", 400),
            (sys_user_client, "/credentials/{credential.public_identifier}/", 400),
            (sys_user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 400),
            (sys_user_client, "/scm-services/{service.public_identifier}/", 405),
            (sys_user_client, "/scm-repositories/{repository.public_identifier}/", 400),
            (sys_user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 400),
            (sys_user_client, "/scm-step-runs/{step_run.public_identifier}/", 400),
            (sys_user_client, "/scm-releases/{release.public_identifier}/", 405),
            # check sys_user_client, but this time with everything that does not belong to that user
            (sys_user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (
                sys_user_client,
                "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/",
                404,
            ),
            (sys_user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (sys_user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (sys_user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (sys_user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (sys_user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (sys_user_client, "/scm-releases/{not_my_release.public_identifier}/", 405),
            (scoped_client, "/applications/{application.public_identifier}/", 400),
            (scoped_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 400),
            (scoped_client, "/teams/{team.public_identifier}/", 400),
            (scoped_client, "/projects/{project.public_identifier}/", 400),
            (scoped_client, "/credentials/{credential.public_identifier}/", 400),
            (scoped_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 400),
            (scoped_client, "/scm-services/{service.public_identifier}/", 405),
            (scoped_client, "/scm-repositories/{repository.public_identifier}/", 400),
            (scoped_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 400),
            (scoped_client, "/scm-step-runs/{step_run.public_identifier}/", 400),
            (scoped_client, "/scm-releases/{release.public_identifier}/", 405),
        ],
    )
    def test_update(self, client_ctx_manager, url, http_status, most_models):
        with client_ctx_manager() as client:
            url = url.format(**most_models)
            response = client.put(url)
            assert response.status_code == http_status


@pytest.mark.django_db
class TestPartialUpdate:
    @pytest.mark.parametrize(
        ("client_ctx_manager", "url", "http_status"),
        [
            (anonymous_client, "/applications/{application.public_identifier}/", 403),
            (anonymous_client, "/applications/unknown/", 403),
            (anonymous_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 403),
            (anonymous_client, "/teams/{team.public_identifier}/", 403),
            (anonymous_client, "/projects/{project.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 403),
            (anonymous_client, "/scm-services/{service.public_identifier}/", 403),
            (anonymous_client, "/scm-repositories/{repository.public_identifier}/", 403),
            (anonymous_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 403),
            (anonymous_client, "/scm-step-runs/{step_run.public_identifier}/", 403),
            (anonymous_client, "/scm-releases/{release.public_identifier}/", 403),
            (user_client, "/applications/{application.public_identifier}/", 200),
            (user_client, "/applications/unknown/", 404),
            (user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 200),
            (user_client, "/teams/{team.public_identifier}/", 200),
            (user_client, "/projects/{project.public_identifier}/", 200),
            (user_client, "/credentials/{credential.public_identifier}/", 200),
            (user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 200),
            (user_client, "/scm-services/{service.public_identifier}/", 405),
            (user_client, "/scm-repositories/{repository.public_identifier}/", 200),
            (user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 200),
            (user_client, "/scm-step-runs/{step_run.public_identifier}/", 200),
            (user_client, "/scm-releases/{release.public_identifier}/", 405),
            # check user_client, but this time with everything that does not belong to that user
            (user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (user_client, "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/", 404),
            (user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (user_client, "/scm-releases/{not_my_release.public_identifier}/", 405),
            (sys_user_client, "/applications/{application.public_identifier}/", 200),
            (sys_user_client, "/applications/unknown/", 404),
            (sys_user_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 200),
            (sys_user_client, "/teams/{team.public_identifier}/", 200),
            (sys_user_client, "/projects/{project.public_identifier}/", 200),
            (sys_user_client, "/credentials/{credential.public_identifier}/", 200),
            (sys_user_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 200),
            (sys_user_client, "/scm-services/{service.public_identifier}/", 405),
            (sys_user_client, "/scm-repositories/{repository.public_identifier}/", 200),
            (sys_user_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 200),
            (sys_user_client, "/scm-step-runs/{step_run.public_identifier}/", 200),
            (sys_user_client, "/scm-releases/{release.public_identifier}/", 405),
            # check sys_user_client, but this time with everything that does not belong to that user
            (sys_user_client, "/applications/{not_my_application.public_identifier}/", 404),
            (
                sys_user_client,
                "/applications/{not_my_application.public_identifier}/metadata/{not_my_metadata.key}/",
                404,
            ),
            (sys_user_client, "/teams/{not_my_team.public_identifier}/", 404),
            (sys_user_client, "/projects/{not_my_project.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/", 404),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/secrets/{not_my_secret.key}/", 404),
            # no need to check services again, since they are all public
            (sys_user_client, "/scm-repositories/{not_my_repository.public_identifier}/", 404),
            (sys_user_client, "/scm-pipeline-runs/{not_my_pipeline_run.public_identifier}/", 404),
            (sys_user_client, "/scm-step-runs/{not_my_step_run.public_identifier}/", 404),
            (sys_user_client, "/scm-releases/{not_my_release.public_identifier}/", 405),
            (scoped_client, "/applications/{application.public_identifier}/", 200),
            (scoped_client, "/applications/{application.public_identifier}/metadata/{metadata.key}/", 200),
            (scoped_client, "/teams/{team.public_identifier}/", 200),
            (scoped_client, "/projects/{project.public_identifier}/", 200),
            (scoped_client, "/credentials/{credential.public_identifier}/", 200),
            (scoped_client, "/credentials/{credential.public_identifier}/secrets/{secret.key}/", 200),
            (scoped_client, "/scm-services/{service.public_identifier}/", 405),
            (scoped_client, "/scm-repositories/{repository.public_identifier}/", 200),
            (scoped_client, "/scm-pipeline-runs/{pipeline_run.public_identifier}/", 200),
            (scoped_client, "/scm-step-runs/{step_run.public_identifier}/", 200),
            (scoped_client, "/scm-releases/{release.public_identifier}/", 405),
        ],
    )
    def test_partial_update(self, client_ctx_manager, url, http_status, most_models):
        with client_ctx_manager() as client:
            url = url.format(**most_models)
            response = client.patch(url)
            assert response.status_code == http_status


@pytest.mark.django_db
class TestCreate:
    @pytest.mark.parametrize(
        ("client_ctx_manager", "url", "http_status"),
        [
            (anonymous_client, "/applications/", 403),
            (anonymous_client, "/applications/unknown/", 403),
            (anonymous_client, "/applications/{application.public_identifier}/metadata/", 403),
            (anonymous_client, "/teams/", 403),
            (anonymous_client, "/projects/", 403),
            (anonymous_client, "/credentials/", 403),
            (anonymous_client, "/credentials/{credential.public_identifier}/secrets/", 403),
            (anonymous_client, "/scm-services/", 403),
            (anonymous_client, "/scm-repositories/", 403),
            (anonymous_client, "/scm-pipeline-runs/", 403),
            (anonymous_client, "/scm-step-runs/", 403),
            (anonymous_client, "/scm-releases/", 403),
            # since the post has incomplete data, we expect a 400 when we are allowed, not a 200 like with patch
            (user_client, "/applications/", 400),
            (user_client, "/applications/{application.public_identifier}/metadata/", 400),
            (user_client, "/teams/", 400),
            (user_client, "/projects/", 400),
            (user_client, "/credentials/", 400),
            (user_client, "/credentials/{credential.public_identifier}/secrets/", 400),
            (user_client, "/scm-services/", 405),
            (user_client, "/scm-repositories/", 400),
            (user_client, "/scm-pipeline-runs/", 400),
            (user_client, "/scm-step-runs/", 400),
            (user_client, "/scm-releases/", 405),
            # check user_client, but this time with everything that does not belong to that user
            (user_client, "/applications/{not_my_application.public_identifier}/metadata/", 403),
            (user_client, "/credentials/{not_my_credential.public_identifier}/secrets/", 403),
            # since the post has incomplete data, we expect a 400 when we are allowed, not a 200 like with patch
            (sys_user_client, "/applications/", 400),
            (sys_user_client, "/applications/{application.public_identifier}/metadata/", 400),
            (sys_user_client, "/teams/", 400),
            (sys_user_client, "/projects/", 400),
            (sys_user_client, "/credentials/", 400),
            (sys_user_client, "/credentials/{credential.public_identifier}/secrets/", 400),
            (sys_user_client, "/scm-services/", 405),
            (sys_user_client, "/scm-repositories/", 400),
            (sys_user_client, "/scm-pipeline-runs/", 400),
            (sys_user_client, "/scm-step-runs/", 400),
            (sys_user_client, "/scm-releases/", 405),
            # check sys_user_client, but this time with everything that does not belong to that user
            (sys_user_client, "/applications/{not_my_application.public_identifier}/metadata/", 403),
            (sys_user_client, "/credentials/{not_my_credential.public_identifier}/secrets/", 403),
            (scoped_client, "/applications/", 400),
            (scoped_client, "/applications/{application.public_identifier}/metadata/", 400),
            (scoped_client, "/teams/", 400),
            (scoped_client, "/projects/", 400),
            (scoped_client, "/credentials/", 400),
            (scoped_client, "/credentials/{credential.public_identifier}/secrets/", 400),
            (scoped_client, "/scm-services/", 405),
            (scoped_client, "/scm-repositories/", 400),
            (scoped_client, "/scm-pipeline-runs/", 400),
            (scoped_client, "/scm-step-runs/", 400),
            (scoped_client, "/scm-releases/", 405),
        ],
    )
    def test_create(self, client_ctx_manager, url, http_status, most_models):
        with client_ctx_manager() as client:
            url = url.format(**most_models)
            response = client.post(url, {}, content_type="application/json")
            assert response.status_code == http_status
