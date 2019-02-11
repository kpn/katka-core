from contextlib import contextmanager

from django.db import models

from .exceptions import MissingUsername


@contextmanager
def username_on_model(model, username):
    """
    Create a context to set all usernames of all AutoUsernameFields of a Django model.

    Django's models are normally not aware of the request (by design),
    so automatically saving the username of the person who made the change
    to the object is not easy.

    Using a global object can lead to all kinds of subtle bugs, so we
    needed to find a way to pass the username in a different way; in this case
    explicit.

    Args:
        model: The Django model to check for instances of AutoUsernameFields
        username: The username to set in this context
    """

    # the following looks a bit hacky, but is actually the documented way of Django on how to get a list of fields:
    # https://docs.djangoproject.com/en/2.1/ref/models/meta/#retrieving-all-field-instances-of-a-model
    auto_username_fields = [field for field in model._meta.get_fields() if isinstance(field, AutoUsernameField)]

    for field in auto_username_fields:
        field.set_username(username)

    try:
        yield
    finally:
        for field in auto_username_fields:
            field.reset_username()


class AutoUsernameField(models.CharField):
    """
    Save the username on every modification

    To pass the username from a view, put all change operations within a context:

        def view(..., request, ...):
            with username_on_model(YourModel, request.username):
                code_that_gets_querylists_and_modifies_objects()

            return response

    For more information, see the 'username_on_model' context manager.
    """
    def __init__(self, *args, only_on_create=False, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 50

        self.only_on_create = only_on_create
        self._username = None
        self._prev_username = None

        super().__init__(*args, **kwargs)

    def set_username(self, username):
        self._prev_username, self._username = self._username, username

    def reset_username(self):
        self._username, self._prev_username = self._prev_username, None

    def pre_save(self, model_instance, add):
        if self._username is None:
            class_name = model_instance.__class__.__name__
            raise MissingUsername(
                f'No username set. Make sure the username is set with the "username_on_model({class_name}, username)" '
                'context manager'
            )

        if add or not self.only_on_create:
            setattr(model_instance, self.attname, self._username)

        return getattr(model_instance, self.attname)


class KatkaSlugField(models.SlugField):
    def __init__(self, *args, max_length=10, blank=False, null=False, **kwargs):
        super().__init__(*args, max_length=max_length, blank=blank, null=null, **kwargs)
