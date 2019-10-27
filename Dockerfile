FROM python:3
MAINTAINER Jack Brown (jack@brown1993.com)

ADD hive_to_influxdb.py /
ADD requirements.txt /

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["-u","hive_to_influxdb.py"]
