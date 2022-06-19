FROM python:3.9

# Change into the source directory
WORKDIR /bot

COPY . .

RUN pip install -r requirements.txt

# DiscordChatExporter and Dependencies

# https://github.com/dotnet/dotnet-docker/blob/main/documentation/scenarios/installing-dotnet.md

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        \
        # .NET dependencies
        libc6 \
        libgcc1 \
        libgssapi-krb5-2 \
        libicu67 \
        libssl1.1 \
        libstdc++6 \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin -Channel 6.0 -Runtime dotnet -InstallDir /usr/share/dotnet \
    && ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet

CMD [ "python", "./main.py" ]
