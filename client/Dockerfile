FROM node:10

WORKDIR /workspace/

COPY ./client/package* /workspace/
COPY ./client/node_modules /workspace/node_modules

ENV NODE_PATH=/workspace/node_modules

WORKDIR /workspace/client/

EXPOSE 8080
CMD npm run serve