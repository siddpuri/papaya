# papaya

This repository contains all the code needed to start and stop a minecraft server on a given schedule.

* All server infrastructure is run on AWS. This includes EC2 instances, EBS volumes, Route 53 DNS service, and IAM identity management.
* Server machines are AWS spot instances. This cuts the price by a factor of 3, but introduces the problem of instances being revoked.
* All the files needed for minecraft intself (paper.jar, plugins, configs) are kept on an EBS volume, and are not included in this repository. The logic to maintain rolling backups is handled by EC2, and is not included here.
* Instead of using elastic IP, the DNS entry for the server is updated every time a new spot instance is allocated. This saves a few cents, but introduces a delay of a few minutes while the DNS information propagates.
* The SSH key for accessing the server and the IAM credentials to control AWS are not included in this repository for obvious reasons. In order for an installation to work, these two files need to be copied separately.
* The crontab can be installed on Raspberry Pi, allowing the server to start and stop on schedule without relying on a PC staying always on.

Work in progress:

* Implement watchdog that can run on Raspberry Pi and automatically provisions a new server if a spot instance is revoked during server hours.
