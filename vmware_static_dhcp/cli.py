import sys
from .vmware_static_dhcp import main as vmware_main


def main():
    vmware_main(sys.argv[1:])
