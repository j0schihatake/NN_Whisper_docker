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

# RUN service ssh start

# Create user:
RUN groupadd --gid 1020 whisper-group
RUN useradd -rm -d /home/whisper-user -s /bin/bash -G users,sudo,whisper-group -u 1000 whisper-user

# Update user password:
RUN echo 'whisper-user:admin' | chpasswd

RUN mkdir /home/whisper-user/whisper

RUN cd /home/whisper-user/whisper

# Clone the repository
RUN git clone https://github.com/askrella/speech-rest-api.git /home/whisper-user/whisper/

# Navigate to the project directory
#RUN cd speech-rest-api

# Install ffmpeg (Ubuntu & Debian)
#sudo apt update && sudo apt install ffmpeg -y

RUN chmod 777 /home/whisper-user/whisper

RUN cd /home/whisper-user/whisper

# Install the dependencies
RUN python3 -m pip install -r /home/whisper-user/whisper/requirements.txt

# (Optional) Set PORT environment variable
RUN export PORT=3000

# Run the REST API
# python app.py

COPY ./run.sh /home/whisper-user/whisper

#ENTRYPOINT ["/home/whisper-user/whisper/run.sh"]

# Download model
# COPY ./model/wizardLM-7B.ggmlv3.q4_0.bin /home/whisper-user/model/      --> Так не отработало persmission denied

# Preparing for login
ENV HOME /home/whisper-user/whisper
WORKDIR ${HOME}
USER whisper-user
CMD ["/bin/bash"]
#CMD ["python", "llama_cpp.server --model /home/whisper-user/model/wizardLM-7B.ggmlv3.q4_0.bin"]

#CMD["/bin/bash", "python3 -m llama_cpp.server --model /home/whisper-user/model/wizardLM-7B.ggmlv3.q4_0.bin"]


# Docker:
# docker build -t whisper .
# docker run -it -dit --name whisper -p 3000:3000  --gpus all --restart unless-stopped whisper:latest
# docker container attach whisper