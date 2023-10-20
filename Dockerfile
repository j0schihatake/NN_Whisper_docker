# Dockerfile to deploy a llama-cpp container with conda-ready environments

# docker pull continuumio/miniconda3:latest

ARG TAG=latest
FROM continuumio/miniconda3:$TAG

RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        git \
        locales \
        sudo \
        build-essential \
        dpkg-dev \
        wget \
        openssh-server \
        ca-certificates \
        netbase\
        tzdata \
        nano \
        software-properties-common \
        python3-venv \
        python3-tk \
        pip \
        bash \
        git \
        ncdu \
        net-tools \
        openssh-server \
        libglib2.0-0 \
        libsm6 \
        libgl1 \
        libxrender1 \
        libxext6 \
        ffmpeg \
        wget \
        curl \
        psmisc \
        rsync \
        vim \
        unzip \
        htop \
        pkg-config \
        libcairo2-dev \
        libgoogle-perftools4 libtcmalloc-minimal4  \
    && rm -rf /var/lib/apt/lists/*

# Setting up locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# Create user:
RUN groupadd --gid 1020 whisper-group
RUN useradd -rm -d /home/whisper-user -s /bin/bash -G users,sudo,whisper-group -u 1000 whisper-user

RUN python3 -m pip install torch torchvision torchaudio

RUN python3 -m pip install flask

RUN pip3 install setuptools-rust

RUN pip3 install num2words

RUN pip3 install pydub

# Update user password:
RUN echo 'whisper-user:admin' | chpasswd

RUN mkdir /home/whisper-user/src

RUN cd /home/whisper-user/src

#RUN pip3 install "git+https://github.com/openai/whisper.git" \

# Установка Whisper:
RUN pip3 install -U openai-whisper

RUN pip3 install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git

#RUN apt-get install -y ffmpeg

# (Optional) Set PORT environment variable
RUN export PORT=8084

RUN chmod 777 /home/whisper-user/src

ADD src/flask.py /home/whisper-user/whisper/

# Preparing for login
ENV HOME /home/whisper-user/whisper
WORKDIR ${HOME}
USER whisper-user
#CMD python3 flask.py
CMD python3 -m src.flask:app run --host=0.0.0.0

# Docker:
# docker build -t whisper .
# docker run -it -dit --name src -p 8084:8084  --gpus all --restart unless-stopped whisper:latest

# Debug:
# docker container attach whisper