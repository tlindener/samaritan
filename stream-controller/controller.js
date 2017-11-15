var zookeeper = require('node-zookeeper-client');
var _ = require('lodash');
var Docker = require('dockerode');
var docker = new Docker({
  socketPath: '//./pipe/docker_engine'
}); //defaults to http


var client = zookeeper.createClient('localhost:2181');
var path = "/brokers/topics"

function listChildren(client, path) {
  client.getChildren(
    path,
    function(event) {
      console.log('Got watcher event: %s', event);
      listChildren(client, path);
    },
    function(error, children, stat) {
      if (error) {
        console.log(
          'Failed to list children of %s due to: %s.',
          path,
          error
        );
        return;
      }

      console.log('Children of %s are: %j.', path, children);
      startPersonDetector(children);
    }
  );
}

client.once('connected', function() {
  console.log('Connected to ZooKeeper.');
  listChildren(client, path);
});

function startPersonDetector(children) {
  var personVideoStreams = _.filter(children, function(o) {
    return (o.indexOf("raw-video-stream") > -1)
  });
  personVideoStreams.forEach(function(item) {
    console.log(item);
    var id = item.replace('raw', 'person');
    var container = docker.getContainer(id);

    container.inspect(function(err, data) {
      console.log(err);
      if (err != null && err.statusCode === 404) {
        console.log("start container: " + id);
        docker.createContainer({
          Image: 'tlindener/samaritan-person-detector',
          Cmd: ["python", "-u", "consumer.py"],
          name: id
        }, function(err, container) {
          container.start({
            "HostConfig": {
              "NetworkMode": "samaritan_kafkanet"
            }
          }, function(err, data) {
            //...
          });
        });
      }
      if (data != null) {
        if (!data.State.Running) {
          console.log("not running");
        }
      }
    });

  });
}

function startFaceDetector() {

}

client.connect();
