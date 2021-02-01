FROM ubuntu:20.04


# RUN apt install default-jre-headless libcommons-lang3-java libbcprov-java
# RUN apt install git default-jdk-headless ant libcommons-lang3-java libbcprov-java
# RUN git clone https://gitlab.com/pdftk-java/pdftk.git
# RUN cd pdftk
# RUN mkdir libs 
# RUN ln -st libs /usr/share/java/{commons-lang3,bcprov}.jar
# RUN ant jar
# RUN java -jar build/jar/pdftk.jar --help
RUN apt update
RUN echo y | apt install pdftk


RUN apt-get update \
    && apt-get install -y python3-pip python3-dev \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 --no-cache-dir install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

# RUN apt-get install libtiff5-dev libjpeg8-dev \
#     zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev \
#     tk8.6-dev python-tk pdftk libmagickwand-dev
# # We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app



CMD [ "python3","app.py" ]