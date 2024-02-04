FROM ubuntu:22.04

SHELL ["/bin/bash", "-c"]

# Skip country selection
RUN apt-get update && \
    apt-get install -yq tzdata && \
    #localedef -i en_US -f UTF-8 en_US.UTF-8 && \
    echo "LANG=\"en_US.UTF-8\"" > /etc/locale.conf && \
    ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Packages
RUN apt-get update && apt-get -y --quiet --no-install-recommends install \
    # Ubuntu requirements
    sudo openssh-client locales build-essential \
    # Backend Python packages
    python3.11 python3-pip python3-pexpect \
    # Tools
    htop net-tools vim curl git bash-completion \
    sed desktop-file-utils libgl1-mesa-dev libglu1-mesa-dev

# Env variable to use terminal / editors
ENV TERM=xterm
# Set timezone format
ENV TZ=UTC

# Create user (Mandatory to mkdir)
ENV HOME="/home/user"
ENV USER="user"
RUN useradd -m ${USER} && echo "${USER}:${USER}" | chpasswd && adduser ${USER} sudo
# Dodge sudo password
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3
ENV PATH="/opt/poetry/bin:$PATH"

# Swap to user ${USER} (Root things before this line)
USER ${USER}

# Create ssh folder and Load gitlab as known host
RUN mkdir -p ${HOME}/.ssh
RUN chmod +rw ${HOME}/.ssh
RUN ssh-keyscan github.com >> ${HOME}/.ssh/known_hosts

WORKDIR ${HOME}

# Utilisation de Poetry pour installer les dépendances
COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create true && \
    poetry install --no-interaction --no-ansi

CMD [ "/bin/bash" ]
