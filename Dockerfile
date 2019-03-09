FROM python:3.5-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache gcc libc-dev openldap-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi"]
