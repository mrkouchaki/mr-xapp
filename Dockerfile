FROM python:3.7-alpine
# RMR setup
RUN mkdir -p /opt/route_mr/

# copy rmr files from builder image in lieu of an Alpine package
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/lib64/librmr* /usr/local/lib64/

COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/bin/rmr* /usr/local/bin/
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
COPY local.rt /opt/route_mr/local.rt
ENV RMR_SEED_RT /opt/route_mr/local.rt

RUN apk update && apk add gcc musl-dev
RUN pip install ricxappframe

# Install
COPY setup.py /tmp
COPY LICENSE.txt /tmp/
# RUN mkdir -p /tmp/ad/
COPY mr/ /mr
RUN pip install /tmp
ENV PYTHONUNBUFFERED=0
CMD PYTHONPATH=/mr:/usr/lib/python3.7/site-packages/:$PYTHONPATH run-mr.py
