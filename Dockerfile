FROM golang

MAINTAINER Garrett Rodrigues <grodrigues3@gmail.com>

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y python python-pip wget
RUN pip install --upgrade pip 
RUN git clone https://github.com/kubernetes/kubernetes 
EXPOSE 5000

RUN mkdir Fixit_Dashboard
ADD ./* Fixit_Dashboard/
RUN cd Fixit_Dashboard && pip install -r requirements.txt
CMD cd Fixit_Dashboard && python app.py
