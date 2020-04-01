# This Makefile requires the following commands to be available:
# * virtualenv
# * python3.8
# * docker

IMAGE=katka-core
DOCKER_REPOSITORY=kpnnv

REQUIREMENTS_TXT:=requirements.txt

PYTHON_VERSION=python3.8

BLACK="black"
FLAKE8="flake8"
ISORT="isort"
PIP="pip"
TOX="tox"
PYTHON="$(PYTHON_VERSION)"
TWINE="twine"

# When we are not in Docker we assume virtualenv usage
ifneq ($(IN_DOCKER), 1)
  BLACK="venv/bin/black"
  FLAKE8="venv/bin/flake8"
  ISORT="venv/bin/isort"
  PIP="venv/bin/pip"
  TOX="venv/bin/tox"
  PYTHON="venv/bin/python"
  TWINE="venv/bin/twine"
endif

MAKE_MIGRATIONS=`$(shell echo $(PYTHON)) manage.py makemigrations;`
MIGRATIONS_CHECK=`echo $(MAKE_MIGRATIONS_OUTPUT) | awk '{print match($$0, "No changes detected")}'`


# ********** Cleaning **********
.PHONY: pyclean
pyclean:
	@find . -name *.pyc -delete
	@rm -rf *.egg-info build
	@rm -rf coverage.xml .coverage

.PHONY: clean
clean: pyclean
	@rm -rf venv
	@rm -rf .tox


# ********** Migrations **********

# check if there is any forgotten migration
.PHONY: check_forgotten_migrations
check_forgotten_migrations: install_requirement_txt
	$(eval MAKE_MIGRATIONS_OUTPUT:="$(shell echo $(MAKE_MIGRATIONS))")
	@echo $(MAKE_MIGRATIONS_OUTPUT)
	@if [ $(MIGRATIONS_CHECK) -gt 0 ]; then \
		echo "There aren't any forgotten migrations. Well done!"; \
	else \
		echo "Error! You've forgotten to add the migrations!"; \
		exit 1; \
	fi

# migrate on dev environment
.PHONY: migrate
migrate:
	$(PYTHON) manage.py migrate --noinput
	@echo 'Done!'


# ********** Docker **********

docker/build:
	docker build -t $(DOCKER_REPOSITORY)/$(IMAGE) .

docker/build/%:
	docker build -t $(DOCKER_REPOSITORY)/$(IMAGE):$* .

docker/tag/%:
	docker tag $(DOCKER_REPOSITORY)/$(IMAGE) $(DOCKER_REPOSITORY)/$(IMAGE):$*

docker/push/%:
	docker push $(DOCKER_REPOSITORY)/$(IMAGE):$*

docker/%: docker/build
	docker run --rm -v $(PWD):$(PWD) --tmpfs $(PWD)/.tox:exec -w $(PWD) $(DOCKER_REPOSITORY)/$(IMAGE) make $*

docker/publish: docker/build
	docker run --rm -v $(PWD):$(PWD) -w $(PWD) \
	-e tag=$(TAG) -e TWINE_PASSWORD=$(TWINE_PASSWORD) -e TWINE_USERNAME=$(TWINE_USERNAME) \
	$(DOCKER_REPOSITORY)/$(IMAGE) make publish


# ********** Tests **********

# Used by the PR jobs. This target should include all tests necessary
# to determine if the PR should be rejected or not.
.PHONY: tox
tox:
	$(TOX)

.PHONY: test
test: docker/test_local

.PHONY: test_local
test_local: install_requirement_txt check_forgotten_migrations lint tox
	@echo 'tests done'

# ********** Code style **********

.PHONY: lint
lint: lint/flake8 lint/isort lint/black

.PHONY: lint/isort
lint/isort:
	$(ISORT) -rc -c katka tests

.PHONY: lint/flake8
lint/flake8:
	$(FLAKE8) katka tests

.PHONY: lint/black
lint/black:
	$(BLACK) --check katka tests

.PHONY: format
format: format/isort format/black

.PHONY: format/isort
format/isort:
	$(ISORT) -rc katka tests

.PHONY: format/black
format/black:
	$(BLACK) --verbose katka tests


# ********** Packaging and distributing **********
publish:
	$(PYTHON) setup.py sdist bdist_wheel
	$(TWINE) check dist/*
	$(TWINE) upload dist/*


# ********** Requirements **********
.PHONY: install_requirement_txt
install_requirement_txt:
	@$(PIP) install -r $(REQUIREMENTS_TXT)


# ********** Virtual environment **********
.PHONY: venv
venv:
	@rm -rf venv
	@$(PYTHON_VERSION) -m venv venv
	@$(PIP) install -r $(REQUIREMENTS_TXT)
	@touch $@
