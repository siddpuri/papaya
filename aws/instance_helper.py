import typing as T

import app.logger
import boto3  # type: ignore
import botocore  # type: ignore

import aws.constants as c


class InstanceHelper:
    def __init__(self) -> None:
        self.logger = app.logger.Logger()
        self.ec2 = boto3.client('ec2')
        self.route53 = boto3.client('route53')

    def log(self, message: str) -> None:
        self.logger.log(message)

    # Public methods

    def start(self) -> None:
        self.create_spot_request()
        self.register_address()
        self.attach_volume()

    def stop(self) -> None:
        self.unregister_address()
        self.cancel_spot_request()
        self.terminate_instance()

    # Information getters

    def is_instance_running(self) -> bool:
        response = self.ec2.describe_instances(Filters=c.INSTANCE_FILTER)
        reservations = response['Reservations']
        return len(reservations) > 0

    def get_latest_ami(self) -> str:
        response = self.ec2.describe_images(
            Filters=c.AMI_FILTER,
            Owners=[c.AMI_OWNER],
        )
        latest = max(
            response['Images'],
            key=lambda i: i['CreationDate'],
        )
        return latest['ImageId']

    def get_instance(self) -> T.Dict[str, T.Any]:
        response = self.ec2.describe_instances(Filters=c.INSTANCE_FILTER)
        reservations = response['Reservations']
        if not reservations:
            raise RuntimeError('Instance is not running')
        assert len(reservations) == 1
        instances = reservations[0]['Instances']
        assert len(instances) == 1
        return instances[0]

    def get_instance_id(self) -> str:
        return self.get_instance()['InstanceId']

    def get_address(self) -> str:
        network_interfaces = self.get_instance()['NetworkInterfaces']
        assert len(network_interfaces) == 1
        return network_interfaces[0]['Association']['PublicIp']

    # Instance actions

    def create_spot_request(self) -> None:
        if self.is_instance_running():
            raise RuntimeError('Instance is already running')
        self.log('There is no instance running')
        latest_ami = self.get_latest_ami()
        self.log(f'Latest AMI: {latest_ami}')
        response = self.ec2.request_spot_instances(
            LaunchSpecification=c.LAUNCH_SPECIFICATION(latest_ami)
        )
        requests = response['SpotInstanceRequests']
        assert len(requests) == 1
        request_id = requests[0]['SpotInstanceRequestId']
        self.log(f'Created spot request: {request_id}')
        self.ec2.get_waiter('spot_instance_request_fulfilled').wait(
            SpotInstanceRequestIds=[request_id]
        )
        response = self.ec2.describe_spot_instance_requests(
            SpotInstanceRequestIds=[request_id]
        )
        requests = response['SpotInstanceRequests']
        assert len(requests) == 1
        instance_id = requests[0]['InstanceId']
        self.log(f'Starting instance: {instance_id}')
        try:
            self.ec2.get_waiter('instance_running').wait(
                InstanceIds=[instance_id],
            )
        except botocore.exceptions.WaiterError:
            self.log('Waiter error')
        self.log(f'Started instance: {instance_id}')

    def cancel_spot_request(self) -> None:
        response = self.ec2.describe_spot_instance_requests(
            Filters=c.SPOT_REQUEST_FILTER
        )
        requests = response['SpotInstanceRequests']
        if not requests:
            self.log('There is no spot request to cancel')
            return
        assert len(requests) == 1
        request_id = requests[0]['SpotInstanceRequestId']
        self.ec2.cancel_spot_instance_requests(
            SpotInstanceRequestIds=[request_id]
        )
        self.log(f'Canceled spot request: {request_id}')

    def terminate_instance(self) -> None:
        instance_id = self.get_instance_id()
        self.log(f'Terminating instance: {instance_id}')
        self.ec2.terminate_instances(
            InstanceIds=[instance_id],
        )
        try:
            self.ec2.get_waiter('instance_terminated').wait(
                InstanceIds=[instance_id],
            )
        except botocore.exceptions.WaiterError:
            self.log('Waiter error')
        self.log(f'Terminated instance: {instance_id}')

    # DNS actions

    def register_address(self) -> None:
        address = self.get_address()
        self.route53.change_resource_record_sets(
            ChangeBatch=c.DNS_REGISTRATION(address),
            HostedZoneId=c.HOSTED_ZONE,
        )
        self.log(f'Created DNS entry: {address}')

    def unregister_address(self) -> None:
        address = self.get_address()
        self.route53.change_resource_record_sets(
            ChangeBatch=c.DNS_UNREGISTRATION(address),
            HostedZoneId=c.HOSTED_ZONE,
        )
        self.log(f'Deleted DNS entry: {address}')

    # EBS actions

    def attach_volume(self) -> None:
        self.log(f'Attaching volume: {c.VOLUME}')
        response = self.ec2.attach_volume(
            Device='/dev/sdf',
            InstanceId=self.get_instance_id(),
            VolumeId=c.VOLUME,
        )
        self.ec2.get_waiter('volume_in_use').wait(
            VolumeIds=[c.VOLUME],
        )
        self.log(f'Attached volume: {response["VolumeId"]}')
