INSTANCE_TYPE = 'm6g.xlarge'
KEY_NAME = 'tp'
AVAILABILITY_ZONE = 'eu-central-1a'
SECURITY_GROUP = 'minecraft'

DOMAIN_NAME = 'topherpuri.com'
HOSTED_ZONE = 'Z01121531AFCKRL61Q1OG'

VOLUME = 'vol-0f0f9712f7684c896'

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
        'Name': 'instance-state-name',
        'Values': ['pending', 'running'],
    },
]

SPOT_REQUEST_FILTER = [
    {
        'Name': 'state',
        'Values': ['active'],
    },
]

LAUNCH_SPECIFICATION = lambda ami_id: {
    'SecurityGroups': [SECURITY_GROUP],
    'ImageId': ami_id,
    'InstanceType': INSTANCE_TYPE,
    'KeyName': KEY_NAME,
    'Placement': {'AvailabilityZone': AVAILABILITY_ZONE},
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
