class MalformedHostsEntryException(Exception):
    pass


class MalformedHostsFileException(Exception):
    pass


class HostsEntry:
    ADDR_COLUMN_WIDTH = 24
    FOUR_SPACES = "    "

    def __init__(self, addr, hostname, comment):
        self._sanity_check(addr, hostname)
        self.address = addr
        self.hostname = hostname
        self.comment = comment
        self.blank_line = self._is_blank_line(addr, hostname, comment)

    @classmethod
    def parse_hostline(cls, hostline):
        addr = None
        hostname = None
        comment = None
        if hostline.startswith("#"):
            comment = hostline
        else:
            parts = hostline.split(maxsplit=2)
            if len(parts):
                addr = parts.pop(0)
            if len(parts):
                hostname = parts.pop(0)
            if len(parts):
                comment = parts.pop(0)

        return (addr, hostname, comment)

    def _sanity_check(self, addr, hostname):
        addr_hostname = [addr, hostname]
        if None in addr_hostname:
            if [None, None] != addr_hostname:
                raise MalformedHostsEntryException(
                    "Malformed address/hostname pair: {}".format(str(addr_hostname)))

    def _is_blank_line(self, addr, hostname, comment):
        return [None, None, None] == [addr, hostname, comment]

    def __str__(self):
        _str = None
        if [self.address, self.hostname] == [None, None] and self.comment is not None:
            _str = self.comment
        elif self.blank_line:
            _str = ""
        else:
            fmt = "{:%ds}" + self.FOUR_SPACES + "{:s}"
            fmt = fmt % self.ADDR_COLUMN_WIDTH
            _str = fmt.format(self.address, self.hostname)
            if self.comment is not None:
                _str += self.FOUR_SPACES + self.comment

        return _str


class HostsFile:
    def __init__(self, path="/etc/hosts"):
        hosts, address_map = self._parse_hosts_file(path)
        self.hosts = hosts
        self.address_map = address_map

    def _parse_hosts_file(self, path):
        entries = []
        address_map = {}
        lines = open(path, "r").read().splitlines()
        for line in lines:
            addr, hostname, comment = HostsEntry.parse_hostline(line)
            entry = HostsEntry(addr, hostname, comment)
            if entry.address is not None:
                if entry.address in address_map:
                    raise MalformedHostsFileException("Duplicate address: {}".format(line))
                else:
                    address_map[entry.address] = entry
            entries.append(entry)
        return (entries, address_map)

    def add_host_entry(self, addr, hostname, comment):
        if addr in self.address_map:
            raise MalformedHostsEntryException("Address already in hosts file: {}".format(addr))
        entry = HostsEntry(addr, hostname, comment)
        self.address_map[addr] = entry
        self.hosts.append(entry)

    def remove_host_entry(self, addr):
        if addr not in self.address_map:
            raise Exception("Address not found: {}".format(addr))
        entry = self.address_map[addr]
        self.hosts.remove(entry)

    def write_hosts(self, outpath):
        with open(outpath, "w") as outhosts:
            for entry in self.hosts:
                outhosts.write("{}\n".format(str(entry)))


if __name__ == "__main__":
    hosts = HostsFile(path="/etc/hosts")
    for host in hosts.hosts:
        print(str(host))
