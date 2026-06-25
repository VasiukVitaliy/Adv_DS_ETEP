FROM python:3.12-slim

WORKDIR /project

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY requirements.txt /project/

RUN uv pip install --system -r requirements.txt
RUN uv pip install --system awscli

COPY . /project/

CMD ["python3", "app.py"]