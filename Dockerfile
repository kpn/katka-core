FROM python:3.8.1

ENV IN_DOCKER 1
ENV PYTHONUNBUFFERED 1
ENV PROJECT_ROOT /app

WORKDIR $PROJECT_ROOT

COPY Makefile .
COPY requirements.txt .
COPY setup.py .
COPY README.md .
# purely so we can get the version from git
COPY .git .git
RUN make install_requirement_txt

CMD ["make", "test"]
