FROM python:3.10.12-bookworm

WORKDIR /src

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    BASE_PATH=/src \
    STILT_WD=/usr/local/stilt \
    TZ=UTC \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

RUN apt update && apt install -y --no-install-recommends \
        build-essential \
        git \
        libhdf5-dev \
        libhdf5-serial-dev \
        libnetcdf-dev \
        libssl-dev \
        locales \
        netcdf-bin \
        procps \
        r-base \
        r-base-dev \
        gdal-bin \
        libgdal-dev \
        libproj-dev \
        unzip \
        wget \
        vim \
        redis-server \
    && locale-gen en_US.UTF-8 \
    && update-locale \
    && rm -rf /var/lib/apt/lists/*

# Clone STILT, install R packages, and run setup
RUN git clone --depth=1 https://github.com/uataq/stilt ${STILT_WD} && \
    R -e "install.packages(c('dplyr', 'ncdf4', 'parallel', 'rslurm', 'raster', 'R.utils'))" && \
    chmod +x ${STILT_WD}/setup && \
    cd ${STILT_WD} && \
    ./setup && \
    Rscript r/dependencies.r

# Apply for access here: https://www.ready.noaa.gov/HYSPLIT_register.php
# COPY build/bin/linux-gnu/* ${STILT_WD}/exe/
# RUN chmod +x ${STILT_WD}/exe/*

# copy server code and install dependencies
COPY server .
COPY scripts/start_server.sh .
RUN pip install --upgrade pip \
    && pip install . \
    && chmod +x /src/start_server.sh

RUN chmod +x /src/start_server.sh
EXPOSE 8000 5555

CMD ["/src/start_server.sh"]