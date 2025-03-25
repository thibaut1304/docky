FROM python:3.10-slim

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG DOCKER_GID=999

RUN apt-get update && apt-get install -y openssh-client jq && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${GROUP_ID} appgroup && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash appuser && \
    groupadd -g ${DOCKER_GID} docker || true && \
    usermod -aG docker appuser

WORKDIR /app

COPY . /app

RUN chown -R appuser:appgroup /app

USER appuser

RUN pip install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT ["/bin/bash", "/app/start.sh"]
