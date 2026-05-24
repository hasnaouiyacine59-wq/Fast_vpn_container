FROM ubuntu:22.04 AS camoufox-builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip3 install --timeout 300 --retries 5 -r /requirements.txt && \
    python3 -m camoufox fetch


FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:1
ENV PYTHONUNBUFFERED=1

# Layer 1: system packages (rarely changes)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    wget \
    python3 \
    python3-pip \
    iproute2 \
    iptables \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fluxbox \
    xterm \
    git \
    jq \
    dbus \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: NordVPN (changes only on version bumps)
RUN curl -sSf https://repo.nordvpn.com/gpg/nordvpn_public.asc \
    | gpg --dearmor -o /usr/share/keyrings/nordvpn.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/nordvpn.gpg] https://repo.nordvpn.com/deb/nordvpn/debian stable main" \
    > /etc/apt/sources.list.d/nordvpn.list && \
    apt-get update && apt-get install -y nordvpn && \
    rm -rf /var/lib/apt/lists/*

# Layer 3: copy pip packages + camoufox binary from builder (no re-download)
COPY --from=camoufox-builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=camoufox-builder /usr/local/bin /usr/local/bin
COPY --from=camoufox-builder /root/.cache/camoufox /root/.cache/camoufox

EXPOSE 6080

# Layer 4: entrypoint (changes most often — always last)
COPY entrypoint-unified.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
