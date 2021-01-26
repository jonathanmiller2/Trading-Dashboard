FROM python:3

ENV PYTHONUNBUFFERED 1

#Create and cd into /code/ on the container, then copy all of the files in the same directory as this Dockerfile from the normal filesystem into /code/ on the container
WORKDIR /code
COPY . .

RUN python /code/create_db.py

ADD crontab /etc/cron.d/hello-cron
RUN chmod 0644 /etc/cron.d/hello-cron
RUN touch /var/log/cron.log

#Install dependencies
RUN apt-get update
RUN apt-get -y install cron

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD cron && tail -f /var/log/cron.log