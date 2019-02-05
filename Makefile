# This Makefile requires the following commands to be available:
# * virtualenv
# * python3.7.1
# * docker

IMAGE=katka-core
DOCKER_REPOSITORY=kpnnv

REQUIREMENTS_BASE:=requirements/requirements-base.txt
REQUIREMENTS_TEST:=requirements/requirements-testing.txt
REQUIREMENTS_TXT:=requirements.txt

PYTHON_VERSION=python3.7

PIP="pip"
TOX="tox"
PYTHON="$(PYTHON_VERSION)"
TWINE="twine"

# When we are not in Docker we assume virtualenv usage
ifneq ($(IN_DOCKER), 1)
  PIP="venv/bin/pip"
  TOX="venv/bin/tox"
  PYTHON="venv/bin/$(PYTHON_VERSION)"
  TWINE="venv/bin/twine"
endif

MAKE_MIGRATIONS=`$(shell echo $(PYTHON)) manage.py makemigrations;`
MIGRATIONS_CHECK=`echo $(MAKE_MIGRATIONS_OUTPUT) | awk '{print match($$0, "No changes detected")}'`


.PHONY: clean pyclean test test_local check_forgotten_migrations migrate tox install_requirement_txt venv


# ********** Cleaning **********

pyclean:
	@find . -name *.pyc -delete
	@rm -rf *.egg-info build
	@rm -rf coverage.xml .coverage

clean: pyclean
	@rm -rf venv
	@rm -rf .tox


# ********** Migrations **********

# check if there is any forgotten migration
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
	docker run --rm -v $(PWD):$(PWD) -w $(PWD) $(DOCKER_REPOSITORY)/$(IMAGE) make $*

docker/publish: docker/build
	docker run --rm -v $(PWD):$(PWD) -w $(PWD) \
	-e tag=$(TAG) -e TWINE_PASSWORD=$(TWINE_PASSWORD) -e TWINE_USERNAME=$(TWINE_USERNAME) \
	$(DOCKER_REPOSITORY)/$(IMAGE) make publish


# ********** Tests **********

# Used by the PR jobs. This target should include all tests necessary
# to determine if the PR should be rejected or not.
tox:
	$(PIP) install tox
	$(TOX)

tox/%:
	$(PIP) install tox
	$(TOX) -e $*

test: docker/check_forgotten_migrations docker/tox
	@echo 'tests done'

test_local: venv check_forgotten_migrations tox
	@echo 'tests done'


# ********** Packaging and destributing **********
setup.py:
	$(PYTHON) setup_gen.py
	@echo 'setup.py created'

publish: setup.py
	$(PYTHON) setup.py sdist bdist_wheel
	$(TWINE) check dist/*
	$(TWINE) upload dist/*


# ********** Requirements **********
install_requirement_txt:
	@$(PIP) install -r $(REQUIREMENTS_TXT)


# ********** Virtual environment **********
venv:
	@rm -rf venv
	@$(PYTHON_VERSION) -m venv venv
	@$(PIP) install -r $(REQUIREMENTS_TXT)
	@touch $@
