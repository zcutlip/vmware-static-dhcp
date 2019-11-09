import os
import sys
from argparse import ArgumentParser

from .dhcpd_conf import VMNetDhcpdConf
from .hosts_file import HostsFile

# TODO: make this part of default config
# TODO: Make this overridable in user config or command line options/args
HOSTS_FILE_PATH = "/etc/hosts"
VMNET_PATH = "/Library/Preferences/VMware Fusion/vmnet8"


class VMWareStaticDhcp:

    def __init__(self, hosts_path=HOSTS_FILE_PATH, vmnet_path=VMNET_PATH):
        self.hosts_file = HostsFile(path=hosts_path)
        dhcpd_conf_path = os.path.join(vmnet_path, "dhcpd.conf")
        self.vmnet_dhcpd_conf = VMNetDhcpdConf(dhcpd_conf_path)

    def add_static_dhcp(self, hostname, macaddr, ip_addr):
        self.vmnet_dhcpd_conf.add_host_section(hostname, macaddr, ip_addr)
        self.hosts_file.add_host_entry(ip_addr, hostname, None)

    def write_updated_files(self, hosts_path, dhcpd_conf_path):
        self.hosts_file.write_hosts(hosts_path)
        self.vmnet_dhcpd_conf.write_dhcpd_conf(dhcpd_conf_path)


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument("updated_hosts_path", help="Path to updated hosts file")
    parser.add_argument("updated_dhcpd_conf_path", help="Path to update dhcpd.conf file.")
    parser.add_argument("--hw-addr", help="MAC address", required=True)
    parser.add_argument(
        "--ip-addr", help="IP address to reserve", required=True)
    parser.add_argument(
        "--hostname", help="hostname to associate with IP address.", required=True)
    args = parser.parse_args(argv)
    return args


def main(argv):
    args = parse_args(argv)
    new_hosts = args.updated_hosts_path
    new_dhcpd_conf = args.updated_dhcpd_conf_path
    macaddr = args.hw_addr
    ip_addr = args.ip_addr
    hostname = args.hostname
    vmnet_dhcp = VMWareStaticDhcp()
    vmnet_dhcp.add_static_dhcp(hostname, macaddr, ip_addr)
    vmnet_dhcp.write_updated_files(new_hosts, new_dhcpd_conf)


if __name__ == "__main__":
    main(sys.argv[1:])
