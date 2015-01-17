add-missing-hostname:
  cmd.run:
    - name: 'echo "127.0.0.1  $HOSTNAME" | sudo tee -a /etc/hosts'

{% if grains['os'] == 'Ubuntu' %}
python-pip:
  pkg.installed:
    refresh: True

python-setuptools:
  pip.installed

# Aaaand gross:
tmp-cfn-bootstrap:
  cmd.run:
    - name: mkdir ~/aws-cfn-bootstrap-latest

download-cfn-bootstrap:
  cmd.run:
    - name: curl https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz | tar xz -C aws-cfn-bootstrap-latest --strip-components 1

install-cfn-bootstrap:
  cmd.run:
    - name: easy_install aws-cfn-bootstrap-latest

remove-cfn-bootstrap-dir:
  cmd.run:
    - name: rm -rf ~/aws-cfn-bootstrap-latest
{% endif %}
