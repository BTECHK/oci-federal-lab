# Admin Day P2 — Networking + Storage + k3s OS-Level

**Estimated effort:** ~6 focused hours.
**Goal:** Intermediate Linux admin reps — iptables/firewalld, LVM, network namespaces, sysctl tuning, k3s node OS troubleshooting, certificate stores.

## Sections

### 1. iptables / firewalld hands-on (60 min)

**Activities:**
- `firewall-cmd --list-all` — current state on each zone
- Add a service: `firewall-cmd --add-port=8000/tcp --zone=public --permanent`; reload; verify
- Inspect underlying iptables: `iptables -L -n -v`
- NAT chain: trace a packet through PREROUTING → FORWARD → POSTROUTING for the k3s pod network
- Connection tracking: `conntrack -L` shows active flows
- Logging: log dropped packets, test with `nc` from outside

📋 **EVIDENCE CHECKPOINT:**
- [ ] firewall-cmd output (before + after a rule add) → `evidence/admin/p2/command-outputs/p2-firewalld.txt`
- [ ] iptables -L -n -v → `evidence/admin/p2/command-outputs/p2-iptables.txt`
- [ ] conntrack snapshot → `evidence/admin/p2/command-outputs/p2-conntrack.txt`

### 2. LVM hands-on (45 min)

**Activities:**
- Create PV, VG, LV; format as ext4; mount
- Extend an LV online; resize2fs
- Snapshot an LV, mount the snapshot, browse for "consistent backup" demo
- Understand: LV → device-mapper → block layer

📋 **EVIDENCE CHECKPOINT:**
- [ ] pvs / vgs / lvs output before + after operations → `evidence/admin/p2/command-outputs/p2-lvm.txt`
- [ ] `df -h` before + after extension → `evidence/admin/p2/command-outputs/p2-lvm-df.txt`

### 3. Network namespaces (30-45 min)

**Activities:**
- Create a named namespace: `ip netns add demo`
- Attach a veth pair between host and namespace
- Assign IPs, set routes
- Verify isolation: `ping` from host vs from inside namespace
- Tie back to containers: this is what Docker / containerd do under the hood

📋 **EVIDENCE CHECKPOINT:**
- [ ] netns setup commands transcript → `evidence/admin/p2/command-outputs/p2-netns-setup.txt`
- [ ] ip link / ip addr inside vs outside → `evidence/admin/p2/command-outputs/p2-netns-isolation.txt`

### 4. sysctl tuning (45 min)

**Activities:**
- Survey current sysctl: `sysctl -a | grep <category>`
- Key categories to tune for ADB-style workload:
  - `net.core.somaxconn` (listen backlog)
  - `net.ipv4.tcp_max_syn_backlog`
  - `net.ipv4.ip_local_port_range`
  - `net.ipv4.tcp_tw_reuse`
  - `fs.file-max`
  - `vm.swappiness` (low for DB workloads)
- Persist in `/etc/sysctl.d/99-fedplatform.conf`
- `sysctl -p` to apply; verify

📋 **EVIDENCE CHECKPOINT:**
- [ ] Your tuning file → `evidence/admin/p2/configs/sysctl-tuning.conf`
- [ ] sysctl values before / after → `evidence/admin/p2/command-outputs/p2-sysctl-diff.txt`
- [ ] Annotation on why each value was chosen → `evidence/admin/p2/admin-day-notes.md` (Section 4)

### 5. k3s node OS-level troubleshooting (60 min)

**Activities:**
- `journalctl -u k3s -n 200` — what does a healthy k3s startup look like? What does a failure look like?
- Containerd: `crictl ps`, `crictl logs <container-id>` — debug a pod without kubectl
- Kubelet cert: `openssl x509 -noout -dates -in /var/lib/rancher/k3s/agent/client-kubelet.crt`
- Disk pressure: fill disk to 90%, observe pod eviction, recover
- Network mode: Flannel vs Calico vs none — k3s defaults explained

📋 **EVIDENCE CHECKPOINT:**
- [ ] crictl ps output → `evidence/admin/p2/command-outputs/p2-crictl-ps.txt`
- [ ] k3s startup journal annotated → `evidence/admin/p2/command-outputs/p2-k3s-startup.txt`
- [ ] Disk pressure recovery trace → `evidence/admin/p2/command-outputs/p2-k3s-disk-pressure.txt`

### 6. Certificate stores (30 min)

**Activities:**
- System trust anchors: `/etc/pki/ca-trust/source/anchors/`
- Add a custom CA: copy PEM, run `update-ca-trust`, verify Java/Python/curl all trust it
- Inspect a cert chain: `openssl s_client -connect <host>:443 -showcerts`
- Cert pinning awareness: how cert-manager + Let's Encrypt rotates

📋 **EVIDENCE CHECKPOINT:**
- [ ] update-ca-trust before/after → `evidence/admin/p2/command-outputs/p2-ca-trust.txt`
- [ ] Cert chain dump for a service → `evidence/admin/p2/command-outputs/p2-cert-chain.txt`

### 7. Wrap-up reflection (15 min)

Fill in `evidence/admin/p2/admin-day-notes.md` Key Takeaways section.

---

## Why this day matters

The networking + storage layer is where most "production weirdness" lives. Junior engineers stop at "I set up the k3s cluster"; senior engineers can debug why a pod can't reach an external service or why disk usage looks normal in `df` but pods are getting evicted.
