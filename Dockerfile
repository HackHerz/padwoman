FROM python:3.9-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache gcc libc-dev openldap-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apk add --no-cache linux-headers
RUN pip install uwsgi

COPY . .

CMD ["uwsgi", "--http", "0.0.0.0:8000", "--wsgi-file", "wsgi.py", "--master", "--processes", "4", "--threads", "2", "--disable-logging"]
