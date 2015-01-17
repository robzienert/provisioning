{%- from 'java/settings.sls' import java with context %}

oracle-java7-installer:
  pkgrepo.managed:
    - ppa: webupd8team/java
  pkg.installed:
    - require:
      - pkgrepo: oracle-java7-installer
  debconf.set:
    - data:
        'shared/accepted-oracle-license-v1-1': {'type': 'boolean', 'value': True}
    - require_in:
      - pkg: {{ java.version_name }}
  require:
    - pkg: debconf-utils
