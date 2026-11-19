FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 openjdk-17-jdk-headless python3-pip pylint wget unzip ca-certificates \
    && wget -O /tmp/pmd.zip https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.1.0/pmd-dist-7.1.0-bin.zip \
    && unzip /tmp/pmd.zip -d /root \
    && rm /tmp/pmd.zip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
