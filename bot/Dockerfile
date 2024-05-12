FROM python:3 as build_stage
ENV PYTHONUNBUFFERED 1

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]