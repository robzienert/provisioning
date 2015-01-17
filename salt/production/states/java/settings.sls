{% set p = salt['pillar.get']('java', {}) %}
{% set g = salt['grains.get']('java', {}) %}

{%- set default_version_name = 'oracle-java7-installer' %}

{%- set version_name = g.get('version_name', p.get('version_name', default_version_name)) %}

{%- set java = {} %}
{%- do java.update({
  'version_name': version_name
}) %}
