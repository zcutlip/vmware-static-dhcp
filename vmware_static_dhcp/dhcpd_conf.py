class MalformedDhcpdConfHostSection(Exception):
    pass


class MalformedDhcpdConf(Exception):
    pass


class DhcpdConfHostSection:

    def __init__(self, hostname, macaddr, ip_addr, options={}):
        self.hostname = hostname
        self.macaddr = macaddr
        self.ip_addr = ip_addr
        self.options = options

    @classmethod
    def parse_host_section(cls, section_lines):
        hostname = None
        macaddr = None
        ip_addr = None
        options = {}
        cls._sanity_check(section_lines)
        line = section_lines[0]
        line = line.rstrip("{")
        parts = line.split()
        if len(parts) != 2:
            raise MalformedDhcpdConfHostSection(
                "Malformed host section, line 0: {}".format(line))
        hostname = parts[1]
        for line in section_lines[1:-1]:
            line = line.lstrip()
            if line.startswith("hardware ethernet"):
                macaddr = cls._parse_hw_ethernet(line)
            elif line.startswith("fixed-address"):
                ip_addr = cls._parse_fixed_addr(line)
            elif line.startswith("option"):
                option_name, option_val = cls._parse_option(line)
                options[option_name] = option_val

        return (hostname, macaddr, ip_addr, options)

    @classmethod
    def _parse_hw_ethernet(cls, line):
        orig_line = line
        line = line.strip()
        line = line.strip(";")
        parts = line.split()
        if len(parts) != 3:
            raise MalformedDhcpdConfHostSection(
                "Unrecognized hardware ethernet line: {}".format(orig_line))

        return parts[-1]

    @classmethod
    def _parse_fixed_addr(cls, line):
        orig_line = line
        line = line.strip()
        line = line.strip(";")
        parts = line.split()
        if len(parts) != 2:
            raise MalformedDhcpdConfHostSection(
                "Unrecognized fixed-address line: {}".format(orig_line))
        return parts[-1]

    @classmethod
    def _parse_option(cls, line):
        orig_line = line
        line = line.strip()
        line = line.strip(";")
        parts = line.split()
        if len(parts) != 3:
            raise MalformedDhcpdConfHostSection(
                "Unrecognized option line: {}".format(orig_line))

        option_name, option_value = (parts[1], parts[2])

        return (option_name, option_value)

    @classmethod
    def _sanity_check(cls, section_lines):
        if len(section_lines) < 2:
            raise(MalformedDhcpdConfHostSection(
                "Malformed host section. Not enough linses to be complete."))

        line = section_lines[0]
        if not (line.startswith("host") and line.endswith("{")):
            raise MalformedDhcpdConfHostSection(
                "Malformed host section, line 0: {}".format(line))

        line = section_lines[-1]
        if line != "}":
            raise MalformedDhcpdConfHostSection(
                "Malformed host section, line {}: {}".format(len(section_lines) - 1, line))

    def __str__(self):
        _str = "host {} {{\n".format(self.hostname)
        _str += "\thardware ethernet {};\n".format(self.macaddr)
        _str += "\tfixed-address {};\n".format(self.ip_addr)
        for k, v in self.options:
            _str += "\toption {} {};\n".format(k, v)
        _str += "}\n"
        return _str


class VMNetDhcpdConf:

    def __init__(self, path):
        self.hostname_map = {}
        self.mac_addr_map = {}
        self.ip_addr_map = {}
        vmnet_lines, host_sections = self._parse_dhcp_conf(path)
        self.path = path
        self.vmnet_lines = vmnet_lines
        self.host_sections = host_sections

    def _parse_dhcp_conf(self, path):
        vmnet_lines = []
        hosts_start_line_num = -1
        host_section_lines = []
        host_sections = []

        lines = open(path, "r").readlines()
        for linenum, line in enumerate(lines):
            line = line.rstrip()
            if 'End of "DO NOT MODIFY SECTION"' in line:
                vmnet_lines.append(line)
                hosts_start_line_num = linenum + 1
                break
            vmnet_lines.append(line)

        host_section_started = False
        current = hosts_start_line_num - 1
        for line in lines[hosts_start_line_num:]:
            current += 1
            line = line.strip()
            if len(line) == 0:  # we can skip all empty or whitespace-only lines
                continue
            elif line.endswith("{"):
                if not host_section_started:  # start of a host section
                    host_section_started = True
                else:  # shouldn't be any open-braces inside a host section
                    raise MalformedDhcpdConf(
                        "Line {}: unrecognized line inside a host section: {}".format(current, line))
                host_section_lines.append(line)
                continue
            elif line.endswith("}"):
                if not host_section_started:  # shoudln't be any close-braces outside a host section
                    raise MalformedDhcpdConf(
                        "Line {}: unrecognized closing bracket outside a host section: {}".format(current, line))
                else:
                    host_section_lines.append(line)
                    hostname, macaddr, ip_addr, options = DhcpdConfHostSection.parse_host_section(host_section_lines)
                    host_section = DhcpdConfHostSection(hostname, macaddr, ip_addr, options=options)
                    self._update_maps(hostname, macaddr, ip_addr, host_section)
                    host_sections.append(host_section)
                    host_section_lines = []
                    host_section_started = False
            else:  # line must be non-empty, and not '{ or '}'
                if host_section_started:
                    host_section_lines.append(line)
                else:
                    raise MalformedDhcpdConf(
                        "Line {}: unrecognized line outside a host section: {}".format(current, line))

        return (vmnet_lines, host_sections)

    def _update_maps(self, hostname, macaddr, ip_addr, host_section):
        macaddr = macaddr.lower()
        hostname = hostname.lower()
        if hostname in self.hostname_map:
            raise MalformedDhcpdConf(
                "Duplicate hostname found: {}".format(hostname))

        if macaddr in self.mac_addr_map:
            raise MalformedDhcpdConf("Duplicate MAC address found: {}".format(macaddr))

        if ip_addr in self.ip_addr_map:
            raise MalformedDhcpdConf("Duplicate IP Address found: {}".format(ip_addr))

        self.hostname_map[hostname] = host_section
        self.mac_addr_map[macaddr] = host_section
        self.ip_addr_map[ip_addr] = host_section

    def add_host_section(self, hostname, macaddr, ip_addr):
        host_section = DhcpdConfHostSection(hostname, macaddr, ip_addr)
        self._update_maps(hostname, macaddr, ip_addr, host_section)
        self.host_sections.append(host_section)

    def write_dhcpd_conf(self, outpath):
        print("Writing updated dhcpd configuration to {}".format(outpath))
        with open(outpath, "w") as out:
            for line in self.vmnet_lines:
                out.write(line + "\n")
            out.write("\n")
            for section in self.host_sections:
                out.write(str(section))
                out.write("\n")


if __name__ == "__main__":
    conf = VMNetDhcpdConf("./dhcpd.conf")
    for host in conf.host_sections:
        print(str(host))
        print("")
