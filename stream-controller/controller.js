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
    var container = docker.getContainer(item);
    console.log(container);
    container.inspect(function(err, data) {
      if(data === null)
      {

      }
    });

  });
}

function startFaceDetector() {

}

client.connect();
