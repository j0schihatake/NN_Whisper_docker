# Dockerfile to deploy a llama-cpp container with conda-ready environments

# docker pull continuumio/miniconda3:latest
# https://github.com/openai/whisper

ARG TAG=latest
FROM continuumio/miniconda3:$TAG

RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
        git \
        uvicorn \
        libportaudio2 \
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

# FastApi
#RUN python3 -m pip install pydantic uvicorn[standard] fastapi

RUN python3 -m pip install flask

RUN pip3 install setuptools-rust

RUN pip3 install num2words

RUN pip3 install pydub

RUN pip3 install python-multipart

RUN pip3 install ffmpeg-python

# Update user password:
RUN echo 'whisper-user:admin' | chpasswd

RUN mkdir /home/whisper-user/whisper

RUN mkdir /home/whisper-user/whisper/temp

RUN mkdir /home/whisper-user/whisper/src

RUN cd /home/whisper-user/whisper

# Установка Whisper:
RUN pip3 install -U openai-whisper

RUN pip3 install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git

ADD app.py /home/whisper-user/whisper/
#ADD src/fast.py /home/whisper-user/whisper/src
#ADD src/tts.py /home/whisper-user/whisper/

# Preparing for login
RUN chmod 777 /home/whisper-user/whisper
ENV HOME /home/whisper-user/whisper/
WORKDIR ${HOME}
USER whisper-user

#   --------------------------  FastAPI:

#CMD uvicorn src.fast:app --host 0.0.0.0 --port 8084 --reload

#   --------------------------  FLASK:

# (Optional) Set PORT environment variable
RUN export PORT=8084
RUN export FLASK_RUN_HOST=0.0.0.0
RUN export FLASK_RUN_PORT=8084
CMD python3 -m app run --host=0.0.0.0
#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# Docker:
# docker build -t whisper .
# docker run -it -dit --name whisper -p 8084:8084 --gpus all --restart unless-stopped whisper:latest
# docker run -it -dit --name whisper -p 8084:8084 -v D:/Develop/NeuronNetwork/llama_cpp/llama_cpp_java/model/:/home/whisper-user/whisper/temp --gpus all --restart unless-stopped whisper:latest

# Debug:
# docker container attach whisper