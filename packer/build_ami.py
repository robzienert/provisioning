"""
Thin wrapper around Packer to integrate with Jenkins.

This script primarily does two things:

1. Converts YAML files to the Packer expected JSON format.
2. Searches the Ubuntu Cloud Images repository for the latest AMI
   that matches the given criteria, based on region, type,
   virtualization and architecture. This can be skipped by simply
   providing an AMI ID.


Usage
    You can run the following command to get a help menu:

    python build_ami.py -h


Example
    python build_ami.py \
        -var 'api_key_stackdriver=XXX' \
        build ./base/base-ebs.yml
"""
import argparse
import sys
from subprocess import call
import requests
import csv
import logging
import yaml
import json
import boto.ec2
import uuid
import os

IMAGE_TYPE_INDEX = 4
IMAGE_ARCH_INDEX = 5
IMAGE_REGION_INDEX = 6
IMAGE_AMI_INDEX = 7
IMAGE_VM_INDEX = 10

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class UbuntuImagesNotFound(IOError):
    def __init__(self, *args, **kwargs):
        super(UbuntuImagesNotFound, self).__init__(*args, **kwargs)


class UbuntuAmiNotFound(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(UbuntuAmiNotFound, self).__init__(*args, **kwargs)


def build_system_call(packer_command, packer_json, packer_vars, debug):
    system_call = ['packer', packer_command]

    if debug:
        system_call.append('-debug')

    for var in packer_vars:
        system_call.extend(['-var', "'{}'".format(var)])

    system_call.append(packer_json)

    return system_call


def find_latest_ubuntu_image(ubuntu, region, image_type, vm, arch):
    logging.info('Searching for AMI matching criteria: '
                 'ubuntu={}, region={}, type={}, virtualization={}, '
                 'arch={}'.format(ubuntu, region, image_type,
                                  vm, arch))

    r = requests.get('https://cloud-images.ubuntu.com/query/{}/server/'
                     'released.current.txt'.format(ubuntu))
    if r.status_code is not 200:
        raise UbuntuImagesNotFound(
            'Ubuntu cloud images returned with status {}'.format(r.status_code)
        )

    selected_ami = None
    for image in list(csv.reader(r.text.split('\n'), delimiter='\t')):
        if len(image) != 11:
            if len(image) != 0:
                logging.warning('Image line had unexpected length: "{}"'.format(image))
            continue

        if image[IMAGE_REGION_INDEX] != region:
            continue
        if image[IMAGE_ARCH_INDEX] != arch:
            continue
        if image[IMAGE_VM_INDEX] != vm:
            continue
        if image[IMAGE_TYPE_INDEX] != image_type:
            continue
        selected_ami = image[IMAGE_AMI_INDEX]
        break

    if selected_ami is None:
        raise UbuntuAmiNotFound('Could not find Ubuntu AMI for criteria')

    logging.info('Found AMI: "{}"'.format(selected_ami))

    return selected_ami


def convert_to_packer(filename):
    if not filename.endswith('yml'):
        logging.info('YAML Packer file was not passed, assuming already JSON')
        return filename

    target_filename = filename.replace('yml', 'json')

    with open(filename, 'r') as source, open(target_filename, 'w') as target:
        logging.info(
            'Converting "{}" to "{}"'.format(filename, target_filename)
        )

        data = yaml.load(source)
        target.write(json.dumps(data, indent=2))

    return target_filename


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--region', default='us-east-1',
                   help='AWS region to build the AMI')
    p.add_argument('--ubuntu-codename', default='trusty',
                   help='Ubuntu codename to search for')
    p.add_argument('--image-type', default='ebs-ssd',
                   choices=['ebs', 'ebs-io1', 'ebs-ssd', 'instance-store'],
                   help='the image type of the AMI')
    p.add_argument('--image-arch', default='amd64', choices=['amd64', 'i386'],
                   help='the image arch of the AMI')
    p.add_argument('--image-vm', default='hvm',
                   choices=['hvm', 'paravirtual'],
                   help='the image virtualization layer of the AMI')
    p.add_argument('--ami', help='the AMI to use as a base; overrides all '
                                 '--image-* arguments')
    p.add_argument('--artifact', action='store_true',
                   help='if the AMI ID will be saved to an artifact file')
    p.add_argument('-var', action='append', help='all packer variables')
    p.add_argument('-debug', action='store_true', help='run Packer in debug mode')
    p.add_argument('packer_command', choices=['build', 'validate'])
    p.add_argument('packer_file')
    args = p.parse_args()

    ami_uuid = str(uuid.uuid4())

    packer_file = convert_to_packer(args.packer_file)

    if not args.ami:
        source_ami = find_latest_ubuntu_image(
            ubuntu=args.ubuntu_codename,
            region=args.region,
            image_type=args.image_type,
            arch=args.image_arch,
            vm=args.image_vm
        )
    else:
        # TODO use boto to find the virtualization type of this image
        source_ami = args.ami

    packer_variables = [] if args.var is None else args.var
    packer_variables.append('aws_region={}'.format(args.region))
    packer_variables.append('aws_source_ami={}'.format(source_ami))
    packer_variables.append('aws_ami_virtualization={}'.format(args.image_vm))
    packer_variables.append('aws_uuid={}'.format(ami_uuid))

    command = build_system_call(args.packer_command,
                                packer_file,
                                packer_variables,
                                args.debug)

    logging.info('Running command "' + ' '.join(command) + '"')

    ret = call(' '.join(command), shell=True)
    if ret == 0 and args.artifact:
        conn = boto.ec2.connect_to_region(args.region)

        images = conn.get_all_images(filters={
            'tag:BuildUuid': ami_uuid
        })

        if len(images) != 1:
            print images
            logging.warning('Could not find AMI by BuildUuid tag')
        else:
            # If WORKSPACE is set, we're using Jenkins, so create an ami.txt
            # file to create an an artifact for pipelining.
            if os.environ.get('WORKSPACE'):
                dest = os.path.join(os.environ['WORKSPACE'], 'ami.txt')
                logging.info('Writing AMI to "ami.txt"...')
                with open(dest, 'w+') as f:
                    f.write(images[0].id)

    sys.exit(ret)
