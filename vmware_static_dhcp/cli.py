import sys

from .version import Vmware_static_dhcpAbout as About


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    print("vmware_static_dhcp main()")
    print("%s" % About())
    if argv:
        print("args:")
        for arg in argv:
            print(arg)
    else:
        print("No args provided")


if __name__ == "__main__":
    main(sys.argv[1:])
