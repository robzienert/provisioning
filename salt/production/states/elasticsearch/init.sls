{%- from 'elasticsearch/settings.sls' import elasticsearch with context %}

include:
  - java
  - .repo

elasticsearch:
  pkg.latest:
    - name: elasticsearch
    - require:
      - pkgrepo: elasticsearch-repo
  service.running:
    - name: elasticsearch
    - enable: true

elasticsearch-config:
  file.managed:
    - name: /etc/elasticsearch/elasticsearch.yml
    - source: salt://elasticsearch/files/elasticsearch.yml
    - template: jinja
    - user: root
    - watch_in:
      - service: elasticsearch

# TODO add ec2 plugin if production env
# http://www.elasticsearch.org/tutorials/elasticsearch-on-ec2/