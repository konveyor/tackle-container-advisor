# Image for a Python 3 development environment
FROM python:3.8-slim

# Add any tools that are needed beyond Python
RUN apt-get update && \
    apt-get install -y sudo vim git sqlite3 zip tree curl wget jq && \
    apt-get autoremove -y && \
    apt-get clean -y

# Create a user for development
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user with passwordless sudo privileges
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    && usermod -aG sudo $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up the Python development environment
WORKDIR /app
RUN python -m pip install --upgrade pip setuptools wheel

# Enable color terminal for docker exec bash
ENV TERM=xterm-256color

EXPOSE 5000

# Become a regular user for development
USER $USERNAME
