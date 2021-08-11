# FROM jsbroks/coco-annotator:python-env
FROM cdefga/aimed:env-stretch

WORKDIR /workspace/

COPY ./backend/ /workspace/

ARG uid
ARG gid

RUN adduser --disabled-password --no-create-home --gecos '' --uid $uid dockuser
RUN chown -R dockuser:dockuser /workspace/
USER dockuser

RUN python set_path.py

ENV FLASK_ENV=development
ENV DEBUG=true

EXPOSE 5000
CMD gunicorn -c webserver/gunicorn_config.py webserver:app --no-sendfile


