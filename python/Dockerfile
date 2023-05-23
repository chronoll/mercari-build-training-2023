FROM python:3.10.6-alpine

WORKDIR /app

RUN addgroup -S mercari && adduser -S trainee -G mercari

COPY python/requirements.txt /python/requirements.txt
RUN pip3 install -r /python/requirements.txt

COPY db /app/db
COPY python /app/python

RUN chown -R trainee:mercari /app/db
RUN chown -R trainee:mercari /app/python/images

USER trainee
WORKDIR /app/python

CMD ["uvicorn", "main:app","--reload","--port","9000","--host","0.0.0.0"]
