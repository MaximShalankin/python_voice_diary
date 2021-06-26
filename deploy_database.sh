if docker inspect --format '{{json .State.Running}}' mongo_database
then
  echo "container is already running"
  exit
fi
docker pull mongo
docker run -d --name mongo_database -p 27017:27017 -v mongodb_data:/data/db mongo
echo 'database launched successfully'