# annotator

### Requirements
- docker-compose
- npm or yarn
- VueJS for web front-end
- Flask (Python) for web back-end

### run evelopment mode
- start `docker-compose`
```
docker-compose -f docker-compose.build.yml up (-d)
```
(-d is detach mode)
- end `docker-compose` if start `docker-compose` with detach mode (-d)
```
docker-compose down
```

### run production mode
- start `docker-compose`
```
docker-compose up (-d)
```
(-d is detach mode)
- end `docker-compose` if start `docker-compose` with detach mode (-d)
```
docker-compose down
```
