FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV ELAN_HOME=/root/.elan
ENV PATH=/root/.elan/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    build-essential \
    unzip \
    zstd \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY lean-toolchain lakefile.lean lake-manifest.json ./
RUN curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
  | sh -s -- -y --default-toolchain "$(cat lean-toolchain)"

COPY RhCore ./RhCore
COPY data ./data
COPY tools ./tools

RUN lake exe cache get || true
RUN lake build RhCore.Final

CMD ["lake", "build", "RhCore.Final"]
