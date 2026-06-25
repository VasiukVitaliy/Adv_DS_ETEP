FROM python:3.12-slim

WORKDIR /project
COPY . /project/

RUN apt update -y && apt install awscli -y
RUN pip install uv && uv pip install -r requirements.txt

CMD ["python3", "app.py"]