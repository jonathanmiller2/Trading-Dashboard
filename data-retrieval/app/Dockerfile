FROM python:3

ENV PYTHONUNBUFFERED 1

#Create and cd into /code/ on the container, then copy all of the files in the same directory as this Dockerfile from the normal filesystem into /code/ on the container
WORKDIR /code
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY crontab /etc/cron.d/cron-python
RUN chmod 0644 /etc/cron.d/cron-python
RUN touch /var/log/cron.log

ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get -y install cron
RUN crontab /etc/cron.d/cron-python
CMD cron && tail -f /var/log/cron.log






