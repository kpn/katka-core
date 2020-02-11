FROM python:3.8.1

ENV IN_DOCKER 1
ENV PYTHONUNBUFFERED 1
ENV PROJECT_ROOT /app

WORKDIR $PROJECT_ROOT

COPY Makefile .
COPY requirements.txt .
COPY requirements requirements
RUN make install_requirement_txt

CMD ["make", "test"]
