#!/usr/bin/env python
from collections import defaultdict
import subprocess
import os

KEEP_LAST_VERSIONS = int(os.environ.get('KEEP_LAST_VERSIONS', 4))


def find_obsolete_images(images):
    for image_name, versions in images.items():
        if len(versions) > KEEP_LAST_VERSIONS:
            obsolete_versions = sorted(versions, reverse=True)[4:]
            for version in obsolete_versions:
                yield '{}:v{}'.format(image_name, version)


def parse_images(lines):
    images = defaultdict(list)

    for line in lines:
        try:
            image_name, version = line.split(' ')
            version_num = int(version.replace('v', ''))
            images[image_name].append(version_num)
        except ValueError:
            pass

    return images


def remove_image(image_name):
    try:
        subprocess.check_call(['docker', 'rmi', image_name])
    except subprocess.CalledProcessError as e:
        print(e.output)


def all_images():
    output = subprocess \
        .check_output(['./docker_image_versions.sh'], shell=True) \
        .decode('utf-8')

    lines = output.split('\n')
    return parse_images(lines)


if __name__ == '__main__':
    images = all_images()
    for image_name in find_obsolete_images(images):
        remove_image(image_name)
