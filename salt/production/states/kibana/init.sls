{% set kibana_port = salt['pillar.get']('kibana:lookup:http_port', '8080') %}
{% set server_name = salt['pillar.get']('kibana:lookup:server_name', 'kibana') %}
{% set www_home = salt['pillar.get']('kibana:lookup:www_home', '/var/www') %}
{% set bind_host = salt['pillar.get']('kibana:lookup:bind_host', '127.0.0.1') %}
{% set kibana_root = www_home + '/' + server_name + '/' %}

include:
  - elasticsearch.repo

kibana-static-dir:
  file.directory:
    - name: {{ kibana_root }}
    - user: www-data
    - group: www-data
    - makedirs: True

nginx-sites-dir:
  file.directory:
    - name: /etc/nginx/sites-enabled
    - makedirs: True

kibana-config:
  file.managed:
    - name: '{{ kibana_root }}/config.js'
    - template: jinja
    - source: salt://kibana/files/config.jinja
    - context:
      - kibana_port: {{ kibana_port }}
      - bind_host: {{ bind_host }}

nginx-static-site:
  pkg.installed:
    - name: nginx
    - require:
      - file: nginx-sites-dir
      - file: kibana-static-dir
  service.running:
    - name: nginx
    - reload: True
    - enable: True
    - watch:
      - file: nginx-static-site
  file.managed:
    - name: /etc/nginx/sites-enabled/kibana
    - template: jinja
    - source: salt://kibana/files/nginx_kibana_site
    - mode: 644
    - context:
      kibana_port: {{ kibana_port }}
      server_name: {{ server_name }}
      kibana_root: {{ kibana_root }}

kibana:
  archive.extracted:
    - name: {{ kibana_root }}
    - source: https://download.elasticsearch.org/kibana/kibana/kibana-3.1.2.tar.gz
    - archive_format: tar
    - tar_options: xf
