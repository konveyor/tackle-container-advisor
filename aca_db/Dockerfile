FROM registry.access.redhat.com/ubi8

RUN \
    # Download latest release
    wget -O sqlite.tar.gz \
    https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release \
    && tar xvfz sqlite.tar.gz \
    # Configure and make SQLite3 binary
    && ./sqlite/configure --prefix=/usr \
    && make \
    && make install \
    # Smoke test
    && sqlite3 --version \