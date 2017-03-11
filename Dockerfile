FROM ubuntu:14.10
MAINTAINER Anselm Kiefner <fuzzy@anselm.kiefner.de>
RUN apt-get update && apt-get -y install python3-pip
RUN pip3 install numpy
RUN pip3 install "ipython[notebook]"

COPY . /fuzzylogic

ENV PATH $HOME/.local/bin:$PATH