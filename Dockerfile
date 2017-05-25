FROM ubuntu:16.10
RUN apt-get update && apt-get -y install python3-pip
RUN pip3 install matplotlib
RUN pip3 install "ipython[notebook]"
 
COPY . /fuzzy

ENV PATH $HOME/.local/bin:$PATH
