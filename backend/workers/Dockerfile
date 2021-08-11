# FROM jsbroks/coco-annotator:python-env
FROM cdefga/aimed:env-stretch

# RUN apt-get update && \
#     apt-get install -y openjdk-8-jre-headless dcmtk

WORKDIR /workspace/

COPY ./backend/ /workspace/

ARG uid
ARG gid

RUN adduser --disabled-password --no-create-home --gecos '' --uid $uid dockuser
RUN chown -R dockuser:dockuser /workspace/
USER dockuser

EXPOSE 5555

# CMD celery -A workers worker -l info --uid=$uid
CMD celery -A workers worker -l info