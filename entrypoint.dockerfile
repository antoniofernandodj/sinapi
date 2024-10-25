# Stage 1: Build
FROM python:3.13 AS sinapi-api-builder

WORKDIR /home/itemize/flow

COPY ./requirements.txt requirements.txt


RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

# Stage 2: Production
FROM python:3.13 AS sinapi-api-prod

WORKDIR /home/itemize/flow

RUN useradd -ms /bin/bash itemize && \
    pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    mkdir -p /home/itemize/.cache/fontconfig && \
    chown -R itemize:itemize /home/itemize/.cache

USER itemize

COPY --from=sinapi-api-builder /usr/local /usr/local

ENV \
    PATH="${PATH}:/home/itemize/.local/bin" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONBREAKPOINT=0 \
    TERM=xterm-256color

USER itemize

COPY --from=sinapi-api-builder /home/itemize/flow /home/itemize/flow

CMD ["uvicorn", "app_entrypoint:app", "--port", "7000", "--host", "0.0.0.0"]