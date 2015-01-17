elasticsearch-repo-key:
  cmd.run:
    - name: wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
    - unless: apt-key list | grep 'Elasticsearch (Elasticsearch Signing Key)'

elasticsearch-repo:
  pkgrepo.managed:
    - humanname: Elasticsearch Official Debian Repository
    - name: deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main
    - require:
      - cmd: elasticsearch-repo-key
