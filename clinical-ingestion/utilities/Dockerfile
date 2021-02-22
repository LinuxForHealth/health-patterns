FROM praqma/network-multitool:alpine-3.12

LABEL maintainer="Luis A. Garcia at Alvearie"
LABEL maintainer="David Ranum at Alvearie"

# Install python and python dependencies
RUN apk add --update --no-cache python3 py-pip && ln -sf python3 /usr/bin/python
RUN pip install requests

# Copy python and shell scripts
RUN mkdir /scripts
COPY  *.sh scripts/
COPY  *.py scripts/
RUN chmod +x scripts/*.sh