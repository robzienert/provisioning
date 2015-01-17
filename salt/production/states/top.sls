base:
  'G@roles:logstash':
    - match: grain
    - java
    - logstash
  'G@roles:elasticsearch':
    - match: grain
    - java
    - elasticsearch
  'G@roles:kibana':
    - match: grain
    - kibana
development:
  'G@environment:development and G@roles:logstash':
    - match: compound
    - java
    - logstash
  'G@environment:development and G@roles:elasticsearch':
    - match: compound
    - java
    - elasticsearch
  'G@environment:development and G@roles:kibana':
    - match: compound
    - kibana
