FROM python:3.10.6-alpine

WORKDIR /app

RUN addgroup -S mercari && adduser -S trainee -G mercari

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

USER trainee

COPY . .

#COPY /Users/NEC-PCuser/Documents/workspace/mercari-build-training-2023/db /db

#RUN chown -R trainee:mercari ../db/mercari.sqlite3


CMD ["uvicorn", "main:app","--reload","--port","9000","--host","0.0.0.0"]
