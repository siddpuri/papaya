# Arm64 instances with 2 vCPUs, 8 GB RAM, and not t4g
# Ordered by increasing cost
INSTANCE_TYPES = [
    'm6g.large',
    'm6gd.large',
    'a1.xlarge',
    'r6g.large',
    'r6gd.large',
    'c6g.xlarge',
    'c6gd.xlarge',
    'm6g.xlarge',
    'm6gd.xlarge',
    'a1.2xlarge',
]

INSTANCE_NAME = 'minecraft'
KEY_NAME = 'tp'
AVAILABILITY_ZONE = 'us-west-2a'
SECURITY_GROUP = 'minecraft'

DOMAIN_NAME = 'topherpuri.com'
HOSTED_ZONE = 'Z08494311A6US8GNJR58Z'

VOLUME = 'vol-07f47102288b1ac20'

AMI_FILTER = [
    {
        'Name': 'architecture',
        'Values': ['arm64'],
    },
    {
        'Name': 'name',
        'Values': ['amzn2-ami-hvm-*'],
    },
]
AMI_OWNER = 'amazon'

INSTANCE_FILTER = [
    {
        'Name': 'availability-zone',
        'Values': [AVAILABILITY_ZONE],
    },
    {
        'Name': 'tag:Name',
        'Values': [INSTANCE_NAME],
    },
    {
        'Name': 'instance-state-name',
        'Values': ['pending', 'running'],
    },
]

SPOT_REQUEST_FILTER = [
    {
        'Name': 'state',
        'Values': ['active', 'open'],
    },
]

LAUNCH_SPECIFICATION = lambda ami_id, instance_type: {
    'SecurityGroups': [SECURITY_GROUP],
    'ImageId': ami_id,
    'InstanceType': instance_type,
    'KeyName': KEY_NAME,
    'Placement': {'AvailabilityZone': AVAILABILITY_ZONE},
}

TAG_SPECIFICATION = {
    'Tags': [
        {'Key': 'Name', 'Value': INSTANCE_NAME},
    ]
}

DNS_CHANGES = lambda action, address: {
    'Changes': [
        {
            'Action': action,
            'ResourceRecordSet': {
                'Name': DOMAIN_NAME,
                'Type': 'A',
                'ResourceRecords': [{'Value': address}],
                'TTL': 60,
            },
        }
    ]
}
DNS_REGISTRATION = lambda address: DNS_CHANGES('UPSERT', address)
DNS_UNREGISTRATION = lambda address: DNS_CHANGES('DELETE', address)
