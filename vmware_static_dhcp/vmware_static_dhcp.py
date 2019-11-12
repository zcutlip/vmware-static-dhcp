import os
import sys
import tempfile
from argparse import ArgumentParser
from configure_with_sudo import GenericConfigure

from .dhcpd_conf import VMNetDhcpdConf
from .hosts_file import HostsFile

# TODO: make this part of default config
# TODO: Make this overridable in user config or command line options/args
HOSTS_FILE_PATH = "/etc/hosts"
VMNET_PATH = "/Library/Preferences/VMware Fusion/vmnet8"


class CopyFileWithSudo(GenericConfigure):

    def __init__(self, src, dst, cp_path="/bin/cp", kill_sudo_cred=True):
        argv = [cp_path, src, dst]
        super().__init__(argv, use_sudo=True, kill_sudo_cred=kill_sudo_cred)


class VMWareStaticDhcp:

    def __init__(self, hosts_path=HOSTS_FILE_PATH, vmnet_path=VMNET_PATH):
        self.hosts_file = HostsFile(path=hosts_path)
        dhcpd_conf_path = os.path.join(vmnet_path, "dhcpd.conf")
        self.vmnet_dhcpd_conf = VMNetDhcpdConf(dhcpd_conf_path)

    def add_static_dhcp(self, hostname, macaddr, ip_addr):
        self.vmnet_dhcpd_conf.add_host_section(hostname, macaddr, ip_addr)
        self.hosts_file.add_host_entry(ip_addr, hostname, None)

    def write_updated_files(self, hosts_path, dhcpd_conf_path, use_sudo=False):
        if use_sudo:
            tempdir = tempfile.mkdtemp()
            hosts_base = os.path.basename(hosts_path)
            hosts_out = os.path.join(tempdir, hosts_base)
            dhcpd_conf_base = os.path.basename(dhcpd_conf_path)
            dhcpd_conf_out = os.path.join(tempdir, dhcpd_conf_base)
        else:
            hosts_out = hosts_path
            dhcpd_conf_out = dhcpd_conf_path

        self.hosts_file.write_hosts(hosts_out)
        self.vmnet_dhcpd_conf.write_dhcpd_conf(dhcpd_conf_out)
        if use_sudo:
            hosts_copier = CopyFileWithSudo(hosts_out, hosts_path, kill_sudo_cred=False)
            hosts_copier.execute()
            dhcpcd_conf_copier = CopyFileWithSudo(dhcpd_conf_out, dhcpd_conf_path)
            dhcpcd_conf_copier.execute()


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument("updated_hosts_path", help="Path to updated hosts file")
    parser.add_argument("updated_dhcpd_conf_path", help="Path to update dhcpd.conf file.")
    parser.add_argument("--hw-addr", help="MAC address", required=True)
    parser.add_argument(
        "--ip-addr", help="IP address to reserve", required=True)
    parser.add_argument(
        "--hostname", help="hostname to associate with IP address.", required=True)
    parser.add_argument(
        "--use-sudo", help="Use 'sudo' to elevate privileges before writing updated files.", action='store_true')
    args = parser.parse_args(argv)
    return args


def main(argv):
    args = parse_args(argv)
    new_hosts = args.updated_hosts_path
    new_dhcpd_conf = args.updated_dhcpd_conf_path
    macaddr = args.hw_addr
    ip_addr = args.ip_addr
    hostname = args.hostname
    use_sudo = args.use_sudo
    vmnet_dhcp = VMWareStaticDhcp()
    vmnet_dhcp.add_static_dhcp(hostname, macaddr, ip_addr)
    vmnet_dhcp.write_updated_files(new_hosts, new_dhcpd_conf, use_sudo=use_sudo)


if __name__ == "__main__":
    main(sys.argv[1:])
