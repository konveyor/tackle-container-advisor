FROM registry.access.redhat.com/ubi8

# COPY ./sqlite3.tar.gz /tmp
RUN \
    tar xvfz sqlite3.tar.gz \
    # Configure and make SQLite3 binary
    && ./sqlite/configure --prefix=/usr \
    && make \
    && make install \
    # Smoke test
    && sqlite3 --version \