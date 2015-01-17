from troposphere import Template, Ref, Parameter, Output, GetAtt, Join, Condition, Equals, Tags, Base64, If
import troposphere.ec2 as ec2
import troposphere.autoscaling as autoscaling
import troposphere.elasticloadbalancing as elb

def template():
    t = Template()
    t.add_version()
    t.add_description('Creates an ELK stack in CloudFormation. This template '
                      'assumes (maybe incorrectly) that you already have a '
                      'template that\'s creating your VPC with networking and '
                      'private subnets and all that goodness. This template '
                      'creates two ASGs, one for ElasticSearch, one for '
                      'Logstash and then a small t2.micro instance to host '
                      'Kibana. This template is definitely not suitable for '
                      'actual production use without a lot of love, like '
                      'locking down Kibana and ElasticSearch.')

    vpc_id = t.add_parameter(Parameter(
        'VpdId',
        Type='AWS::EC2::Vpc::Id'
    ))

    env_name = t.add_parameter(Parameter(
        'EnvName',
        Type='String',
        Default='ops'
    ))

    provisioner = t.add_parameter(Parameter(
        'Provisioner',
        Type='String',
        Description='Must be one of "salt" or "ansible", defaults to "salt"',
        Default='salt'
    ))

    es_ami = t.add_parameter(Parameter(
        'ElasticSearchAmi',
        Type='String',
        Description='The AMI ID of the ElasticSearch image that is burned by Packer.'
    ))

    ls_ami = t.add_parameter(Parameter(
        'LogstashAmi',
        Type='String',
        Description='The AMI ID of the Logstash image that is burned by Packer.'
    ))

    kibana_ami = t.add_parameter(Parameter(
        'KibanaAmi',
        Type='String',
        Description='The AMI ID of the Kibana image that is burned by Packer.'
    ))

    key_name = t.add_parameter(Parameter(
        'KeyName',
        Type='String',
        Description='One key to rule them all',
        Default='ops-elk-demo'
    ))

    private_subnets = t.add_parameter(Parameter(
        'PrivateSubnets',
        Type='List<AWS::EC2::Subnet::Id>',
        Description='The private subnets that the autoscaling groups will belong'
    ))

    public_subnets = t.add_parameter(Parameter(
        'PublicSubnets',
        Type='List<AWS::EC2::Subnet::Id>',
        Description='The public subnets that the ELBs will belong'
    ))

    azs = t.add_parameter(Parameter(
        'AvailabilityZones',
        Type='CommaDelimitedList',
        Description='A list of the availability zones correlated to the subnets'
    ))

    bastion_sg = t.add_parameter(Parameter(
        'BastionSg',
        Type='AWS::EC2::SecurityGroup::Id',
        Description='Allow SSH from this security group'
    ))

    t.add_condition('UseSalt', Equals(Ref(provisioner), 'salt'))

    kibana_lb_sg = t.add_resource(ec2.SecurityGroup(
        'KibanaLbSg',
        GroupDescription='Provides internet access to the Kibana external load balancer',
        VpcId=Ref(vpc_id),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=8080,
                ToPort=8080,
                CidrIp='0.0.0.0/0'
            )
        ],
        Tags=Tags(
            Name=Join('.', [Ref(env_name), 'kibana-lb-sg']),
            env='ops'
        )
    ))

    kibana_server_sg = t.add_resource(ec2.SecurityGroup(
        'KibanaServerSg',
        GroupDescription='Allows access to Kibana',
        VpcId=Ref(vpc_id),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=8080,
                ToPort=8080,
                SourceSecurityGroupId=Ref(kibana_lb_sg)
            ),
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=22,
                ToPort=22,
                SourceSecurityGroupId=Ref(bastion_sg)
            )
        ],
        Tags=Tags(
            Name=Join('.', [Ref(env_name), 'kibana-server-sg']),
            env='ops'
        )
    ))

    ls_server_sg = t.add_resource(ec2.SecurityGroup(
        'LogstashServerSg',
        GroupDescription='Allows SSH access to Logstash',
        VpcId=Ref(vpc_id),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=22,
                ToPort=22,
                SourceSecurityGroupId=Ref(bastion_sg)
            )
        ],
        Tags=Tags(
            Name=Join('.', [Ref(env_name), 'logstash-server-sg']),
            env='ops'
        )
    ))

    # This isn't right.
    es_lb_sg = t.add_resource(ec2.SecurityGroup(
        'ElasticSearchLbSg',
        GroupDescription='Allow internal traffic to access ES cluster',
        VpcId=Ref(vpc_id),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=9200,
                ToPort=9200,
                SourceSecurityGroupId=Ref(kibana_server_sg)
            ),
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=9300,
                ToPort=9300,
                SourceSecurityGroupId=Ref(ls_server_sg)
            )
        ],
        Tags=Tags(
            Name=Join('.', [Ref(env_name), 'elasticsearch-lb-sg']),
            env='ops'
        )
    ))

    # TODO This is probably wrong.
    es_server_sg = t.add_resource(ec2.SecurityGroup(
        'ElasticSearchServerSg',
        GroupDescription='Allow internal traffic to access ES cluster',
        VpcId=Ref(vpc_id),
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=9200,
                ToPort=9200,
                SourceSecurityGroupId=Ref(es_lb_sg)
            ),
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=9300,
                ToPort=9300,
                SourceSecurityGroupId=Ref(es_lb_sg)
            ),
            ec2.SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=22,
                ToPort=22,
                SourceSecurityGroupId=Ref(bastion_sg)
            )
        ],
        Tags=Tags(
            Name=Join('.', [Ref(env_name), 'elasticsearch-server-sg']),
            env='ops'
        )
    ))

    es_lb = t.add_resource(elb.LoadBalancer(
        'ElasticSearchLb',
        LoadBalancerName='ElkElasticSearchInternalLb',
        CrossZone=True,
        SecurityGroups=[Ref(es_lb_sg)],
        Subnets=Ref(private_subnets),
        Scheme='internal',
        Listeners=[
            elb.Listener(
                Protocol='HTTP',
                LoadBalancerPort=9200,
                InstancePort=9200
            ),
            elb.Listener(
                Protocol='TCP',
                LoadBalancerPort=9300,
                InstancePort=9300
            )
        ],
        Tags=Tags(
            Name=Join('.', [Ref(env_name, 'elasticsearch-internal-lb')]),
            env=Ref(env_name),
            stackdriver_monitor=False
        )
    ))

    es_launch_config = t.add_resource(autoscaling.LaunchConfiguration(
        'ElasticSearchLaunchConfig',
        KeyName=Ref(key_name),
        ImageId=Ref(es_ami),
        SecurityGroups=[Ref(es_server_sg)],
        InstanceType='r3.xlarge',
        BlockDeviceMappings=[
            autoscaling.BlockDeviceMapping(
                DeviceName='/dev/xvdb',
                VirtualName='ephemeral0'
            )
        ],
        UserData=Base64(Join('', [
            If(
                'UseSalt',
                '',
                ''
            )
        ]))
    ))

    t.add_resource(autoscaling.AutoScalingGroup(
        'ElasticSearchAsg',
        LaunchConfigurationName=Ref(es_launch_config),
        AvailabilityZones=Ref(azs),
        MinSize=1,
        MaxSize=10,
        DesiredCapacity=1,
        LoadBalancerNames=[Ref(es_lb)],
        VPCZoneIdentifier=Ref(private_subnets),
        Tags=autoscaling.Tags(
            Name=Join('.', [Ref(env_name), 'elasticsearch']),
            env='ops'
        )
    ))

    ls_launch_config = t.add_resource(autoscaling.LaunchConfiguration(
        'LogstashLaunchConfig',
        KeyName=Ref(key_name),
        ImageId=Ref(ls_ami),
        SecurityGroups=[Ref(ls_server_sg)],
        InstanceType='c3.large',
        UserData=Base64(Join('', [
            If(
                'UseSalt',
                '',
                ''
            )
        ]))
    ))

    t.add_resource(autoscaling.AutoScalingGroup(
        'LogstashAsg',
        LaunchConfigurationName=Ref(ls_launch_config),
        AvailabilityZones=Ref(azs),
        MinSize=1,
        MaxSize=10,
        DesiredCapacity=1,
        VPCZoneIdentifier=Ref(private_subnets),
        Tags=autoscaling.Tags(
            Name=Join('.', [Ref(env_name), 'elasticsearch']),
            env='ops'
        )
    ))

    t.add_resource(ec2.Instance(
        'KibanaInstance',
        # TODO Fuck it bed time.
    ))

    kibana_lb = t.add_resource(elb.LoadBalancer(
        'KibanaLb',
        # TODO
    ))

    t.add_output([
        Output(
            'KibanaUrl',
            Value=Join('', [GetAtt(kibana_lb, 'PublicDNS')])
        )
    ])

    return t


if __name__ == '__main__':
    with open('templates/kibana.json', 'wb') as template_file:
        template_file.write(template().to_json())
