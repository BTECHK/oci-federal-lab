# Linux Systems Administration & Networking Primer

A practical reference covering server diagnostics, networking fundamentals, enterprise patching, DNS, TLS, and cloud storage — with emphasis on FedRAMP and government environments.

---

## Server Down — Diagnostic Tree

When a service is reported down, follow this order.

### Step 1: Is the service actually running? (~40% of tickets)

- `systemctl status <service>` — asks the OS if the service is running, crashed, or stopped. Shows current state and recent log lines.
- `ps aux | grep <process>` — lists every running process, filters for a name. If nothing shows, it's not running.

If stopped/crashed, check logs, restart, done.

### Step 2: Can you reach the server?

Try `ping -c 4 <server-ip>` first (`-c 4` = stop after 4 attempts). If ICMP is blocked (common in FedRAMP/DoD), use TCP-based alternatives.

### Ping Alternatives When ICMP Is Blocked

- `nc -zv <ip> <port> -w 3` — TCP connect to a known port. `-z` = just check, don't send data. `-v` = verbose. `-w 3` = timeout after 3 seconds.
- `curl -sI --connect-timeout 5 https://<ip>:<port>` — HTTP-level probe. `-s` = silent (no progress bar). `-I` = headers only. `--connect-timeout 5` = bail after 5 seconds.
- `ssh -o ConnectTimeout=5 user@<ip>` — if you get a login prompt, the server is alive. `-o ConnectTimeout=5` = don't hang forever.
- `nmap -Pn -p 22,443 <ip>` — scan specific ports. `-Pn` = skip ping/host discovery (critical when ICMP is blocked). `-p 22,443` = only check those ports.
- `traceroute -T -p 443 <ip>` — TCP traceroute that bypasses ICMP blocks. `-T` = use TCP. `-p 443` = target port.
- `openssl s_client -connect <ip>:443` — attempts a full TLS handshake. If it connects and shows a certificate, the server is up and HTTPS is working.

Any TCP response = server is alive, ICMP is just filtered at the firewall.

### Path A — No Response (ping and TCP alternatives all fail)

1. **Cloud console** — check if the instance is running (AWS EC2 console, OCI console, Azure portal). If stopped or terminated, that's the answer.
2. **Security groups / NACLs / NSGs** — check if a recent firewall rule change locked down ingress.
3. **Serial console** — if truly unreachable, use cloud serial console for boot errors, kernel panics, disk corruption. Doesn't require network access.
4. **Check from another source** — try reaching the server from a different subnet, VPN, or bastion host to rule out your own network being the problem.

### Path B — Server Responds

1. **Service status + logs:** `systemctl status <service>` then `journalctl -u <service> -n 100 --no-pager` (`-u` = specific service, `-n 100` = last 100 lines, `--no-pager` = dump to terminal).
2. **Resource exhaustion:** `df -h` (disk space, `-h` = human-readable), `free -h` (RAM), `top -bn1 | head -20` (CPU snapshot; `-b` = batch mode, `-n1` = one snapshot).
3. **Port listening:** `ss -tlnp | grep <port>` (`-t` = TCP, `-l` = listening only, `-n` = numeric ports, `-p` = show owning process). Also check `iptables -L -n` for host firewall rules (`-L` = list rules, `-n` = numeric output).
4. **Application health:** `curl -v http://localhost:<port>/health` (`-v` = verbose, shows full request/response). If port is open but app returns 5xx, check app config, database connectivity, cert expiry.

### Path C — Intermittent Failures

- `mtr --tcp -P 443 <ip>` — live traceroute with packet loss stats over TCP. `--tcp` = bypass ICMP. `-P 443` = target port.
- `tcpdump -i eth0 host <ip> -c 50` — capture raw packets. `-i eth0` = listen on that interface. `-c 50` = stop after 50 packets.
- `dig <hostname>` / `nslookup <hostname>` — check DNS resolution. Stale cache or wrong records can make a healthy server look dead.

---

## Nmap and Network Scanning Warnings

Running a full `nmap` scan (without `-p` to limit ports) sweeps thousands of ports and looks identical to attack reconnaissance. IDS/IPS systems (Snort, Suricata, CrowdStrike) will flag it immediately.

**Safe usage:** `nmap -Pn -p 22,443 10.0.1.5` — targeted check of specific ports on a server you own. Clear it with your security team first in FedRAMP environments.

