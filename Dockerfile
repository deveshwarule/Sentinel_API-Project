FROM python:latest
WORKDIR /home/lt-337/PycharmProjects/Sentinel_API/
RUN apt-get update -y
RUN apt-get install pip -y
RUN pip install sentinelsat
RUN pip install flask
RUN pip install flask_sqlalchemy
RUN pip install flask_marshmallow
COPY map.geojson ./
COPY requirement.txt ./
COPY Sentinel_Data.sqlite ./
COPY Fetch_Sentineldata.py ./
COPY templates ./templates/
CMD [ "python" , "./Fetch_Sentineldata.py" ]