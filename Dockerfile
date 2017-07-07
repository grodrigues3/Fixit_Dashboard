FROM ubuntu

MAINTAINER Garrett Rodrigues <grodrigues3@gmail.com>

RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y python python-pip wget

ADD identify_test_ownership.py /
ADD app.py /
ADD requirements.txt /

RUN git clone https://github.com/kubernetes/kubernetes 
RUN pip install -r /requirements.txt
EXPOSE 5000
CMD python app.py
