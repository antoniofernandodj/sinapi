# Stage 1: Build
FROM python:3.13 AS sinapi-builder

WORKDIR /home/itemize/flow

COPY ./requirements.txt requirements.txt


RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

# Stage 2: Production
FROM python:3.11 AS sinapi-prod

WORKDIR /home/itemize/flow

RUN useradd -ms /bin/bash itemize && \
    pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    mkdir -p /home/itemize/.cache/fontconfig && \
    chown -R itemize:itemize /home/itemize/.cache

USER itemize

COPY --from=sinapi-builder /usr/local /usr/local

ENV PATH="${PATH}:/home/itemize/.local/bin" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONBREAKPOINT=0 TERM=xterm-256color

USER itemize

COPY --from=sinapi-builder /home/itemize/flow /home/itemize/flow

CMD ["python", "sinapi"]