**Dangerous usage:** `nmap 10.0.1.0/24` — scanning an entire subnet will get you a meeting with your ISSO.

**Other tools that need authorization:** `nmap -sS` (SYN/half-open scan, IDS specifically watches for this), `nmap -O` (OS fingerprinting, very noisy), `tcpdump`/`wireshark` (packet sniffers that can capture others' traffic), `masscan` (internet-scale scanning).

**General rule:** On any enterprise or government network, if a tool sends unsolicited packets to machines you don't own or captures traffic passively, get written authorization first. Even for your own servers, notify the SOC.

---

## Enterprise IT Tips (What You Learn on the Job)

- **DNS before everything.** Check `dig <hostname>` first. Half of "server down" tickets are actually DNS issues.
- **Always specify timeouts.** Every network command should have a timeout flag. Without one, commands hang 30-120 seconds on dead hosts.
- **`sudo` awareness.** Many diagnostic commands give incomplete results without root. `ss -tlnp` won't show process names, `tcpdump` won't run at all, `iptables -L` shows nothing useful.
- **Localhost vs bind address.** A service can be "running" and "listening" but only on `127.0.0.1`, rejecting all external connections. Check `ss -tlnp` output for the listen address.
- **Test from the right place.** Enterprise networks are segmented. Test connectivity FROM the machine having the problem, not from your workstation.
- **Certificates expire silently.** An HTTPS service "goes down" but everything else checks out — check the TLS cert with `openssl s_client`. Expired certs don't crash the service; they make every client reject the connection.
- **Firewalls are layered.** Cloud security group, subnet NACL/security list, host firewall (`iptables`/`firewalld`/`ufw`), and sometimes a WAF. A rule can be open at one layer and blocked at another.
- **Don't restart first, investigate first.** `systemctl restart` destroys evidence — logs, process state, memory dumps. Read `journalctl` and `systemctl status` before restarting. In FedRAMP, you may need the forensic trail for incident reporting.
- **Change control correlation.** Ask "what changed?" before "what's broken?" Check CI/CD pipelines, change management boards, Slack.
- **`curl -v` is the swiss army knife.** Tests DNS resolution, TCP connection, TLS handshake, and HTTP response in one shot. Shows exactly where the failure occurred.

---

## Localhost vs Bind Address

**Localhost (127.0.0.1)** is a loopback address — the machine talking to itself. Traffic never leaves the machine or touches the network card.

**Bind address** determines which network interfaces a service accepts connections on:

- `bind 127.0.0.1` — only accepts local connections. External clients get "connection refused."
- `bind 10.0.1.5` — only accepts connections on that specific interface.
- `bind 0.0.0.0` — accepts connections on ALL interfaces.

**How to spot it:** In `ss -tlnp` output, the fourth column shows the listen address:

- `127.0.0.1:5432` — localhost only, external connections refused
- `0.0.0.0:5432` — all interfaces, wide open
- `:::5432` — same as 0.0.0.0 for IPv6

**Common scenario:** Install Postgres, app on another server can't connect, firewall is open, `ss` shows it's listening — but on `127.0.0.1`. Fix: edit config to change `listen_addresses` to `'*'` and restart.

---

## Host Firewalls: iptables vs firewalld vs ufw

All three are host-level firewalls that talk to the same underlying kernel system (netfilter). The difference is the frontend.

**`iptables`** — the old-school option. Powerful but verbose. Rules are sequential (first match wins). No built-in persistence across reboots. Common on older systems, Amazon Linux 2, minimal installs, and air-gapped government environments.

**`firewalld`** — the modern daemon-based option. Uses zones (public, trusted, internal, dmz) instead of raw rules. Supports runtime changes without restart. Default on RHEL 7+, CentOS 7+, Oracle Linux, most FedRAMP Red Hat environments.

**`ufw`** (Uncomplicated Firewall) — the simple Ubuntu/Debian frontend. `ufw allow 22` and done. Writes iptables rules under the hood.

**Check which is active:** `systemctl status firewalld` or `ufw status`. Don't mix them — they overwrite each other.

---

## Linux Distributions and Package Managers

**Unix** is the original ancestor (1970s). You can't run it today, but every modern system borrowed from it. macOS is one of the last direct descendants.

**Linux kernel** is just the core — it manages hardware, memory, and processes. Linus Torvalds created it in 1991.

**Distributions** wrap the kernel with different tools, package managers, and defaults. Two major families:

### Debian Family (uses `apt`, `.deb` packages)

- **Debian** — the foundation. Rock solid, no-frills.
- **Ubuntu** — most popular distro for developers and cloud. Friendlier experience built on Debian.

### Red Hat Family (uses `yum`/`dnf`, `.rpm` packages)

- **RHEL (Red Hat Enterprise Linux)** — the enterprise/government standard. Paid support, warranty.
- **Oracle Linux** — RHEL with Oracle's branding and support contract. Uses `dnf`/`yum`.
- **Amazon Linux** — optimized for AWS, based on Red Hat/Fedora family. Uses `dnf`.
- **CentOS** — was the free RHEL clone. Killed in 2020, replaced by CentOS Stream.
- **Rocky Linux / AlmaLinux** — community rebuilds of the free RHEL clone after CentOS died.

**Interview gotcha:** Running `yum` on Ubuntu or `apt` on Red Hat doesn't work. Know which family you're on: `cat /etc/os-release`. Packages are different formats (`.deb` vs `.rpm`) even if the software inside is the same.

---

## Ports vs Sockets

**Port** = a number (1-65535) that identifies which service traffic is for. Like an apartment number in a building (the IP address). Port 443 = HTTPS, port 22 = SSH, port 5432 = Postgres.

**Socket** = an active connection. The combination of client IP + client port + server IP + server port. One port can have thousands of simultaneous sockets.

---

## Root Access as a Junior Admin

You almost never get root on every server. The typical model:

- You get an unprivileged user account that can SSH into servers.
- **`sudo`** provides controlled escalation. Your `/etc/sudoers` file (managed by Ansible/Puppet) grants specific commands only.
- Diagnostic commands often work without sudo. Restarting services and installing packages require it.

In **FedRAMP/government**, root access is limited to 2-3 senior people. Everything goes through a privileged access management tool (CyberArk), sessions are recorded, and every sudo command is logged to a SIEM. Credentials are checked out from a vault and auto-rotated after sessions end.

---

## Enterprise Patching Process

In enterprise and FedRAMP environments, you never pull patches directly from the internet.

### The Supply Chain

1. **Vendor releases patch.** Oracle/Red Hat/Canonical publishes a security advisory (CVE).
2. **Internal repo team pulls it.** Downloaded to an internal mirror (Satellite, Spacewalk, Artifactory, or a plain yum mirror). In air-gapped environments, this is done via data diode or approved media (sneakernet).
3. **Security team reviews.** Vulnerability management (Tenable Nessus, Qualys) confirms the CVE applies. Assigns timeline: 30 days for critical, 90 days for high (per FedRAMP continuous monitoring requirements).
4. **Test environment first.** Patch applied to dev/test. Application validated post-patch.
5. **Change request.** Submitted through change management (ServiceNow, Jira) with rollback plan.
6. **Maintenance window.** Patches applied during approved window. The actual command might be `sudo dnf update --security` (applies only security patches), but usually an orchestration tool (BigFix, Ansible, SCCM, Satellite) runs it across hundreds of servers.
7. **Validation scan.** Nessus/Qualys rescans to confirm remediation. Results go into POA&M and get reported to FedRAMP PMO.

---

## DNS Resolution Steps

When you type `www.google.com`:

1. **Browser cache** — "Did I just look this up?" If yes, use it.
2. **OS cache** — checks the OS memory and `/etc/hosts` file.
3. **Recursive resolver** — your configured DNS server (ISP, 8.8.8.8, 1.1.1.1) does the legwork.
4. **Root nameserver** — 13 addresses worldwide. Knows who handles `.com`.
5. **TLD nameserver** — the `.com` authority. Knows which nameserver is authoritative for google.com.
6. **Authoritative nameserver** — Google's own DNS server. Has the actual answer: `142.250.80.46`.
7. **Answer cached and returned** — every server remembers the answer for a duration (TTL).

### DNS Companies Mapped to Steps

| Step | Role | Companies |
|------|------|-----------|
| 0 | Domain registrar (buy the name) | GoDaddy, Namecheap, Cloudflare, Route 53, Squarespace. ICANN behind them all. |
| 1-2 | Local cache | Your machine only. No companies. |
| 3 | Recursive resolver (the librarian) | Google (8.8.8.8), Cloudflare (1.1.1.1), Quad9 (9.9.9.9), ISP default, Route 53 Resolver (AWS VPCs), internal Microsoft DNS or BIND (enterprise) |
| 4 | Root nameservers | Verisign, ICANN, NASA, US Army Research Lab, universities (13 addresses, hundreds of anycast locations) |
| 5 | TLD nameservers | Verisign (.com/.net), Public Interest Registry (.org), country orgs (.uk/.de/.jp) |
| 6 | Authoritative nameserver (the actual answer) | Cloudflare DNS, Route 53, Google Cloud DNS, Azure DNS, GoDaddy (default), self-hosted BIND/PowerDNS (gov/air-gapped) |

**Multi-role companies:** Cloudflare operates at steps 0, 3, and 6. Amazon/Route 53 operates at steps 0, 3, and 6. Google operates at steps 3 and 6. Verisign operates at steps 4 and 5.

---

## TCP Handshake

Three-step process to establish a reliable connection.

1. **SYN (client → server):** Client picks a random port (e.g., 52431), sends a packet with the SYN flag, an Initial Sequence Number (ISN, e.g., 1000), window size (buffer capacity), and MSS (max segment size).
2. **SYN-ACK (server → client):** Server responds with its own ISN (e.g., 5000) and acknowledges the client's by saying "expecting 1001 next."
3. **ACK (client → server):** Client confirms "expecting 5001 next." Connection is open.

Sequence numbers track every byte sent. If a packet is lost, the receiver never ACKs it, and the sender retransmits. This is how TCP guarantees delivery.

**Failure modes:** No SYN response = server down or firewalled. RST response = port closed. SYN-ACK then hang = stateful firewall blocking after handshake.

Cost: **1 round trip** before any higher-level protocol can begin.

---

## TLS 1.3 Handshake

Rides on top of the open TCP connection. Wraps the plaintext pipe in encryption.

1. **ClientHello (client → server):** Lists supported TLS versions, cipher suites (encryption algorithms), a client random number, and key share data (client's half of Diffie-Hellman key material).
2. **ServerHello + Certificate + Finished (server → client):** Server picks a cipher suite, sends its key share (server's half), its certificate (ID proving it's really google.com), and a Finished message (encrypted hash of everything so far).
3. **Client verifies, sends Finished:** Browser validates the certificate chain (leaf → intermediate → root CA in trust store). Checks domain match, expiry, revocation. Sends its own encrypted Finished message.

Both sides independently compute the same **session key** from the Diffie-Hellman exchange. Neither side ever sent the full key across the wire. This session key is **symmetric** (AES-256-GCM typically) — fast for bulk data. The certificate/Diffie-Hellman exchange uses **asymmetric** crypto — slow but secure for the initial secret exchange.

Cost: **1 round trip** (was 2 in TLS 1.2). With 0-RTT resumption, returning visitors can send encrypted data in the first packet.

**Total before first byte of content: 2 round trips** (1 TCP + 1 TLS).

---

## Protocols vs Message Types

**Protocol** = the language two systems agree to speak (HTTP, TCP, UDP, ICMP, DNS, TLS). Defines the rules and format.

**Message types** = the vocabulary within each protocol:

- **ICMP:** Echo Request (ping), Echo Reply, Destination Unreachable, Time Exceeded
- **TCP:** SYN, ACK, FIN, RST (immediate hangup)
- **HTTP:** GET, POST, PUT, DELETE (requests); 200 OK, 404, 500 (responses)
- **DNS:** Query, Response, NXDOMAIN (domain doesn't exist)
- **TLS:** ClientHello, ServerHello, Certificate, Finished

Blocking ICMP = blocking an entire protocol. A 403 response = a message type within HTTP.

---

## HTTP/1.1, HTTP/2, HTTP/3

The HTTP protocol (GET, POST, 200, 404) stays the same across versions. What changed is how messages travel over the wire.

**HTTP/1.1** — one request-response at a time per connection. Head-of-line blocking: if one request is slow, everything behind it waits.

**HTTP/2** — multiple requests share one TCP connection simultaneously via binary frames. But TCP still treats all data as one ordered stream — one lost packet blocks everything (head-of-line blocking moved from HTTP layer to TCP layer).

**HTTP/3** — runs over QUIC, which runs over UDP. QUIC rebuilds TCP's reliability and TLS encryption inside UDP packets. Key innovations:

- **Independent streams:** If packet for stream 7 is lost, only stream 7 waits. Streams 1-6 and 8-30 keep flowing. Eliminates TCP's head-of-line blocking entirely.
- **Built-in TLS 1.3:** Connection setup and encryption setup happen in 1 round trip (vs 2 for HTTP/2). Returning visitors get 0-RTT.
- **Connection migration:** Uses connection IDs instead of IP tuples, so connections survive network switches (WiFi to cellular).

UDP itself is stateless, but QUIC running on top of UDP is fully stateful — it manages its own sequencing, acknowledgment, retransmission, and encryption. UDP is just the envelope; QUIC is the entire postal system inside.

**Enterprise/FedRAMP:** HTTP/3 adoption is minimal because security tools can't inspect encrypted UDP (QUIC). Many enterprises actively block QUIC at the firewall and force fallback to HTTP/2 over TCP.

---

## Certificates and the Trust Chain

- **Certificate Authority (CA):** A trusted organization that issues certificates. Browsers ship with ~100-150 pre-trusted CAs.
- **Root certificate:** The CA's master credential. Kept in offline vaults, almost never directly signs anything.
- **Intermediate certificate:** A branch authority. The root delegates signing to intermediates. If compromised, only the intermediate is revoked, not the root.
- **Leaf/server certificate:** Your server's identity. Says "this server is really google.com." Signed by an intermediate, which is signed by a root.
- **Certificate chain:** The full trail: leaf → intermediate → root. Server sends leaf + intermediate(s). Browser follows the chain to a root in its trust store.
- **Self-signed certificate:** You made your own ID with no CA backing. Works for encryption, but no browser trusts it.

### Can you self-sign and put it on the internet?

Yes. `openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365` creates a self-signed cert. Traffic will be encrypted, but every visitor gets a browser warning. For a real website, use **Let's Encrypt** (free automated CA) with `certbot`. You just need a domain name ($10-15/year from any registrar). DNS, hosting, and certificates are separate systems that don't need to come from the same vendor.

### Certificate Management by Environment

**Commercial enterprise:** Internal CA (usually Microsoft AD CS) for internal services. Public CA (DigiCert, managed by Venafi) for external services. Auto-renewal or monitoring for expiry.

**FedRAMP / federal civilian:** Certs must come from a Federal PKI-approved CA. Federal Common Policy CA at the top of the trust chain. Certificate lifecycle is documented, tracked, and audited.

**Air-gapped (classified):** Entirely separate PKI with zero connection to the public internet trust chain. NSA runs the root CA for classified networks. Certificates are generated, distributed, and revoked entirely within the boundary. No Let's Encrypt, no external OCSP — everything internal.

---

## Docker Certificate Troubleshooting in Enterprise

When containers can't reach the internet through an enterprise network, the cert injection process is:

1. Export enterprise root/intermediate CA certs from Windows cert store or GPO.
2. Convert to PEM format.
3. Copy into container at `/usr/local/share/ca-certificates/` (Debian) or `/etc/pki/ca-trust/source/anchors/` (Red Hat).
4. Run `update-ca-certificates` (Debian) or `update-ca-trust` (Red Hat).

**Common reasons this still fails:**

- **Proxy settings missing.** Enterprise networks require traffic through a proxy (Zscaler, Bluecoat). Docker needs `HTTP_PROXY` / `HTTPS_PROXY` set in BOTH the Docker daemon config AND inside the container.
- **TLS inspection.** Enterprise proxies do man-in-the-middle on HTTPS — they decrypt, inspect, and re-encrypt with the enterprise CA cert. That's why you need the internal CA certs in the first place.
- **Network-level blocks.** Docker Hub domains may be blocked at the firewall or DNS level.
- **Docker daemon proxy config.** Needs to be set in `/etc/systemd/system/docker.service.d/proxy.conf`, not just environment variables.

In government environments, the proper solution is an **internal container registry** (Harbor, Nexus, Artifactory) that mirrors approved images. Docker pulls only from the internal registry, same pattern as patching.

---

## Reading Server Output: Memory, Disk, and LVM

### Memory (`free -h`)

- **buff/cache** — Linux intentionally uses "unused" RAM as disk cache. Empty RAM is wasted RAM. The kernel drops cache instantly when applications need memory.
- **available** — the number that actually matters. It equals free + reclaimable cache. If someone panics about low `free`, point to `available`.
- **swap** — overflow parking for RAM. A file or partition on disk that Linux uses when physical RAM is full. Swap at 0B used = server has plenty of RAM.

### Thrashing

Thrashing occurs when the system spends more time moving data between RAM and swap than doing useful work. Detect it with `vmstat 1` — watch the `si` (swap in) and `so` (swap out) columns. Consistently high values + unresponsive system = thrashing. Fix: add RAM, kill the memory-hungry process, or tune the application.

### I/O (Input/Output)

I/O wait = CPU waiting for disk. CPU operates in nanoseconds, disk in milliseconds.

- `top` — look at `%wa` in the header. Above 20-30% = disk bottleneck.
- `iostat -x 1` — per-disk utilization. Watch `%util` and `await`.
- `iotop` — shows which process is hammering the disk.

Common I/O killers: full table scans, runaway log rotation, backup jobs during business hours, or disks above 95% full (fragmentation craters performance).

### Disk and LVM (`df -h`, `lsblk`, `pvs/vgs/lvs`)

**LVM (Logical Volume Manager)** layers: Physical Volumes (raw disks, `pvs`) → Volume Groups (pools, `vgs`) → Logical Volumes (usable partitions, `lvs`).

**PFree = 0** in `vgs` means the entire pool is allocated. No room to extend existing volumes without adding new storage or shrinking an existing volume (XFS doesn't support shrinking).

### Extending a Logical Volume (when PFree > 0)

```
sudo lvextend -L +10G /dev/ocivolume/root
sudo xfs_growfs /          # for XFS
sudo resize2fs /dev/...    # for ext4
```

The second command is critical — LVM grows the block device, but the filesystem doesn't know it grew until you explicitly expand it.

### Attaching New Cloud Storage (OCI / AWS)

1. **Create the volume** in the cloud console (must match the instance's availability domain/zone).
2. **Attach it** to the instance (paravirtualized or iSCSI on OCI; direct attach on AWS).
3. **Find the new disk:** `lsblk` shows a new device (e.g., `sdb`) with no partitions.
4. **Choose your approach:**
   - **Add to LVM:** `pvcreate /dev/sdb` → `vgextend ocivolume /dev/sdb` → `lvextend` → `xfs_growfs`
   - **Standalone mount:** `mkfs.xfs /dev/sdb` → `mkdir /data` → `mount /dev/sdb /data` → add to `/etc/fstab`
5. **fstab rules:** Always use UUID (from `blkid`) instead of `/dev/sdb` — device names can change between reboots. On OCI iSCSI volumes, include the `_netdev` flag or the server hangs on reboot waiting for a network disk before the network is up.
6. **Verify:** `df -h` and `lsblk`.

No reboot required. The entire process takes about 5 minutes.

---

## Linux vs Windows: File System Comparison

If you're coming from a Windows background, the mental shift is that Linux has no drive letters. Everything lives under a single root `/` — including other disks, USB drives, and network shares. They just get mounted as folders.

| Concept | Windows | Linux |
|---------|---------|-------|
| Root of everything | `C:\` | `/` |
| Path separator | Backslash `\` | Forward slash `/` |
| Drive letters | `C:\`, `D:\`, `E:\` | No drive letters. Other disks mount as directories (e.g., `/mnt/data`, `/media/usb`) |
| User home folder | `C:\Users\yourname` | `/home/yourname` |
| Admin home folder | `C:\Users\Administrator` | `/root` |
| Desktop | `C:\Users\yourname\Desktop` | `/home/yourname/Desktop` (if GUI installed; servers usually don't have one) |
| Program files | `C:\Program Files\` | `/usr/bin/`, `/usr/local/bin/`, or `/opt/` |
| System files | `C:\Windows\System32\` | `/usr/lib/`, `/lib/`, `/usr/sbin/` |
| Temp files | `C:\Temp` or `%TEMP%` | `/tmp` |
| Configuration | Registry + `C:\ProgramData\` | Text files in `/etc/` |
| Logs | Event Viewer + `C:\Windows\Logs\` | Text files in `/var/log/` |
| Startup services | Services (services.msc) | `systemd` units in `/etc/systemd/` |
| Device access | Device Manager | `/dev/` (everything is a file — disks, USBs, terminals) |
| Package install | `.exe` / `.msi` installers, Windows Store | `apt` / `dnf` / `yum` from repositories |
| Hidden files | File attribute (right-click → properties) | Filename starts with a dot (`.bashrc`, `.ssh/`) |
| File permissions | ACLs via Security tab | `rwx` (read/write/execute) for owner, group, others. Managed with `chmod`, `chown` |
| Case sensitivity | `File.txt` = `file.txt` (case-insensitive) | `File.txt` ≠ `file.txt` (case-sensitive) |
| Line endings | `\r\n` (carriage return + line feed) | `\n` (line feed only). Mixing these causes subtle bugs when moving scripts between Windows and Linux. |
| Text editor | Notepad, VS Code | `vi`/`vim`, `nano`, VS Code (remote SSH) |

**The biggest mental shift:** In Windows, configuration lives in the registry (a binary database you edit with `regedit`). In Linux, configuration is plain text files in `/etc/`. You edit them with a text editor. This makes Linux configs easy to version control, diff, copy between servers, and manage with automation tools like Ansible.

---

## Linux Directory Structure — What Each Folder Does

Everything in Linux hangs off the root `/`. Here's what each default directory is for and when you'd actually touch it as an admin.

### `/` — Root

The top of the tree. Everything else is a subdirectory of this. Equivalent to `C:\` on Windows, except ALL disks mount somewhere under here — there's no `D:\`.

### `/home` — User home directories

Each user gets a folder: `/home/jsmith`, `/home/opc`, etc. Personal files, SSH keys (in `~/.ssh/`), shell configs (`.bashrc`, `.bash_profile`). On servers, this is small because users shouldn't be storing personal files on production systems. The `~` shortcut always points to the current user's home directory.

### `/root` — Root user's home directory

Not to be confused with `/` (the filesystem root). This is the home folder for the `root` superuser. It's at `/root` instead of `/home/root` because `/home` might be on a separate disk that hasn't mounted yet during early boot — root needs a home directory that's always available.

### `/etc` — Configuration files

The most important directory for a sysadmin. Almost every service stores its config here as plain text files.

- `/etc/ssh/sshd_config` — SSH server configuration
- `/etc/fstab` — disk mount table (you saw this in your OCI server output)
- `/etc/hosts` — manual DNS overrides
- `/etc/resolv.conf` — which DNS servers to use
- `/etc/passwd` — user accounts (not actually passwords despite the name)
- `/etc/shadow` — the actual hashed passwords (root-readable only)
- `/etc/sudoers` — who can run sudo and what commands they're allowed
- `/etc/systemd/system/` — custom service unit files
- `/etc/yum.repos.d/` or `/etc/apt/sources.list.d/` — package repository configs
- `/etc/pki/` (Red Hat) or `/etc/ssl/` (Debian) — certificate trust store

When someone says "check the config," they mean look in `/etc/`.

### `/var` — Variable data (things that change)

Files that grow, shrink, get created, and get deleted during normal operation.

- `/var/log/` — system and application logs. `messages` or `syslog` (general), `secure` or `auth.log` (login attempts), `audit/audit.log` (SELinux/auditd). This is where you look after checking `journalctl`.
- `/var/lib/` — application state data. Databases often store data here (e.g., `/var/lib/mysql/`, `/var/lib/pgsql/`).
- `/var/tmp/` — temporary files that persist across reboots (unlike `/tmp`).
- `/var/cache/` — cached package downloads, etc.
- `/var/spool/` — queued work (print jobs, cron jobs, mail).

**When `/var` fills up, services die.** Logs grow forever if not rotated. Databases write here. This is the most common disk-full culprit on servers.

### `/tmp` — Temporary files

Scratch space that any user or process can write to. Automatically cleaned on reboot (and sometimes periodically by `systemd-tmpfiles`). Don't put anything here you need to keep.

### `/usr` — User programs and system software

Despite the name, this has nothing to do with individual users. It's where installed software lives.

- `/usr/bin/` — most user commands (`ls`, `grep`, `curl`, `vim`, `python3`). The equivalent of `C:\Program Files\` for command-line tools.
- `/usr/sbin/` — system administration commands (`fdisk`, `iptables`, `useradd`). Historically needed root to run; modern systems often merge this with `/usr/bin/`.
- `/usr/lib/` — shared libraries (like `.dll` files on Windows).
- `/usr/local/` — software you compiled and installed manually (not from a package manager). `/usr/local/bin/` is the conventional place for custom scripts and locally built tools.
- `/usr/share/` — architecture-independent data like documentation and man pages.

### `/bin` and `/sbin` — Essential commands

On older systems, `/bin` had basic commands (`ls`, `cp`, `cat`) and `/sbin` had admin commands (`mount`, `reboot`). These were separate from `/usr/bin` so they'd be available even if `/usr` was on a separate disk that hadn't mounted. On modern systems (RHEL 7+, Ubuntu 16.04+), `/bin` and `/sbin` are just symlinks to `/usr/bin` and `/usr/sbin`. You'll see both paths used interchangeably.

### `/opt` — Optional / third-party software

Where large, self-contained third-party applications install themselves. Things like `/opt/oracle`, `/opt/splunk`, `/opt/CrowdStrike`. Think of it as the Linux equivalent of `C:\Program Files\` for commercial software that ships as a bundle rather than a package.

### `/dev` — Device files

Linux treats everything as a file, including hardware. This directory contains special files that represent devices.

- `/dev/sda` — first disk, `/dev/sdb` — second disk (these appeared in your `lsblk` output)
- `/dev/sda1`, `/dev/sda2` — partitions on the first disk
- `/dev/null` — the black hole. Anything written here disappears. Used to discard output: `command > /dev/null`
- `/dev/zero` — infinite stream of zeros. Used to wipe disks or create empty files.
- `/dev/tty` — the current terminal

You rarely touch files in `/dev` directly. Tools like `fdisk`, `mkfs`, and `mount` interact with them for you.

### `/proc` — Process information (virtual)

Not a real directory on disk — it's a virtual filesystem generated by the kernel in real time. Every running process gets a numbered directory (`/proc/1234/`) containing its status, memory maps, open files, etc.

- `/proc/cpuinfo` — CPU details
- `/proc/meminfo` — detailed memory breakdown (what `free` reads from)
- `/proc/loadavg` — system load average
- `/proc/mounts` — currently mounted filesystems

Useful for scripting and debugging. `cat /proc/cpuinfo` tells you how many cores, what model CPU, what speed.

### `/sys` — System/hardware info (virtual)

Similar to `/proc` but focused on hardware and kernel subsystems. Used by the kernel to expose hardware configuration. You'll rarely interact with it directly unless tuning network parameters or hardware settings.

### `/boot` — Boot files

Contains the Linux kernel (`vmlinuz`), initial RAM disk (`initramfs`), and bootloader config (GRUB). Your OCI server had this as a separate 2GB partition — standard practice so the bootloader can always find these files regardless of LVM or disk layout.

### `/mnt` and `/media` — Mount points

- `/mnt` — traditional location for temporarily mounting filesystems. Admins use it for manual mounts (`mount /dev/sdb1 /mnt`).
- `/media` — where the OS auto-mounts removable media (USB drives, CDs) on desktop Linux. Rarely used on servers.

In cloud environments, additional block volumes often mount at custom paths like `/data` or `/var/data` rather than under `/mnt`.

### `/srv` — Service data

Intended for data served by the system (web server files, FTP files). In practice, many organizations ignore this and put web content in `/var/www/` or `/opt/` instead. You'll see it used inconsistently.

### Quick Reference: Where to Look for Common Tasks

| Task | Directory |
|------|-----------|
| Edit a service's configuration | `/etc/` |
| Read logs after an incident | `/var/log/` or `journalctl` |
| Find where a command is installed | `which <command>` (usually `/usr/bin/`) |
| Check disk devices and partitions | `/dev/` via `lsblk` |
| Check CPU, memory, kernel info | `/proc/cpuinfo`, `/proc/meminfo` |
| Find a user's SSH keys | `/home/<user>/.ssh/` |
| Install custom scripts | `/usr/local/bin/` |
| Find third-party enterprise software | `/opt/` |
| Check what's eating disk space | `du -sh /var/*`, `du -sh /home/*`, `du -sh /tmp/*` |
| Check certificate trust store | `/etc/pki/tls/` (Red Hat) or `/etc/ssl/certs/` (Debian) |