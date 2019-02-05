# Katka core

Django app which is be responsible for storing information abouts applications and teams.

## Clone
You can clone this repository on: https://github.com/kpn/katka-core

## Setup
Setup your environment:

```shell
$ make venv
```

## Stack

Katka core is built on top of the Python framework Django and the Django Rest
Framework to build APIs. Under the hood it runs Python 3.7.

### Dependencies
* [djangorestframework](djangorestframework): django toolkit for building Web APIs
* [django-encrypted-model-fields](django-encrypted-model-fields): save encrypted fields on DB

[djangorestframework]: https://github.com/encode/django-rest-framework
[django-encrypted-model-fields]: https://gitlab.com/lansharkconsulting/django/django-encrypted-model-fields/

## Contributing

### Workflow
1. Fork this repository
2. Clone your fork
3. Create and test your changes
4. Create a pull-request
5. Wait for default reviewers to review and merge your PR

## Running tests
Tests are run on docker by executing
```shell
$ make test
```

Or using venv
```shell
$ make test_local
```

## Versioning

We use SemVer 2 for versioning. For the versions available, see the tags on this 
repository.

## Authors
* *KPN I&P D-Nitro* - d-nitro@kpn.com
