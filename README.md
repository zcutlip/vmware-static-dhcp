# `vmwarestatic`

## Description

A utility to add:

- A static DHCP reservation to VMWare Fusion's `dhcpd.conf`
- A corresponding hostname/IP address entry to `/etc/hosts`

## Caveats

Currently, `vmwarestatic` does minimal sanity checking, so if asked it may add nonsensical things to your system's configuration files. It may hose your VMWare Fusion installation or even your entire system. It works for me, but use at your own risk.

## Rationale

For the user who creates Virtual Machines then wants to frequently `ssh` or `rsync` to them to kick off software builds, test code, etc. it's convenient to give those machines static DHCP reservations in `/path/to/vmware/config/vmnet8/dhcpd.conf` and make those VMs resolvable by hostname in using `/etc/hosts` entries. This tool automates that.

## Installation

    $ virtualenv -p python3 ./vmwarestatic
    $ $ source ./vmwarestatic/bin/activate
    $ (vmwarestatic) cd ./vmware-dhcp-static
    $ (vmwarestatic) pip install .
    $ (vmwarestatic) vmwarestatic --version
    vmwarestatic VMware Fusion static DHCP/hosts file setup tool version 0.1.0.dev0

## Usage

    usage: vmwarestatic [-h] --hw-addr HW_ADDR --ip-addr IP_ADDR --hostname
                        HOSTNAME [--use-sudo] [--version]
                        updated_hosts_path updated_dhcpd_conf_path

    vmwarestatic VMware Fusion static DHCP/hosts file setup tool version
    0.1.0.dev0

    positional arguments:
    updated_hosts_path    Path to updated hosts file
    updated_dhcpd_conf_path
                            Path to update dhcpd.conf file.

    optional arguments:
    -h, --help            show this help message and exit
    --hw-addr HW_ADDR     MAC address
    --ip-addr IP_ADDR     IP address to reserve
    --hostname HOSTNAME   hostname to associate with IP address.
    --use-sudo            Use 'sudo' to elevate privileges before writing
                            updated files.
    --version             Print version string and exit

## Examples

For the following example, we'll add a static DHCP reservation for:

- IP address: `192.168.111.10`
- Hostname: `catalina-vm`
- MAC address: `aa:bb:cc:dd:ee:ff`

Creating updated copies of `/etc/hosts` and `dhcpd.conf` for review before manually copying them into place. **Root privileges NOT required.**

```Console
$ vmwarestatic ./hosts ./dhcpd.conf --hw-addr aa:bb:cc:dd:ee:ff --ip-addr 192.168.111.10 --hostname catalina-vm
Writing updated hosts file to ./hosts
Writing updated dhcpd configuration to ./dhcpd.conf
$ cat ./hosts
##
# Host Database
##
127.0.0.1                   localhost
255.255.255.255             broadcasthost
::1                         localhost
fe80::1%lo0                 localhost
192.168.127.16              sierra
192.168.111.10              catalina-vm

$ cat ./dhcpd.conf
# Configuration file for ISC 2.0 vmnet-dhcpd operating on vmnet8.
#

###### VMNET DHCP Configuration. Start of "DO NOT MODIFY SECTION" #####

allow unknown-clients;
default-lease-time 1800;                # default is 30 minutes
max-lease-time 7200;                    # default is 2 hours

subnet 192.168.111.0 netmask 255.255.255.0 {
	range 192.168.111.128 192.168.111.254;
	option broadcast-address 192.168.111.255;
	option domain-name-servers 192.168.111.2;
	option domain-name localdomain;
	default-lease-time 1800;                # default is 30 minutes
	max-lease-time 7200;                    # default is 2 hours
	option netbios-name-servers 192.168.111.2;
	option routers 192.168.111.2;
}
host vmnet8 {
	hardware ethernet 00:50:56:C0:00:08;
	fixed-address 192.168.111.1;
	option domain-name-servers 0.0.0.0;
	option domain-name "";
	option routers 0.0.0.0;
}
####### VMNET DHCP Configuration. End of "DO NOT MODIFY SECTION" #######

host catalina-vm {
	hardware ethernet aa:bb:cc:dd:ee:ff;
	fixed-address 192.168.111.10;
}
```

To update config files in place, they are first created as temp files, and then copied in place. The last step requires elevated, privileges. Tell `vmwarestatic` to use `sudo`, which will prompt for authentication when necessary. Also note the destination is the actual system configuration destination:

```Console
$ vmwarestatic /etc/hosts /Library/Preferences/VMware\ Fusion/vmnet8/dhcpd.conf \
    --use-sudo \
    --hw-addr aa:bb:cc:dd:ee:ff \
    --ip-addr 192.168.111.10 \
    --hostname catalina-vm
Writing updated hosts file to /var/folders/7w/h64245yx5j50747sjclfktp80009rj/T/tmpdj8890t2/hosts
Writing updated dhcpd configuration to /var/folders/7w/h64245yx5j50747sjclfktp80009rj/T/tmpdj8890t2/dhcpd.conf
about to run: /usr/bin/sudo /bin/cp /var/folders/7w/h64245yx5j50747sjclfktp80009rj/T/tmpdj8890t2/hosts /etc/hosts
Password:
about to run: /usr/bin/sudo /bin/cp /var/folders/7w/h64245yx5j50747sjclfktp80009rj/T/tmpdj8890t2/dhcpd.conf /Library/Preferences/VMware Fusion/vmnet8/dhcpd.conf
Killing sudo credential.
```

## TODO

- [ ] More robust sanity checking of IP addresses, against subnet, etc.
- [ ] Checking if VMWare is currently running
- [ ] Should work on VMware Workstation, at least on Linux (maybe on Windows) without too much effort
- [ ] A config file to avoid having to provide the same command line args every time.
- [ ] Maybe upload to PyPI in order top `pip install`?
