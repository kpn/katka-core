import pytest
from katka import models


@pytest.mark.django_db
class TestUpdateStatusSCMStepRunView:

    def test_partial_update_status_valid(self, client, logged_in_user, scm_step_run):
        url = f'/update-scm-step-run/{scm_step_run.public_identifier}/'
        data = {'status': 'success'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.SCMStepRun.objects.get(pk=scm_step_run.public_identifier)
        assert p.status == 'success'

    def test_partial_update_no_param(self, client, logged_in_user, scm_step_run):
        url = f'/update-scm-step-run/{scm_step_run.public_identifier}/'
        data = {}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 400
        assert response.json()['status'][0] == 'This field is required.'

    def test_partial_update_invalid_status(self, client, logged_in_user, scm_step_run):
        url = f'/update-scm-step-run/{scm_step_run.public_identifier}/'
        data = {'status': 'bla'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 400
        assert response.json()['status'][0] == '"bla" is not a valid choice.'

    def test_no_other_field_is_updated_using_put(self, client, logged_in_user, scm_step_run):
        url = f'/update-scm-step-run/{scm_step_run.public_identifier}/'
        data = {'status': 'success', 'output': 'test'}
        assert scm_step_run.output == ''
        response = client.put(url, data, content_type='application/json')
        assert response.status_code == 200
        p = models.SCMStepRun.objects.get(pk=scm_step_run.public_identifier)
        assert p.status == 'success'
        assert p.output == ''

    def test_not_logged_in(self, client, scm_step_run):
        url = f'/update-scm-step-run/{scm_step_run.public_identifier}/'
        data = {'status': 'success'}
        response = client.patch(url, data, content_type='application/json')
        assert response.status_code == 404
