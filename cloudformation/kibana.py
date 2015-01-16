from troposphere import Template, Ref


def template():
    t = Template()
    t.add_version()
    t.add_description('Creates an ELK stack in CloudFormation. This template '
                      'assumes (maybe incorrectly) that you already have a '
                      'template that\'s creating your VPC with networking and '
                      'private subnets and all that goodness. This template '
                      'creates two ASGs, one for ElasticSearch, one for '
                      'Logstash and then a small t2.micro instance to host '
                      'Kibana.')

    return t


if __name__ == '__main__':
    with open('templates/kibana.json', 'wb') as template_file:
        template_file.write(template().to_json())
