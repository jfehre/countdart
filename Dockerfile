FROM python:3.8-bullseye AS base

RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN apt-get clean

# Add software-properties-common to allow installing PPA repositories
ENV TZ=Europe/Berlin
RUN echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget software-properties-common git tzdata \
    graphviz \
    vim

#create a non root user to access the container
RUN adduser --disabled-password --gecos '' --uid 1000 user

# create virtual environment
ENV VIRTUAL_ENV=/opt/venvs/countdart
RUN mkdir -p /opt/venvs && python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


WORKDIR /app/
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/

FROM base as dev

# Install dependencies
COPY requirements/dev.txt /dev-requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip,mode=0755 \
    python3 -m pip install \
    -r /dev-requirements.txt && \
    rm /dev-requirements.txt

# Allow user write access to virtual env, so we can
# install packages for testing.
RUN chown -R user $VIRTUAL_ENV

USER user