# -*- coding: utf-8 -*-
#
# This file is part of Glances.
#

# Copyright (C) 2019 Nicolargo <nicolas@nicolargo.com>

# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Cloud plugin.

Supported Cloud API:
- AWS EC2 (class ThreadAwsEc2Grabber, see bellow)
"""

try:
    import urllib3
except ImportError:
    cloud_tag = False
else:
    cloud_tag = True

import json
import threading

from memory_profiler import profile
from glances.compat import iteritems, to_ascii
from glances.plugins.glances_plugin import GlancesPlugin
from glances.logger import logger


class Plugin(GlancesPlugin):

    """Glances' cloud plugin.

    The goal of this plugin is to retreive additional information
    concerning the datacenter where the host is connected.

    See https://github.com/nicolargo/glances/issues/1029

    stats is a dict
    """

    # AWS EC2
    AWS = 'aws'
    AZURE = 'azure'
    GCP = 'gcp'
    OPC = 'opc'
    ALIBABA = 'alibaba'

    # http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html
    AWS_EC2_API_URL = 'http://169.254.169.254/latest/dynamic/instance-identity/document'
    AWS_EC2_API_URL_CHECK = 'http://169.254.169.254/latest/dynamic/instance-identity/document'

    # https://docs.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service
    AZURE_VM_API_URL = 'http://169.254.169.254/metadata/instance?api-version=2017-12-01'
    AZURE_VM_API_URL_CHECK = 'http://169.254.169.254/metadata/instance?api-version=2017-12-01'

    # https://cloud.google.com/compute/docs/storing-retrieving-metadata#querying
    GCP_VM_API_URL = 'http://metadata.google.internal/computeMetadata/v1/instance'
    GCP_VM_API_URL_CHECK = 'http://metadata.google.internal/computeMetadata/v1/instance/id'
    GCP_VM_API_METADATA = {'cpu-platform': 'cpu-platform',
                           'description': 'description',
                           'hostname': 'hostname',
                           'id': 'id',
                           'machine-type': 'machine-type',
                           'name': 'name',
                           'tags': 'tags',
                           'zone': 'zone'
                           }
    # https://docs.cloud.oracle.com/iaas/Content/Compute/Tasks/gettingmetadata.htm
    OPC_VM_API_URL = 'http://169.254.169.254/opc/v1/instance/'
    OPC_VM_API_URL_CHECK = 'http://169.254.169.254/opc/v1/instance/'

    ALIBABA_VM_API_URL = 'http://100.100.100.200/latest/meta-data'
    ALIBABA_VM_API_URL_CHECK = 'http://100.100.100.200/latest/meta-data/instance-id'
    ALIBABA_VM_API_URL_METADATA = {'dns-conf/nameservers': 'dns-conf/nameservers',
                                   'eipv4': 'eipv4',
                                   'hostname': 'hostname',
                                   'image-id': 'image-id',
                                   'image/market-place/product-code': 'image/market-place/product-code',
                                   'image/market-place/charge-type': 'image/market-place/charge-type',
                                   'instance-id': 'instance-id',
                                   'mac': 'mac',
                                   'network-type': 'network-type',
                                   'owner-account-id': 'owner-account-id',
                                   'private-ipv4': 'private-ipv4',
                                   'public-ipv4': 'public-ipv4',
                                   'region-id': 'region-id',
                                   'zone-id': 'zone-id',
                                   'serial-number': 'serial-number',
                                   'vpc-id': 'vpc-id',
                                   'vpc-cidr-block': 'vpc-cidr-block',
                                   'vswitch-cidr-block': 'vswitch-cidr-block',
                                   'vswitch-id': 'vswitch-id',
                                   'instance/spot/termination-time': 'instance/spot/termination-time',
                                   'network/interfaces/macs': 'network/interfaces/macs',
                                   'instance/virtualization-solution': 'instance/virtualization-solution',
                                   'instance/virtualization-solution-version': 'instance/virtualization-solution-version',
                                   'instance/last-host-landing-time': 'instance/last-host-landing-time'}

    def __init__(self, args=None):
        """Init the plugin."""
        super(Plugin, self).__init__(args=args)

        # We want to display the stat in the curse interface
        self.display_curse = True

        # Init the stats
        self.reset()

    def reset(self):
        """Reset/init the stats."""
        self.stats = {}

    fp = open('/tmp/memory_profiler_stats_cloud.log', 'w+')
    @GlancesPlugin._check_decorator
    @GlancesPlugin._log_result_decorator
    @profile(stream=fp, precision=4)
    def update(self):
        if not cloud_tag:
            logger.debug("cloud plugin - Requests lib is not installed")
            return {}

        cloud = self.determine_cloud_provider()
        timeout = 3
        if cloud == self.AWS:
            r_url = self.AWS_EC2_API_URL
            try:
                http = urllib3.PoolManager()
                r = http.request('GET', r_url, timeout=timeout)
                if r.status == 200:
                    document = json.loads(r.data)
                    self.stats['privateIp'] = document['privateIp']
                    self.stats['devpayProductCodes'] = document['devpayProductCodes']
                    self.stats['marketplaceProductCodes'] = document['marketplaceProductCodes']
                    self.stats['version'] = document['version']
                    self.stats['instanceId'] = document['instanceId']
                    self.stats['billingProducts'] = document['billingProducts']
                    self.stats['instanceType'] = document['instanceType']
                    self.stats['availabilityZone'] = document['availabilityZone']
                    self.stats['kernelId'] = document['kernelId']
                    self.stats['ramdiskId'] = document['ramdiskId']
                    self.stats['accountId'] = document['accountId']
                    self.stats['architecture'] = document['architecture']
                    self.stats['imageId'] = document['imageId']
                    self.stats['pendingTime'] = document['pendingTime']
                    self.stats['region'] = document['region']
                    self.stats['type'] = self.AWS
            except Exception as e:
                logger.debug('cloud plugin - Cannot connect to the AWS EC2 API {}: {}'.format(r_url, e))
        elif cloud == self.AZURE:
            r_url = self.AZURE_VM_API_URL
            try:
                headers = {}
                headers['Metadata'] = "true"
                http = urllib3.PoolManager()
                r = http.request('GET', r_url, headers=headers, timeout=timeout)
                if r.status == 200:
                    document = json.loads(r.data)
                    self.stats['compute'] = document['compute']
                    self.stats['network'] = document['network']
                    self.stats['type'] = self.AZURE
            except Exception as e:
                logger.debug('cloud plugin - Cannot connect to the AZURE VM API {}: {}'.format(r_url, e))
        elif cloud == self.GCP:
            self.stats['type'] = self.GCP
            for k, v in iteritems(self.GCP_VM_API_METADATA):
                r_url = '{}/{}'.format(self.GCP_VM_API_URL, v)
                try:
                    headers = {}
                    headers['Metadata-Flavor'] = "Google"
                    # Local request, a timeout of 3 seconds is OK
                    http = urllib3.PoolManager()
                    r = http.request('GET', r_url, headers=headers, timeout=timeout)
                    if r.status == 200:
                        self.stats[k] = r.data
                except Exception as e:
                    logger.debug('cloud plugin - Cannot connect to the GCP VM API {}: {}'.format(r_url, e))
        elif cloud == self.OPC:
            self.stats['type'] = self.OPC
            r_url = self.OPC_VM_API_URL
            try:
                http = urllib3.PoolManager()
                r = http.request('GET', r_url, timeout=timeout)
                if r.status == 200:
                    document = json.loads(r.data)
                    self.stats['id'] = document['id']
                    self.stats['displayName'] = document['displayName']
                    self.stats['compartmentId'] = document['compartmentId']
                    self.stats['shape'] = document['shape']
                    self.stats['region'] = document['region']
                    self.stats['availabilityDomain'] = document['availabilityDomain']
                    self.stats['timeCreated'] = document['timeCreated']
                    self.stats['image'] = document['image']
            except Exception as e:
                logger.debug('cloud plugin - Cannot connect to the OPC VM API {}: {}'.format(r_url, e))
        elif cloud == self.ALIBABA:
            self.stats['type'] = self.ALIBABA
            for k, v in iteritems(self.ALIBABA_VM_API_URL_METADATA):
                r_url = '{}/{}'.format(self.ALIBABA_VM_API_URL, v)
                try:
                    headers = {}
                    http = urllib3.PoolManager()
                    r = http.request('GET', r_url, headers=headers, timeout=timeout)
                    if r.status == 200:
                        self.stats[k] = r.data
                except Exception as e:
                    logger.debug('cloud plugin - Cannot connect to the ALIBABA VM API {}: {}'.format(r_url, e))
                    self.stats[k] = to_ascii(r.content)
        return self.stats

    def msg_curse(self, args=None):
        """Return the string to display in the curse interface."""
        # Init the return message
        ret = []

        if not self.stats or self.stats == {} or self.is_disable():
            return ret

        # Generate the output
        if 'ami-id' in self.stats and 'region' in self.stats:
            msg = 'AWS EC2'
            ret.append(self.curse_add_line(msg, "TITLE"))
            msg = '{} instance {} ({})'.format(to_ascii(self.stats['instance-type']),
                                                to_ascii(self.stats['instance-id']),
                                                to_ascii(self.stats['region']))

        # Return the message with decoration
        logger.info(ret)
        return ret

    fp = open('/tmp/memory_profiler_stats_cloud__determine_cloud_provider.log', 'w+')
    @GlancesPlugin._check_decorator
    @GlancesPlugin._log_result_decorator
    @profile(stream=fp, precision=4)
    def determine_cloud_provider(self):
        headers = {}
        try:
            http = urllib3.PoolManager()
            r = http.request('GET', url, headers=headers, timeout=0.1)
            if r.status == 200:
                return self.AWS
        except Exception as e:
                pass
        return None
