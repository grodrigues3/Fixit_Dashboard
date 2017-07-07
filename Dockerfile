FROM ubuntu

MAINTAINER Garrett Rodrigues <grodrigues3@gmail.com>

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y python python-pip wget

RUN git clone https://github.com/grodrigues3/Fixit_Dashboard 

RUN git clone https://github.com/kubernetes/kubernetes 
RUN pip install -r /requirements.txt
EXPOSE 5000
RUN cd /Fixit_Dashboard
CMD python app.py
