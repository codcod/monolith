
    $ cd platform/traffik
    $ docker-build build -t stelo-traffic .

    => ERROR [compile-image 5/9] COPY ../inbox /opt stelo
    ------
     > [compile-image 5/9] COPY ../inbox /opt/stelo:
    ------
    Dockerfile:13
    --------------------
      11 |
      12 |     RUN mkdir -p /opt/stelo/
      13 | >>> COPY ../inbox /opt/stelo
      14 |
      15 |     WORKDIR /opt/stelo/
    --------------------
    ERROR: failed to solve: failed to compute cache key: failed to calculate checksum of ref 30650724-84eb-458a-af69-66bb61de7de4::u5l3l0368mv017xycaxh9hlz2: "/inbox": not found
