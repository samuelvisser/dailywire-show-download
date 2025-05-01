FROM python:3.13-slim

# System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git \
      ffmpeg \
      cron \
    && rm -rf /var/lib/apt/lists/*

# Clone yt-dlp + PR #9920, install
WORKDIR /opt
RUN git clone https://github.com/yt-dlp/yt-dlp.git && \
    cd yt-dlp && \
    git fetch origin pull/9920/head:pr-9920 && \
    git checkout pr-9920 && \
    pip install .

# Create directories
RUN mkdir -p /downloads /config /app/cache /tmp/yt-dlp-tmp \
    && chmod a+rwX /tmp/yt-dlp-tmp /app/cache

# Copy the Python package
COPY ./dailywire_downloader /app/dailywire_downloader
COPY ./setup.py /app/

# Install the package
WORKDIR /app
RUN pip install -e .

# Copy the cron‐template
COPY ./cron.d /etc/cron.d
RUN chmod 0644 /etc/cron.d/dailywire.cron.template

# Ensure cron log exists
RUN touch /var/log/cron.log

# Volumes for user‑mounted config & outputs
VOLUME ["/config","/downloads"]

# Copy in our scripts
COPY ./scripts/ /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Entrypoint sets up cron, then CMD runs it
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["cron", "-f"]
