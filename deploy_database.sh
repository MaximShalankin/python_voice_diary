docker pull mongo
docker rm -f mongo_database || echo no service to remove

docker run -d --name mongo_database -p 27017:27017 -v mongodb_data:/data/db mongo
docker logs -f mongo_database
