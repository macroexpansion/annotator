FROM node:10 as build-stage

WORKDIR /workspace/
COPY ./client /workspace/client

ENV NODE_PATH=/workspace/client/node_modules

WORKDIR /workspace/client
RUN npm run build

FROM cdefga/aimed:env-stretch

WORKDIR /workspace/
COPY ./backend/ /workspace/

RUN python set_path.py

COPY --from=build-stage /workspace/client/dist /workspace/dist

ARG uid
ARG gid

RUN adduser --disabled-password --no-create-home --gecos '' --uid $uid dockuser
RUN chown -R dockuser:dockuser /workspace/
USER dockuser

ENV FLASK_ENV=production
ENV DEBUG=false

EXPOSE 5000
CMD gunicorn -c webserver/gunicorn_config.py webserver:app --no-sendfile --timeout 180
