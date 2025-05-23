FROM continuumio/miniconda3
COPY requirements.txt /tmp/
COPY ./app /app

LABEL maintainer "Soo-Yeon Kim, sooyeonkim@gwu.edu"

WORKDIR "/app"
RUN conda install python=3.10 -y
RUN conda install --file /tmp/requirements.txt -c conda-forge
RUN conda install gunicorn -y 
RUN conda install uwsgi -y
RUN useradd -m appUser
USER appUser

EXPOSE 8050

CMD gunicorn --bind 0.0.0.0:8050 index:server
