# requirements-stage
FROM python:3.12.3-bullseye as requirements-stage

WORKDIR /tmp

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    openssl \
    wget \
    build-essential \
    automake \
    autoconf \
    libtool \
    pkg-config \
    gettext \
    libc-dev \
    ffmpeg \
    vim

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && ln -s /opt/poetry/bin/poetry && poetry config virtualenvs.create false && poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

# 환경이 올바른지 확인하기 위해 종속성 설치
RUN poetry install --no-root

# poetry-plugin-export 명시적으로 설치
RUN poetry self add poetry-plugin-export

ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then poetry export -f requirements.txt --output requirements.txt --dev --without-hashes; else poetry export -f requirements.txt --output requirements.txt --without-hashes; fi

FROM python:3.12.3-bullseye

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    openssl \
    wget \
    build-essential \
    automake \
    autoconf \
    libtool \
    pkg-config \
    gettext \
    libc-dev \
    ffmpeg \
    vim

LABEL name="jychoi" version="0.1.0" description="connectslab_user_api"

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && echo "Asia/Tokyo" > /etc/timezone
ENV TZ=Asia/Tokyo

WORKDIR /src/

COPY --from=requirements-stage /tmp/requirements.txt /src/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
RUN pip install pandas

COPY ./app /src/app/

EXPOSE 2456
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2456"]
