# Federal Cloud Engineer Lab — Linux Admin Deep Dive
## Days 6-7: Oracle Linux Mastery for Federal Environments

**Goal:** Build deep Linux administration skills that directly map to federal cloud engineer daily work. Every section includes intentional break-fix exercises and interview talking points.
**Prerequisite:** Phase 1 Days 1-5 complete (FedTracker app deployed, basic hardening done)
**Environment:** Same Phase 1 Oracle Linux 9 VM (or rebuild via Terraform if torn down)
**Total Cost:** $0.00 (OCI Always Free tier)

---

## WHAT YOU'RE BUILDING

These two days transform you from "I can use Linux" to "I can administer, troubleshoot, and harden Linux in a federal environment." Every section maps directly to skills a federal hiring manager will probe.

| Topic | What You'll Do | Interview Question It Answers |
|-------|---------------|------------------------------|
| SELinux | Write custom policies, troubleshoot denials, audit2allow | "Is SELinux enforcing? How do you handle denials?" |
| LVM | Create, extend, resize, snapshot volumes | "The app needs more disk space — walk me through it" |
| Systemd | Write units from scratch, journal forensics, cgroups | "How would you investigate why a service crashed at 3am?" |
| Networking | tcpdump, ss, firewalld zones, DNS debugging | "Users report the app is slow — how do you diagnose?" |
| Kernel Tuning | sysctl, iostat, sar, OOM investigation | "The server ran out of memory — what happened?" |
| User/Group/PAM | LDAP-style management, sudoers, PAM modules | "How do you manage access for 50 engineers?" |
| NFS & ACLs | Mount shared storage, POSIX ACLs | "Teams need shared file access with different permissions" |
| Patch Management | dnf security patches, Ksplice, OCI OS Management Hub | "Walk me through your patching process" |
| Troubleshooting Labs | 8 break-fix scenarios | "Tell me about a time you debugged a production issue" |

---

## DAY 6 — STORAGE, SECURITY CONTEXTS, AND SYSTEM INTERNALS

**Time:** 6-8 hours | **Difficulty:** Intermediate-Advanced

---

### STEP 1: SELinux Deep Dive (90 minutes)

**[VM TERMINAL]**

> **ELI5: What is SELinux?**
>
> Regular Linux permissions (rwx) say WHO can access a file. SELinux says WHAT PROGRAMS can access WHAT RESOURCES. Even if a process runs as root, SELinux can block it from reading files it shouldn't touch. Think of it as a second lock on every door — the key (user permissions) gets you in, but the security camera (SELinux) decides if you're allowed to be there.
>
> In federal environments, SELinux enforcing mode is **mandatory**. Disabling it (`setenforce 0`) is an automatic audit failure. The correct approach is always to write a custom policy, never to disable.

#### 1.1 Verify SELinux Status

```bash
# Check current SELinux status
getenforce
# Expected: Enforcing

# Detailed status
sestatus
# Look for:
#   SELinux status:                 enabled
#   Current mode:                   enforcing
#   Policy from config file:        targeted

# See what policy modules are loaded
semodule -l | head -20

# Count total modules
semodule -l | wc -l
```

> **Interview Insight: "What's the difference between targeted and strict policy?"**
>
> **Strong answer:** "Targeted policy confines specific services (httpd, sshd, etc.) while leaving unconfined processes unrestricted. Strict policy confines everything. Oracle Linux and RHEL use targeted by default because strict breaks too many applications. In a federal environment, we use targeted and write custom policies for any application we deploy."
>
> **Weak answer:** "I usually set it to permissive to avoid issues." (Instant disqualification for a federal role)

#### 1.2 Understand SELinux Contexts

```bash
# Every file has a security context
ls -Z /opt/fedtracker/
# Example output: unconfined_u:object_r:usr_t:s0 main.py

# Every process has a security context
ps -eZ | grep uvicorn
# Example output: system_u:system_r:unconfined_service_t:s0

# The important fields:
# user:role:type:level
# The TYPE field is what matters most for policy decisions

# View your own context
id -Z

# View context of key system directories
ls -Zd /etc /var/log /tmp /home
```

#### 1.3 Create a Custom SELinux Policy for FedTracker

```bash
# Step 1: Check if SELinux is currently blocking FedTracker
sudo ausearch -m avc -ts today | grep fedtracker
# If no denials, FedTracker is running as unconfined — let's fix that

# Step 2: Create a dedicated SELinux type for the app
# First, put SELinux in permissive mode TEMPORARILY to collect denials
# (In production, you'd do this on a test system, never in prod)
sudo semanage permissive -a unconfined_service_t

# Step 3: Exercise the application to generate audit events
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/personnel
curl -X POST http://localhost:8000/api/v1/personnel \
  -H "Content-Type: application/json" \
  -d '{"name": "SELinux Test", "department": "Security", "clearance_level": "SECRET"}'

# Step 4: Generate a policy module from the denials
sudo ausearch -m avc -ts today | audit2allow -M fedtracker_policy

# Step 5: View what the policy allows (ALWAYS review before applying)
cat fedtracker_policy.te
# Look for: allow statements showing what was blocked

# Step 6: Install the policy module
sudo semodule -i fedtracker_policy.pp

# Step 7: Restore enforcing mode
sudo semanage permissive -d unconfined_service_t

# Step 8: Verify the module is loaded
semodule -l | grep fedtracker

# Step 9: Verify the app still works
curl http://localhost:8000/health
```

#### 1.4 SELinux File Contexts (labeling)

```bash
# Set custom context for the FedTracker directory
sudo semanage fcontext -a -t httpd_sys_content_t "/opt/fedtracker(/.*)?"
sudo restorecon -Rv /opt/fedtracker/

# Verify the new context
ls -Z /opt/fedtracker/

# If you need the app to write to a directory:
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/opt/fedtracker/data(/.*)?"
sudo mkdir -p /opt/fedtracker/data
sudo restorecon -Rv /opt/fedtracker/data/
ls -Z /opt/fedtracker/data/
```

#### 1.5 SELinux Booleans

```bash
# List all booleans (these are pre-defined policy switches)
getsebool -a | wc -l

# Check booleans relevant to web services
getsebool -a | grep httpd

# Enable the app to make network connections (if needed for DB)
sudo setsebool -P httpd_can_network_connect on

# Enable the app to connect to databases
sudo setsebool -P httpd_can_network_connect_db on

# The -P flag makes it persistent across reboots (without -P, lost on reboot)
```

#### 1.6 Break-Fix: SELinux Denial Investigation

```bash
# BREAK IT: Move the app to a location with wrong context
sudo cp -a /opt/fedtracker /srv/fedtracker-moved
# Note: -a preserves the original context, but /srv has a different default

# Update the systemd unit to point to new location
sudo sed -i 's|/opt/fedtracker|/srv/fedtracker-moved|g' /etc/systemd/system/fedtracker.service
sudo systemctl daemon-reload
sudo systemctl restart fedtracker

# The app may fail or behave strangely. Diagnose:
sudo systemctl status fedtracker
sudo journalctl -u fedtracker --no-pager -n 20
sudo ausearch -m avc -ts recent

# FIX IT: Apply correct context to new location
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/fedtracker-moved(/.*)?"
sudo restorecon -Rv /srv/fedtracker-moved/
sudo systemctl restart fedtracker
curl http://localhost:8000/health

# CLEAN UP: Move back to original location
sudo sed -i 's|/srv/fedtracker-moved|/opt/fedtracker|g' /etc/systemd/system/fedtracker.service
sudo systemctl daemon-reload
sudo systemctl restart fedtracker
```

> **Interview Insight: "How do you handle SELinux denials?"**
>
> **Strong answer:** "I check `ausearch -m avc -ts recent` to see what's being denied. I NEVER disable SELinux — instead I use `audit2allow` to generate a targeted policy module that allows only what's needed. I review the `.te` file before installing to make sure it's not overly permissive. Then I install with `semodule -i` and verify the app works."
>
> **Weak answer:** "I set it to permissive." (Red flag in federal context)

---

### STEP 2: LVM — Logical Volume Management (90 minutes)

**[VM TERMINAL]**

> **ELI5: What is LVM?**
>
> Think of LVM as a flexible layer between your physical disks and your filesystems. Without LVM, if your /var partition fills up, you're stuck — you'd need to add a disk and move data. With LVM, you can grow /var on the fly by adding more physical space to a "pool" and extending the filesystem. It's like having a stretchy closet that can grow when you need more room.
>
> **Why it matters for federal environments:** Servers grow over time. Audit logs accumulate. Databases expand. LVM lets you handle this without downtime. Every RHEL/Oracle Linux admin needs to know LVM cold.

#### 2.1 Understand the LVM Stack

```bash
# The three layers of LVM:
# Physical Volumes (PVs) → Volume Groups (VGs) → Logical Volumes (LVs)
#
# Think of it as:
# PV = individual bricks
# VG = a wall made of bricks
# LV = rooms carved out of the wall

# Check current LVM setup
sudo pvs      # Physical volumes
sudo vgs      # Volume groups
sudo lvs      # Logical volumes
sudo lsblk    # Block device overview (shows the whole picture)
```

#### 2.2 Create a Practice LVM Setup

```bash
# Create a 5GB block volume in OCI (via CLI or console)
# If using OCI CLI:
oci bv volume create \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain $(oci iam availability-domain list --query 'data[0].name' --raw-output) \
  --display-name "lvm-practice" \
  --size-in-gbs 5

# Attach the volume to your VM (paravirtualized attachment)
oci compute volume-attachment attach \
  --instance-id $INSTANCE_ID \
  --volume-id $VOLUME_OCID \
  --type paravirtualized

# Wait for attachment, then find the new device
sudo lsblk
# Look for a new device (likely /dev/sdb or /dev/vdb)
# On OCI ARM instances, it's usually /dev/sdb

# Set a variable for convenience (adjust to your actual device)
NEWDISK=/dev/sdb
```

#### 2.3 Build LVM from Scratch

```bash
# Step 1: Create a Physical Volume
sudo pvcreate $NEWDISK
sudo pvs
# Shows the new PV with no VG assigned

# Step 2: Create a Volume Group
sudo vgcreate vg_appdata $NEWDISK
sudo vgs
# Shows vg_appdata with the full 5GB available

# Step 3: Create Logical Volumes
# Create a 2GB LV for application data
sudo lvcreate -L 2G -n lv_appdata vg_appdata
# Create a 1GB LV for logs
sudo lvcreate -L 1G -n lv_logs vg_appdata
# Leave 2GB free in the VG for future growth

sudo lvs
# Shows both LVs

# Step 4: Create filesystems
sudo mkfs.xfs /dev/vg_appdata/lv_appdata
sudo mkfs.xfs /dev/vg_appdata/lv_logs

# Step 5: Mount them
sudo mkdir -p /data/appdata /data/logs
sudo mount /dev/vg_appdata/lv_appdata /data/appdata
sudo mount /dev/vg_appdata/lv_logs /data/logs

# Step 6: Make persistent (add to fstab)
echo '/dev/vg_appdata/lv_appdata /data/appdata xfs defaults 0 0' | sudo tee -a /etc/fstab
echo '/dev/vg_appdata/lv_logs /data/logs xfs defaults 0 0' | sudo tee -a /etc/fstab

# Step 7: Verify
df -h /data/appdata /data/logs
mount | grep vg_appdata
```

#### 2.4 Extend a Logical Volume (Most Common Task)

```bash
# Scenario: /data/logs is running low on space. Extend it.

# Check available space in the VG
sudo vgs
# Look at VFree column — should show ~2GB free

# Extend the LV by 1GB
sudo lvextend -L +1G /dev/vg_appdata/lv_logs

# CRITICAL: Extend the filesystem too (the LV is bigger but the FS doesn't know yet)
# For XFS:
sudo xfs_growfs /data/logs
# For ext4, you'd use: sudo resize2fs /dev/vg_appdata/lv_logs

# Verify
df -h /data/logs
# Should now show ~2GB instead of ~1GB
```

> **Interview Insight: "The audit log partition is 90% full. What do you do?"**
>
> **Strong answer:** "First, I check `df -h` and `lvs` to understand the current layout. If there's free space in the volume group, I extend the LV with `lvextend -L +XG` and grow the filesystem with `xfs_growfs` or `resize2fs`. If the VG is full, I either add a new physical disk with `pvcreate` and `vgextend`, or I investigate why the partition filled up — maybe audit logs need rotation with `logrotate`. All of this can be done online without unmounting."
>
> **Weak answer:** "I'd delete old files to free up space." (Deleting audit logs is a compliance violation)

#### 2.5 LVM Snapshots (Point-in-Time Backup)

```bash
# Create a snapshot of lv_appdata (useful before risky changes)
sudo lvcreate -L 500M -s -n snap_appdata /dev/vg_appdata/lv_appdata

# The snapshot captures the state at this moment
sudo lvs
# Shows snap_appdata as a snapshot of lv_appdata

# Make some changes to the original
echo "data added after snapshot" | sudo tee /data/appdata/post_snapshot.txt

# Mount the snapshot to verify it has the OLD data
sudo mkdir -p /mnt/snapshot
sudo mount -o ro /dev/vg_appdata/snap_appdata /mnt/snapshot
ls /mnt/snapshot/
# Should NOT contain post_snapshot.txt

# Clean up
sudo umount /mnt/snapshot
sudo lvremove -f /dev/vg_appdata/snap_appdata
```

#### 2.6 Break-Fix: LVM Troubleshooting

```bash
# EXERCISE 1: "The disk is full but df says there's space"
# Cause: Deleted files held open by a process
sudo dd if=/dev/zero of=/data/logs/bigfile bs=1M count=800
# Now "delete" it while something has it open
tail -f /data/logs/bigfile &
TAILPID=$!
sudo rm /data/logs/bigfile
df -h /data/logs
# Space NOT freed! The file is "deleted" but tail still has it open

# DIAGNOSE:
sudo lsof +L1 /data/logs
# Shows deleted files still held open

# FIX:
kill $TAILPID
df -h /data/logs
# Space is now freed

# EXERCISE 2: "Extend the VG with a new disk"
# (If you have another OCI block volume)
# sudo pvcreate /dev/sdc
# sudo vgextend vg_appdata /dev/sdc
# sudo vgs  # Now shows more total space
```

---

### STEP 3: Systemd Mastery (90 minutes)

**[VM TERMINAL]**

> **ELI5: What is systemd?**
>
> systemd is the "manager of managers" on modern Linux. It starts services, manages dependencies between them, handles logging, controls resource limits, and schedules tasks. Every process on the system traces back to systemd (PID 1). Knowing systemd deeply is like knowing how the engine works, not just how to drive.

#### 3.1 Write a Service Unit from Scratch

```bash
# Instead of copying a template, write one understanding every line
sudo tee /etc/systemd/system/fedtracker-worker.service << 'EOF'
[Unit]
# Human-readable description
Description=FedTracker Background Worker
# Start after network AND database are available
After=network-online.target
Wants=network-online.target
# If the main app fails, this worker should stop too
BindsTo=fedtracker.service

[Service]
# Type=simple: systemd considers the service started as soon as ExecStart runs
# Type=forking: for daemons that fork (like traditional Apache)
# Type=notify: service signals systemd when it's ready (most robust)
Type=simple

# Security: run as a dedicated user, not root
User=fedtracker
Group=fedtracker

# Working directory
WorkingDirectory=/opt/fedtracker

# The actual command to run
ExecStart=/usr/bin/python3 -m celery worker --app=tasks --loglevel=info

# Restart policy: always restart on failure, wait 5 seconds
Restart=on-failure
RestartSec=5
# Give up after 5 consecutive failures within 30 seconds
StartLimitIntervalSec=30
StartLimitBurst=5

# Resource limits via cgroups
# Limit memory to 512MB (OOM-killed if exceeded)
MemoryMax=512M
# Limit CPU to 50% of one core
CPUQuota=50%
# Limit number of open files
LimitNOFILE=4096

# Security hardening directives
# Prevent the service from gaining new privileges
NoNewPrivileges=yes
# Read-only filesystem except specified paths
ProtectSystem=strict
ReadWritePaths=/opt/fedtracker/data /var/log/fedtracker
# Private /tmp (isolated from other services)
PrivateTmp=yes
# Cannot modify kernel parameters
ProtectKernelTunables=yes
# Cannot load kernel modules
ProtectKernelModules=yes

# Environment (use EnvironmentFile for secrets)
EnvironmentFile=/etc/fedtracker/env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fedtracker-worker

[Install]
# Start on multi-user runlevel (standard for servers)
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
```

> **Interview Insight: "Walk me through a systemd service file you wrote"**
>
> **Strong answer:** Point to specific directives — "I used `MemoryMax` to prevent OOM impact on other services, `NoNewPrivileges` and `ProtectSystem=strict` for security hardening, `BindsTo` to create a dependency chain, and `EnvironmentFile` to keep secrets out of the unit file. The restart policy uses `StartLimitBurst` to prevent infinite restart loops."
>
> **Weak answer:** "I used the `[Service]` section with `ExecStart`." (Shows no depth beyond basics)

#### 3.2 Journal Forensics (the art of `journalctl`)

```bash
# Basic: View logs for a service
journalctl -u fedtracker --no-pager -n 50

# Filter by time range (last 30 minutes)
journalctl -u fedtracker --since "30 min ago"

# Filter by time range (specific window)
journalctl -u fedtracker --since "2026-03-21 14:00" --until "2026-03-21 15:00"

# Show only errors and above
journalctl -u fedtracker -p err

# Priority levels: emerg(0) alert(1) crit(2) err(3) warning(4) notice(5) info(6) debug(7)
# Show warnings and above
journalctl -u fedtracker -p warning

# Follow logs in real-time (like tail -f but better)
journalctl -u fedtracker -f

# Show kernel messages (like dmesg but persistent)
journalctl -k

# Show logs from a specific boot
journalctl --list-boots       # List boots
journalctl -b -1              # Previous boot (useful after a crash)

# JSON output for parsing
journalctl -u fedtracker -o json-pretty -n 5

# Disk usage of journal
journalctl --disk-usage

# Vacuum old logs (keep only 500MB)
sudo journalctl --vacuum-size=500M
# Or keep only last 7 days
sudo journalctl --vacuum-time=7d

# CRITICAL SKILL: Correlate service crash with system events
# "Why did the service crash at 3am?"
journalctl --since "03:00" --until "03:30" -p err
# Then check for OOM:
journalctl -k --since "03:00" | grep -i "out of memory\|oom"
# Check for disk space issues:
journalctl --since "03:00" | grep -i "no space\|disk full\|ENOSPC"
```

#### 3.3 Cgroup Resource Limits

```bash
# View resource usage of a service
systemctl status fedtracker
# Shows Memory and CPU lines

# Detailed resource accounting
systemd-cgtop
# Interactive view of cgroup resource usage (like top for services)

# Check cgroup limits for a service
systemctl show fedtracker | grep -E "Memory|CPU|Tasks"

# Set a memory limit on the fly (without editing the unit file)
sudo systemctl set-property fedtracker MemoryMax=256M

# Verify it took effect
systemctl show fedtracker | grep MemoryMax

# Set a CPU limit
sudo systemctl set-property fedtracker CPUQuota=25%

# These runtime changes are saved in /etc/systemd/system/fedtracker.service.d/
ls /etc/systemd/system/fedtracker.service.d/
```

#### 3.4 Timer Units (systemd replacement for cron)

```bash
# Create a timer that runs a health check every 5 minutes
sudo tee /etc/systemd/system/fedtracker-healthcheck.timer << 'EOF'
[Unit]
Description=FedTracker Health Check Timer

[Timer]
# Run 1 minute after boot
OnBootSec=1min
# Then every 5 minutes
OnUnitActiveSec=5min
# Add random delay up to 30 seconds (prevents thundering herd)
RandomizedDelaySec=30
# Catch up on missed runs after system downtime
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Create the service the timer triggers
sudo tee /etc/systemd/system/fedtracker-healthcheck.service << 'EOF'
[Unit]
Description=FedTracker Health Check

[Service]
Type=oneshot
ExecStart=/opt/fedtracker/scripts/health_check.sh
User=fedtracker
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now fedtracker-healthcheck.timer

# Verify
systemctl list-timers | grep fedtracker
# Shows next run time, last run time, and whether it's active
```

#### 3.5 Break-Fix: Service Won't Start

```bash
# EXERCISE: Diagnose a service that won't start
# Break it intentionally with a bad ExecStart
sudo cp /etc/systemd/system/fedtracker.service /etc/systemd/system/fedtracker.service.bak

# Introduce a subtle error (wrong path)
sudo sed -i 's|ExecStart=.*|ExecStart=/usr/bin/python3 /opt/fedtracker/mian.py|' /etc/systemd/system/fedtracker.service
sudo systemctl daemon-reload
sudo systemctl restart fedtracker

# DIAGNOSE:
systemctl status fedtracker          # Shows "failed"
journalctl -u fedtracker -n 20      # Shows the error
systemctl show fedtracker | grep -E "ExecStart|Result|ActiveState"

# FIX:
sudo cp /etc/systemd/system/fedtracker.service.bak /etc/systemd/system/fedtracker.service
sudo systemctl daemon-reload
sudo systemctl restart fedtracker
systemctl status fedtracker
```

---

### STEP 4: User, Group, and PAM Management (60 minutes)

**[VM TERMINAL]**

#### 4.1 User and Group Administration

```bash
# Create a service account (no login shell, no home directory)
sudo useradd -r -s /sbin/nologin -M fedtracker

# Create team groups
sudo groupadd sre-team
sudo groupadd dev-team
sudo groupadd audit-team

# Create users with specific groups
sudo useradd -m -G sre-team,wheel -s /bin/bash sre-admin
sudo useradd -m -G dev-team -s /bin/bash dev-user
sudo useradd -m -G audit-team -s /bin/bash auditor

# Set password policies
sudo chage -M 90 -m 7 -W 14 sre-admin
# -M 90: max password age 90 days
# -m 7: min password age 7 days (prevent rapid reuse)
# -W 14: warn 14 days before expiration

# View password aging info
sudo chage -l sre-admin

# Lock/unlock accounts
sudo usermod -L dev-user     # Lock
sudo usermod -U dev-user     # Unlock

# View who's logged in
who
w
last | head -20
lastlog | head -20
```

#### 4.2 Sudoers Configuration

```bash
# NEVER edit /etc/sudoers directly — use visudo or drop-in files
# Create a drop-in file for the SRE team
sudo tee /etc/sudoers.d/sre-team << 'EOF'
# SRE team can restart services and view logs without password
%sre-team ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart fedtracker*, \
                               /usr/bin/systemctl status fedtracker*, \
                               /usr/bin/journalctl -u fedtracker*

# SRE team can run specific diagnostic commands
%sre-team ALL=(ALL) NOPASSWD: /usr/sbin/ss, \
                               /usr/sbin/tcpdump, \
                               /usr/bin/iostat, \
                               /usr/bin/sar

# Dev team can only deploy (no service management)
%dev-team ALL=(fedtracker) NOPASSWD: /opt/fedtracker/scripts/deploy.sh
EOF

# Validate the file (CRITICAL — broken sudoers locks you out)
sudo visudo -c -f /etc/sudoers.d/sre-team
# Must say "parsed OK"

# Set correct permissions (MUST be 0440)
sudo chmod 0440 /etc/sudoers.d/sre-team
```

> **Interview Insight: "How do you manage sudo access for different teams?"**
>
> **Strong answer:** "I use drop-in files in `/etc/sudoers.d/` so each team's permissions are isolated and version-controlled. I grant specific command access with NOPASSWD only for operational commands like service restarts, never for shells. I always validate with `visudo -c` before committing. In a federal environment, I'd tie this to an LDAP/AD group so onboarding/offboarding is automatic."

#### 4.3 PAM (Pluggable Authentication Modules)

```bash
# View PAM configuration for SSH
cat /etc/pam.d/sshd

# View PAM configuration for sudo
cat /etc/pam.d/sudo

# Add password complexity requirements
sudo tee /etc/security/pwquality.conf << 'EOF'
# Minimum password length
minlen = 14
# Require at least 1 digit
dcredit = -1
# Require at least 1 uppercase
ucredit = -1
# Require at least 1 lowercase
lcredit = -1
# Require at least 1 special character
ocredit = -1
# Reject passwords containing the username
usercheck = 1
# Minimum different characters from old password
difok = 8
# Reject dictionary words
dictcheck = 1
EOF

# Configure login attempt limits (lockout after 5 failures)
sudo tee /etc/security/faillock.conf << 'EOF'
# Lock account after 5 failed attempts
deny = 5
# Unlock after 15 minutes
unlock_time = 900
# Count failures within this window
fail_interval = 900
# Don't lock root (use separate controls)
even_deny_root = false
EOF

# Verify PAM is enforcing faillock
grep faillock /etc/pam.d/system-auth
# Should see pam_faillock.so lines
```

---

## DAY 7 — NETWORKING, PERFORMANCE, AND TROUBLESHOOTING SCENARIOS

**Time:** 6-8 hours | **Difficulty:** Advanced

---

### STEP 5: Network Troubleshooting (90 minutes)

**[VM TERMINAL]**

#### 5.1 Socket Analysis with `ss`

```bash
# ss is the modern replacement for netstat (faster, more info)

# Show all listening TCP sockets
ss -tlnp
# -t: TCP, -l: listening, -n: numeric (no DNS lookup), -p: show process

# Show all established connections
ss -tnp state established

# Show connections to a specific port
ss -tnp dst :8000

# Show socket statistics
ss -s

# Show connections with timer information (useful for debugging hangs)
ss -tnpo

# Count connections per state (useful for connection leak detection)
ss -tn | awk '{print $1}' | sort | uniq -c | sort -rn

# Find processes with many connections (connection leak?)
ss -tnp | awk '{print $NF}' | sort | uniq -c | sort -rn | head

# Monitor connection rate in real-time
watch -n 1 'ss -tn | wc -l'
```

#### 5.2 Packet Capture with `tcpdump`

```bash
# Capture packets on the main interface for port 8000
sudo tcpdump -i any port 8000 -n -c 20
# -i any: all interfaces
# -n: don't resolve hostnames
# -c 20: capture 20 packets then stop

# Capture and save to file for analysis
sudo tcpdump -i any port 8000 -w /tmp/fedtracker.pcap -c 100 &
TCPDUMP_PID=$!

# Generate some traffic
for i in {1..10}; do curl -s http://localhost:8000/health > /dev/null; done

# Stop capture
kill $TCPDUMP_PID

# Read the capture file
tcpdump -r /tmp/fedtracker.pcap -n | head -20

# Advanced: Show only SYN packets (new connections)
sudo tcpdump -i any 'tcp[tcpflags] & (tcp-syn) != 0' port 8000 -n -c 10

# Advanced: Show HTTP request headers
sudo tcpdump -i any port 8000 -A -s 0 -c 5 | grep -E "^(GET|POST|HTTP|Host|Content)"

# Clean up
rm /tmp/fedtracker.pcap
```

#### 5.3 Firewalld Advanced Configuration

```bash
# View current zone configuration
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --list-all

# Create a custom zone for the application
sudo firewall-cmd --permanent --new-zone=fedtracker
sudo firewall-cmd --permanent --zone=fedtracker --set-description="FedTracker application zone"

# Add specific rules to the zone
sudo firewall-cmd --permanent --zone=fedtracker --add-port=8000/tcp
sudo firewall-cmd --permanent --zone=fedtracker --add-source=10.0.0.0/16
# This allows port 8000 only from the VCN, not the internet

# Rich rules (more granular control)
# Allow specific IP to access SSH
sudo firewall-cmd --permanent --zone=public --add-rich-rule='
  rule family="ipv4" source address="YOUR_IP/32" service name="ssh" accept'

# Rate limit connections to prevent DDoS
sudo firewall-cmd --permanent --zone=public --add-rich-rule='
  rule family="ipv4" service name="ssh" accept limit value="5/m"'

# Log dropped packets (useful for troubleshooting)
sudo firewall-cmd --permanent --zone=public --add-rich-rule='
  rule family="ipv4" log prefix="DROPPED: " level="warning" limit value="5/m" drop'

# Reload to apply permanent rules
sudo firewall-cmd --reload

# Verify
sudo firewall-cmd --list-all --zone=fedtracker
sudo firewall-cmd --list-all --zone=public
```

#### 5.4 DNS Troubleshooting

```bash
# Check DNS resolution
dig fedtracker.example.com
nslookup fedtracker.example.com

# Check which DNS server is being used
cat /etc/resolv.conf
resolvectl status 2>/dev/null || nmcli dev show | grep DNS

# Test DNS resolution speed
time dig google.com

# Trace DNS resolution path
dig +trace google.com

# Check reverse DNS
dig -x $(curl -s ifconfig.me)

# Common DNS issues in cloud environments:
# 1. VCN DNS resolver not working
# 2. /etc/resolv.conf overwritten by DHCP
# 3. Search domain not set correctly

# Fix search domain for internal resolution
sudo nmcli connection modify "System eth0" ipv4.dns-search "vcn.oraclevcn.com"
sudo nmcli connection up "System eth0"
```

#### 5.5 Break-Fix: Network Connectivity

```bash
# EXERCISE 1: "The API is unreachable"
# Break: Add a firewall rule that blocks port 8000
sudo firewall-cmd --zone=public --remove-port=8000/tcp
# Now test:
curl http://localhost:8000/health  # This works (localhost bypasses firewall)
curl http://$(hostname -I | awk '{print $1}'):8000/health  # This fails

# DIAGNOSE:
sudo firewall-cmd --list-all
ss -tlnp | grep 8000  # Service IS listening
sudo tcpdump -i any port 8000 -n -c 5  # See SYN but no SYN-ACK

# FIX:
sudo firewall-cmd --zone=public --add-port=8000/tcp

# EXERCISE 2: "DNS resolution is slow"
# Break: Point to a bad DNS server
sudo nmcli connection modify "System eth0" ipv4.dns "192.0.2.1"  # Non-routable
sudo nmcli connection up "System eth0"
time dig google.com  # Takes 5+ seconds (timeout then fallback)

# FIX:
sudo nmcli connection modify "System eth0" ipv4.dns "169.254.169.254"  # OCI DNS
sudo nmcli connection up "System eth0"
time dig google.com  # Fast again
```

> **Interview Insight: "Users report the application is slow. How do you diagnose?"**
>
> **Strong answer:** "I start with `ss -tnp` to check connection states — a high number of TIME_WAIT or CLOSE_WAIT indicates connection management issues. Then `tcpdump` on the app port to check latency between SYN and SYN-ACK. I check `journalctl` for app errors, `iostat` for disk bottlenecks, `sar` for CPU/memory trends, and `ss -s` for socket statistics. I also verify DNS with `dig` since slow resolution adds latency to every request."
>
> **Weak answer:** "I'd check if the server is up and restart the service."

---

### STEP 6: Kernel Tuning and Performance Analysis (90 minutes)

**[VM TERMINAL]**

#### 6.1 The /proc Filesystem

```bash
# /proc is a virtual filesystem — files here represent live kernel data

# System information
cat /proc/cpuinfo | head -20
cat /proc/meminfo | head -20
cat /proc/version

# Process information (PID of FedTracker)
FEDPID=$(pgrep -f uvicorn | head -1)
ls /proc/$FEDPID/
cat /proc/$FEDPID/status          # Process status
cat /proc/$FEDPID/cmdline | tr '\0' ' '  # How it was started
ls -la /proc/$FEDPID/fd | wc -l   # Number of open file descriptors
cat /proc/$FEDPID/limits           # Resource limits
cat /proc/$FEDPID/cgroup           # Cgroup membership

# System-wide stats
cat /proc/loadavg       # Load average
cat /proc/uptime         # Uptime in seconds
cat /proc/stat | head -5 # CPU statistics
```

#### 6.2 Performance Monitoring Tools

```bash
# iostat — Disk I/O statistics
# Install if needed: sudo dnf install -y sysstat
iostat -xz 1 5
# Key columns:
# %util: How busy the disk is (>80% is concerning)
# await: Average wait time in ms (>20ms is slow for SSD)
# r/s, w/s: Reads/writes per second

# vmstat — Virtual memory statistics
vmstat 1 10
# Key columns:
# r: processes waiting for CPU (>2x cores is bad)
# si/so: swap in/out (any swap activity is concerning)
# us/sy/wa: user/system/wait CPU (high wa = I/O bottleneck)

# sar — System Activity Reporter (historical data)
# Enable data collection
sudo systemctl enable --now sysstat

# View CPU history
sar -u 1 5          # Real-time CPU
sar -u -f /var/log/sa/sa$(date +%d)  # Today's history

# View memory history
sar -r 1 5          # Real-time memory

# View network history
sar -n DEV 1 5      # Network interface stats

# View disk history
sar -d 1 5          # Disk activity

# top/htop for interactive monitoring
top -bn1 | head -20  # Batch mode, one iteration
```

#### 6.3 sysctl Kernel Parameters

```bash
# View all current kernel parameters
sysctl -a 2>/dev/null | wc -l  # Hundreds of parameters

# Key parameters for a web server

# Network performance tuning
cat << 'EOF' | sudo tee /etc/sysctl.d/99-fedtracker.conf
# === Network Performance ===
# Increase max connections in backlog queue
net.core.somaxconn = 4096
# Increase network buffer sizes
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
# TCP keepalive (detect dead connections faster)
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 5
# Reuse TIME_WAIT sockets (useful for high-traffic servers)
net.ipv4.tcp_tw_reuse = 1
# Increase local port range
net.ipv4.ip_local_port_range = 1024 65535
# Enable SYN flood protection
net.ipv4.tcp_syncookies = 1
# Increase SYN backlog
net.ipv4.tcp_max_syn_backlog = 8192

# === Memory Management ===
# Reduce swappiness (prefer to keep app in RAM)
vm.swappiness = 10
# Percentage of memory at which background writeback starts
vm.dirty_ratio = 20
vm.dirty_background_ratio = 5

# === File Descriptors ===
# Increase system-wide file descriptor limit
fs.file-max = 1048576

# === Security ===
# Disable IP forwarding (not a router)
net.ipv4.ip_forward = 0
# Ignore ICMP redirects (prevent MITM)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
# Log martian packets (packets with impossible source addresses)
net.ipv4.conf.all.log_martians = 1
EOF

# Apply without reboot
sudo sysctl --system

# Verify specific parameters
sysctl net.core.somaxconn
sysctl vm.swappiness
```

> **Interview Insight: "How do you tune a Linux server for a web application?"**
>
> **Strong answer:** "I focus on three areas: network (increase `somaxconn` and buffer sizes for connection handling, enable `tcp_tw_reuse` for high-traffic scenarios), memory (`swappiness=10` to keep the app in RAM, tune dirty ratios for write performance), and security (`tcp_syncookies` for SYN flood protection, disable IP forwarding, log martians). I put tuning in `/etc/sysctl.d/` drop-in files so they're persistent, version-controlled, and can be managed by Ansible."

#### 6.4 OOM Killer Investigation

```bash
# The OOM (Out of Memory) killer is Linux's last resort when memory is exhausted
# It picks a process and kills it to free memory. Understanding it is critical.

# Check if OOM killer has run
sudo dmesg | grep -i "out of memory"
journalctl -k | grep -i "oom"

# View OOM score for each process (higher = more likely to be killed)
for pid in $(ps -eo pid --no-header); do
  if [ -f /proc/$pid/oom_score ]; then
    echo "PID: $pid Score: $(cat /proc/$pid/oom_score) Cmd: $(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ' | head -c 60)"
  fi
done 2>/dev/null | sort -t: -k3 -rn | head -20

# Protect critical services from OOM killer
# Set OOM score adjustment (-1000 = never kill, +1000 = kill first)
echo -500 | sudo tee /proc/$(pgrep -f uvicorn | head -1)/oom_score_adj
# Make it permanent in the systemd unit:
# Add OOMScoreAdjust=-500 to [Service] section

# EXERCISE: Simulate OOM (carefully!)
# Create a memory pressure scenario to see OOM in action
# WARNING: This WILL kill processes on a small VM
# Only run this on your lab VM, never in production

# Check current memory
free -h

# Create a process that slowly eats memory
python3 -c "
import time
data = []
try:
    while True:
        data.append('x' * (1024 * 1024))  # 1MB per iteration
        print(f'Allocated: {len(data)} MB')
        time.sleep(0.1)
except MemoryError:
    print('MemoryError caught')
" &
MEMPID=$!

# Watch in another terminal:
# watch -n 1 'free -h; echo "---"; dmesg | tail -5'

# After OOM kills it, investigate:
sleep 30
kill $MEMPID 2>/dev/null
sudo dmesg | tail -20
journalctl -k --since "1 min ago" | grep -i oom
```

> **Interview Insight: "A service was killed by the OOM killer at 3am. What happened and how do you prevent it?"**
>
> **Strong answer:** "I check `dmesg` and `journalctl -k` for OOM messages to identify which process was killed and what consumed the memory. I use `sar -r` to review memory trends leading up to the event. For prevention: I set `MemoryMax` in the systemd unit to cap the service's memory, set `OOMScoreAdjust=-500` to protect critical services, tune `vm.swappiness`, and set up monitoring alerts at 80% memory threshold so we catch it before OOM kicks in. I also investigate whether the killed process has a memory leak using `valgrind` or process metrics over time."

---

### STEP 7: NFS and File ACLs (45 minutes)

**[VM TERMINAL]**

#### 7.1 NFS Setup (Simulated Shared Storage)

```bash
# Install NFS server and client
sudo dnf install -y nfs-utils

# Create a shared directory
sudo mkdir -p /exports/shared-evidence
sudo chown nobody:nobody /exports/shared-evidence
sudo chmod 755 /exports/shared-evidence

# Configure NFS exports
sudo tee /etc/exports << 'EOF'
# Share evidence directory with the VCN subnet
# ro = read-only, sync = write to disk before confirming, root_squash = map remote root to nobody
/exports/shared-evidence 10.0.0.0/16(ro,sync,root_squash,no_subtree_check)
# For read-write access (e.g., app server writing evidence):
# /exports/shared-evidence 10.0.2.0/24(rw,sync,root_squash,no_subtree_check)
EOF

# Start NFS
sudo systemctl enable --now nfs-server
sudo exportfs -v

# Configure firewall for NFS
sudo firewall-cmd --permanent --add-service=nfs
sudo firewall-cmd --permanent --add-service=rpc-bind
sudo firewall-cmd --permanent --add-service=mountd
sudo firewall-cmd --reload

# Mount locally to test (simulating a client)
sudo mkdir -p /mnt/evidence
sudo mount -t nfs localhost:/exports/shared-evidence /mnt/evidence
df -h /mnt/evidence

# Persistent mount via fstab
echo 'localhost:/exports/shared-evidence /mnt/evidence nfs ro,soft,timeo=30 0 0' | sudo tee -a /etc/fstab

# Clean up
sudo umount /mnt/evidence
```

#### 7.2 POSIX ACLs (Fine-Grained Permissions)

```bash
# Standard Unix permissions: owner/group/other (rwx)
# ACLs: add permissions for specific users/groups beyond the three categories

# Install ACL tools (usually pre-installed)
sudo dnf install -y acl

# Check filesystem supports ACLs
mount | grep /data
# XFS and ext4 support ACLs by default

# Create a shared project directory
sudo mkdir -p /data/appdata/compliance-reports

# Set base permissions (owner=fedtracker, group=sre-team)
sudo chown fedtracker:sre-team /data/appdata/compliance-reports
sudo chmod 750 /data/appdata/compliance-reports

# Add ACL: audit-team gets read-only access
sudo setfacl -m g:audit-team:rx /data/appdata/compliance-reports

# Add ACL: specific user gets read-write
sudo setfacl -m u:sre-admin:rwx /data/appdata/compliance-reports

# Set default ACLs (inherited by new files created in this directory)
sudo setfacl -d -m g:audit-team:rx /data/appdata/compliance-reports
sudo setfacl -d -m g:sre-team:rwx /data/appdata/compliance-reports

# View ACLs
getfacl /data/appdata/compliance-reports

# The + in ls -l indicates ACLs are set
ls -la /data/appdata/

# Test: create a file as fedtracker and check inherited ACLs
sudo -u fedtracker touch /data/appdata/compliance-reports/test-report.txt
getfacl /data/appdata/compliance-reports/test-report.txt

# Remove an ACL entry
sudo setfacl -x u:sre-admin /data/appdata/compliance-reports

# Remove ALL ACLs
# sudo setfacl -b /data/appdata/compliance-reports
```

> **Interview Insight: "How do you handle file permissions when multiple teams need different access levels?"**
>
> **Strong answer:** "I use POSIX ACLs to grant granular access beyond basic owner/group/other. For example, the SRE team gets rwx, the audit team gets read-only, and developers get no access to compliance reports. I set default ACLs on directories so new files inherit the correct permissions. This is managed via Ansible to ensure consistency across servers."

---

### STEP 8: Comprehensive Troubleshooting Labs (90 minutes)

**[VM TERMINAL]**

These exercises simulate real scenarios you'll face in federal environments. Each follows the pattern: **symptom → diagnosis → root cause → fix → verification**.

#### Lab 1: "The Application is Returning 502 Errors"

```bash
# SETUP: Break the app
sudo systemctl stop fedtracker
# But leave the reverse proxy / security list open
# (In production, a load balancer would return 502 when backend is down)

# SYMPTOM: curl returns "Connection refused" on port 8000

# DIAGNOSIS STEPS:
# 1. Is the process running?
systemctl status fedtracker
pgrep -f uvicorn

# 2. Is anything listening on port 8000?
ss -tlnp | grep 8000

# 3. Check logs for why it stopped
journalctl -u fedtracker --since "5 min ago" -p err

# FIX:
sudo systemctl start fedtracker
curl http://localhost:8000/health
```

#### Lab 2: "Disk Space Alert — Root Filesystem 95% Full"

```bash
# SETUP: Fill up space
sudo dd if=/dev/zero of=/var/log/fake-audit.log bs=1M count=500
# (Adjust count based on your disk size)

# SYMPTOM: df -h shows / at 95%+

# DIAGNOSIS STEPS:
# 1. Find the largest directories
sudo du -sh /* 2>/dev/null | sort -rh | head -10

# 2. Drill down into the largest
sudo du -sh /var/* 2>/dev/null | sort -rh | head -10
sudo du -sh /var/log/* 2>/dev/null | sort -rh | head -10

# 3. Find recently modified large files
sudo find /var/log -type f -size +100M -mtime -1 -exec ls -lh {} \;

# 4. Check for deleted files held open
sudo lsof +L1 | head -20

# 5. Check inode usage (can be full even with free disk space)
df -i

# FIX:
sudo rm /var/log/fake-audit.log
# Configure logrotate for real log management
sudo tee /etc/logrotate.d/fedtracker << 'EOF'
/var/log/fedtracker/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 fedtracker sre-team
    postrotate
        systemctl reload fedtracker 2>/dev/null || true
    endscript
}
EOF

# Test logrotate config
sudo logrotate -d /etc/logrotate.d/fedtracker
```

#### Lab 3: "SSH Connection Hangs"

```bash
# SETUP: Add a firewall rule that allows SYN but drops established
sudo firewall-cmd --direct --add-rule ipv4 filter INPUT 0 \
  -p tcp --dport 22 -m state --state ESTABLISHED -j DROP

# SYMPTOM: New SSH connections start but hang after authentication

# DIAGNOSIS (from another session or OCI console serial connection):
# 1. Check firewall rules
sudo firewall-cmd --direct --get-all-rules

# 2. Check for the broken rule
sudo iptables -L INPUT -v -n | grep -i drop

# FIX:
sudo firewall-cmd --direct --remove-rule ipv4 filter INPUT 0 \
  -p tcp --dport 22 -m state --state ESTABLISHED -j DROP
```

#### Lab 4: "Application Memory Leak"

```bash
# SETUP: Start a script that slowly leaks memory
python3 -c "
import time, os
data = []
while True:
    data.append('x' * (1024 * 1024))  # 1MB per iteration
    print(f'PID {os.getpid()}: {len(data)} MB allocated')
    time.sleep(2)
" &
LEAKPID=$!

# SYMPTOM: Memory usage climbing steadily

# DIAGNOSIS:
# 1. Watch memory in real-time
watch -n 2 "free -h; echo '---'; ps aux --sort=-%mem | head -5"

# 2. Track specific process memory over time
while true; do
  ps -o pid,rss,vsz,comm -p $LEAKPID
  sleep 5
done &
WATCHPID=$!

# 3. Check /proc for detailed memory info
cat /proc/$LEAKPID/status | grep -E "VmRSS|VmSize|VmPeak"

# FIX:
kill $LEAKPID
kill $WATCHPID
```

#### Lab 5: "Service Starts But Crashes After 30 Seconds"

```bash
# SETUP: Create a service with a bug
sudo tee /etc/systemd/system/crashtest.service << 'EOF'
[Unit]
Description=Crash Test Service

[Service]
Type=simple
ExecStart=/bin/bash -c 'echo "Starting..."; sleep 5; exit 1'
Restart=on-failure
RestartSec=3
StartLimitIntervalSec=30
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start crashtest

# SYMPTOM: Service goes to "failed" status after a few restarts

# DIAGNOSIS:
systemctl status crashtest
# Shows "start-limit-hit"
journalctl -u crashtest --since "2 min ago"
# Shows the pattern: start → fail → restart → fail → restart → fail → STOP

# KEY LEARNING: StartLimitBurst prevents infinite restart loops
# After 3 failures within 30 seconds, systemd gives up

# FIX: Fix the underlying issue (exit code), then reset the failure counter
sudo systemctl reset-failed crashtest
# Edit ExecStart to fix the command, then start again

# CLEAN UP:
sudo systemctl stop crashtest
sudo rm /etc/systemd/system/crashtest.service
sudo systemctl daemon-reload
```

#### Lab 6: "SELinux is Blocking but I Don't Know What"

```bash
# SETUP: Create a Python script that writes to a protected location
sudo tee /opt/fedtracker/write_test.py << 'EOF'
#!/usr/bin/env python3
import os
with open('/etc/fedtracker/runtime_data.json', 'w') as f:
    f.write('{"status": "ok"}')
print("Write successful")
EOF
sudo chmod +x /opt/fedtracker/write_test.py
sudo mkdir -p /etc/fedtracker

# Run it as the fedtracker user (may be blocked by SELinux)
sudo -u fedtracker /opt/fedtracker/write_test.py

# DIAGNOSIS:
sudo ausearch -m avc -ts recent
# Look for: denied { write } ... for scontext=... tcontext=...

# Use sealert for human-readable analysis (if installed)
sudo dnf install -y setroubleshoot-server
sudo sealert -a /var/log/audit/audit.log | tail -40

# Generate a targeted fix
sudo ausearch -m avc -ts recent | audit2allow -R
# Shows which boolean or policy module would fix it

# FIX:
sudo ausearch -m avc -ts recent | audit2allow -M fedtracker_write
sudo semodule -i fedtracker_write.pp
sudo -u fedtracker /opt/fedtracker/write_test.py
```

#### Lab 7: "Process Using 100% CPU"

```bash
# SETUP: Create a CPU-bound process
yes > /dev/null &
YESPID=$!

# SYMPTOM: System feels sluggish, top shows high CPU

# DIAGNOSIS:
# 1. Find the culprit
top -bn1 | head -15
# or
ps aux --sort=-%cpu | head -5

# 2. What is this process doing? (strace)
sudo strace -p $YESPID -c -S time 2>&1 &
STRACEPID=$!
sleep 5
kill $STRACEPID
# Shows system call breakdown — reveals what the process is actually doing

# 3. Limit it with cgroups (without killing it)
sudo systemctl set-property user-$(id -u).slice CPUQuota=20%
# Or use cpulimit:
# sudo dnf install -y cpulimit
# sudo cpulimit -p $YESPID -l 10  # Limit to 10% CPU

# FIX:
kill $YESPID
```

#### Lab 8: "Inode Exhaustion"

```bash
# SETUP: Create millions of tiny files
mkdir -p /tmp/inode-test
for i in $(seq 1 50000); do touch /tmp/inode-test/file_$i; done

# SYMPTOM: "No space left on device" but df -h shows free space

# DIAGNOSIS:
df -h /tmp     # Shows space available
df -i /tmp     # Shows inode usage — may be near 100%!

# Find directories with the most files
sudo find /tmp -type d -exec sh -c 'echo "$(find "{}" -maxdepth 1 -type f | wc -l) {}"' \; 2>/dev/null | sort -rn | head -10

# FIX:
rm -rf /tmp/inode-test
df -i /tmp     # Inodes freed
```

---

### STEP 9: Enterprise Patch Management (90 minutes)

> **🧠 ELI5 — Patching:** Patching is how you fix security vulnerabilities and bugs in your operating system and installed software. Think of it like getting a recall notice for your car — the manufacturer found a problem and released a fix. In federal environments, patching is mandated by NIST SI-2 (Flaw Remediation): you must apply security patches within defined timelines (typically 30 days for critical, 90 days for high). Miss the deadline, that's an audit finding.
>
> But patching isn't just running `dnf update`. In enterprise, a security team identifies which patches to apply, tests them in a staging environment, then promotes them to production during a maintenance window. Tools like IBM BigFix, Red Hat Satellite, or OCI OS Management Hub orchestrate this workflow at scale.

#### 9.1 Manual Patching Fundamentals

**[VM TERMINAL]**

Every admin needs to understand what happens on the individual server, regardless of what orchestration tool pushes the patches.

```bash
# Check what updates are available (doesn't install anything)
sudo dnf check-update
# Shows: package name, new version, repository source
# If nothing shows, your system is fully up to date

# Check only security-related updates (federal standard — you patch security first)
sudo dnf updateinfo list security
# Shows: advisory ID (e.g., ELSA-2026-1234), severity, package name
# ELSA = Enterprise Linux Security Advisory (Oracle's equivalent of RHEL's RHSA)

# View details of a specific advisory
sudo dnf updateinfo info ELSA-2026-1234
# Shows: CVE IDs, severity, description, affected packages
```

> **Interview Insight: "Walk me through your patching process."**
>
> **Strong answer:** "I start by reviewing available security advisories with `dnf updateinfo list security`. I categorize by severity — critical patches get priority. Before applying, I verify the patch in a staging environment. On the target server, I apply security-only patches with `dnf update --security`, verify services are still running, then check if any services need restart with `needs-restarting`. I document the change in our change management system and validate with a post-patch scan."
>
> **Weak answer:** "I run `dnf update -y` and hope nothing breaks." (Shows no risk awareness or process discipline)

```bash
# Apply security patches only (not all updates — this is the federal-standard approach)
sudo dnf update --security -y
# Only installs packages with security advisories — skips bug fixes, enhancements

# After patching: check which services need to be restarted
sudo dnf install -y dnf-utils  # provides needs-restarting
sudo needs-restarting -s
# Lists services that are running old code and need restart
# Example output:
#   sshd.service
#   fedtracker.service

# Restart affected services (or reboot if kernel was patched)
sudo needs-restarting -r
# Exit code 0 = no reboot needed
# Exit code 1 = reboot required (kernel or core library patched)
```

> **Why `--security` instead of just `dnf update`?** In federal environments, change control is strict. Every change needs justification. Security patches have CVE numbers — you can point to the vulnerability they fix. General updates (new features, performance improvements) don't have that justification and introduce unnecessary risk. Patch what you must, leave everything else for planned maintenance windows.

```bash
# View patching history — the audit trail
dnf history
# Shows: transaction ID, date, action (install/update/remove), number of packages

# View details of a specific transaction
dnf history info 5
# Shows exactly which packages were changed and from which version to which

# ROLLBACK: Undo a bad patch
sudo dnf history undo 5 -y
# Reverts all packages changed in transaction 5 to their previous versions
# This is your emergency button when a patch breaks something
```

> **🧠 ELI5 — `dnf history undo`:** This is your "undo" button. Every `dnf` operation gets a transaction ID. If a patch breaks your app, you run `dnf history undo <ID>` to revert every package in that transaction to its previous version. It's like restoring from a save point in a video game.

<sub><em style="color: #999; font-size: 0.65em;">

💡🖥️ Commands used:

| Command | Flag(s) | What It Does |
|---------|---------|-------------|
| `dnf check-update` | | List available updates without installing |
| `dnf updateinfo list` | `security` | Show only security-related advisories |
| `dnf updateinfo info` | `<advisory>` | Show details of a specific security advisory |
| `dnf update` | `--security -y` | Install only security patches |
| `needs-restarting` | `-s` | List services that need restart after patching |
| `needs-restarting` | `-r` | Check if a full reboot is required |
| `dnf history` | | Show all package transaction history |
| `dnf history info` | `<ID>` | Show details of a specific transaction |
| `dnf history undo` | `<ID> -y` | Rollback all changes from a specific transaction |

</em></sub>

#### 9.2 Oracle Ksplice — Zero-Downtime Kernel Patching

> **🧠 ELI5 — Ksplice:** Normally, a kernel patch requires a reboot — the kernel is the core of the OS and can't be replaced while running. Ksplice is Oracle's technology that patches the kernel live, in memory, without rebooting. For servers that can't afford downtime (think: 24/7 compliance monitoring), this is critical. It's like changing the engine on a car while it's driving.

```bash
# Check if Ksplice is available (pre-installed on OCI Oracle Linux instances)
sudo ksplice --help 2>/dev/null && echo "Ksplice available" || echo "Ksplice not installed"

# If available, check current kernel patch status
sudo uptrack-show
# Shows: list of applied Ksplice patches (CVE fixes applied without reboot)

# Check for new Ksplice updates
sudo uptrack-upgrade -n
# -n = dry run (shows what would be applied without applying)

# Apply Ksplice patches (zero downtime)
sudo uptrack-upgrade -y
# Patches the running kernel in memory — no reboot needed
```

> **Federal Reality Check:** Some compliance frameworks (FedRAMP, DISA STIG) require that security patches be applied within specific timelines. Ksplice lets you meet those timelines without scheduling maintenance windows for reboots. In an interview, you can say: "Oracle Ksplice lets me apply critical kernel CVE fixes in minutes without downtime. For non-kernel patches, I use `dnf update --security` and restart only the affected services."

#### 9.3 OCI OS Management Hub — Enterprise Patch Pipeline

> **🧠 ELI5 — OS Management Hub:** If `dnf update` is you fixing one car in your garage, OS Management Hub is a fleet maintenance operation. It's OCI's native patch management service — the cloud-native equivalent of IBM BigFix or Red Hat Satellite. A security team creates a "patch bundle" (list of approved packages), then promotes it through stages: security-review → staging → production. Each stage's servers automatically receive the exact same packages that were tested. You manage the whole thing as Terraform code.

**Enable OS Management Hub on your VMs:**

📍 **OCI Console**

1. Navigate to **Compute** → **Instances** → select your bastion or p1-app-server
2. Click the **Oracle Cloud Agent** tab
3. Find **OS Management Hub** plugin → toggle it to **Enabled**
4. Wait 2-3 minutes for the agent to register

> ⚠️ **OS Management Hub requires an active OCI tenancy (trial credits work). It is not available on Always Free-only accounts.** If the plugin doesn't appear, your tenancy may not have access.

📍 **OCI Console** → **OS Management Hub**

5. Navigate to **Observability & Management** → **OS Management Hub** → **Managed Instances**
6. Verify your VM appears in the list with status "Online"
7. Click your instance → review **Installed Packages**, **Available Updates**, and **Applicable Errata**

> **What are Errata?** Errata are security advisories — each one maps to one or more CVE vulnerabilities. OS Management Hub tracks which errata apply to each of your instances, giving you a fleet-wide view of your security posture. This is what auditors want to see.

**Create a 3-stage lifecycle environment:**

This simulates the enterprise workflow: security team approves → staging validates → production receives.

📍 **OCI Console** → **OS Management Hub** → **Lifecycle Environments**

1. Click **Create Lifecycle Environment**
2. Fill in:
   - **Name:** `federal-patch-pipeline`
   - **Description:** 3-stage patch promotion for NIST SI-2 compliance
   - **OS Family:** Oracle Linux
   - **Architecture:** aarch64 (matches your A1 Flex VMs)
   - **Vendor:** Oracle
3. **Stages** — add 3 stages in order:
   - Stage 1: `security-review` (rank 1)
   - Stage 2: `staging` (rank 2)
   - Stage 3: `production` (rank 3)
4. Click **Create**

**Or via OCI CLI:**

```bash
# Create the lifecycle environment (run from your local machine with OCI CLI configured)
oci os-management-hub lifecycle-environment create \
  --compartment-id $COMPARTMENT_OCID \
  --display-name "federal-patch-pipeline" \
  --arch-type AARCH64 \
  --os-family ORACLE_LINUX \
  --vendor-name ORACLE \
  --stages '[
    {"displayName":"security-review","rank":1},
    {"displayName":"staging","rank":2},
    {"displayName":"production","rank":3}
  ]'
```

**Or via Terraform** (recommended — infrastructure as code):

```hcl
resource "oci_os_management_hub_lifecycle_environment" "patch_pipeline" {
  compartment_id = var.compartment_id
  display_name   = "federal-patch-pipeline"
  description    = "3-stage patch promotion for NIST SI-2 compliance"
  arch_type      = "AARCH64"
  os_family      = "ORACLE_LINUX"
  vendor_name    = "ORACLE"

  stages {
    display_name = "security-review"
    rank         = 1
  }
  stages {
    display_name = "staging"
    rank         = 2
  }
  stages {
    display_name = "production"
    rank         = 3
  }
}
```

**Simulate the enterprise patch workflow:**

```bash
# Step 1: Security team creates a versioned patch bundle
# This is an immutable, frozen snapshot of approved packages
oci os-management-hub software-source create-versioned-custom-swsrc \
  --compartment-id $COMPARTMENT_OCID \
  --display-name "Security-Patch-$(date +%Y-%m)" \
  --software-source-version "1.0" \
  --vendor-software-sources '[{"id":"<ol9-baseos-source-ocid>","displayName":"ol9_baseos_latest"}]'

# Step 2: Security analyst promotes to security-review stage
oci os-management-hub lifecycle-stage promote-software-source \
  --lifecycle-stage-id $SECURITY_REVIEW_STAGE_OCID \
  --software-source-id $VERSIONED_SOURCE_OCID

# Step 3: After review — ops admin promotes to staging
oci os-management-hub lifecycle-stage promote-software-source \
  --lifecycle-stage-id $STAGING_STAGE_OCID \
  --software-source-id $VERSIONED_SOURCE_OCID

# Step 4: After staging validation — promote to production
oci os-management-hub lifecycle-stage promote-software-source \
  --lifecycle-stage-id $PRODUCTION_STAGE_OCID \
  --software-source-id $VERSIONED_SOURCE_OCID

# Step 5: Verify compliance
oci os-management-hub managed-instance list-errata \
  --managed-instance-id $INSTANCE_OCID
```

> **Interview Insight: "How do you manage patching at scale?"**
>
> **Strong answer:** "I use OCI OS Management Hub to manage patching across our fleet. The security team creates versioned patch bundles — immutable snapshots of approved packages. We promote them through a 3-stage lifecycle: security-review, staging, production. Each stage's instances automatically receive the exact packages that were tested. The lifecycle environment is managed as Terraform code, and compliance is tracked through the OSMH errata dashboard. For critical kernel patches, we use Oracle Ksplice for zero-downtime application."
>
> **What this demonstrates:** You understand that patching isn't just `dnf update` — it's a controlled, auditable process with separation of duties (security team approves, ops team promotes, change management tracks).

#### 9.4 Break-Fix Lab: Patch and Rollback

```bash
# SCENARIO: You applied a security patch and FedTracker stopped working.
# Walk through diagnosis and rollback.

# Step 1: Apply available security patches
sudo dnf update --security -y
# Note the transaction ID from dnf history

# Step 2: Verify FedTracker is still running
systemctl status fedtracker
curl -s http://localhost:8000/health | python3 -m json.tool

# Step 3: Check if services need restart
sudo needs-restarting -s

# Step 4: If FedTracker needs restart, restart it
sudo systemctl restart fedtracker
systemctl status fedtracker

# BREAK IT: Simulate a bad patch (we'll use dnf history to rollback)
# Check your latest transaction ID
dnf history
# Note the ID number (e.g., 12)

# Step 5: Rollback the patch
sudo dnf history undo 12 -y

# Step 6: Verify rollback worked
dnf history
# Should show a new transaction undoing the previous one

# Step 7: Restart affected services
sudo systemctl restart fedtracker
curl -s http://localhost:8000/health | python3 -m json.tool
```

> **What you just practiced:** The complete patch-rollback cycle that every federal sysadmin needs: apply → verify → discover breakage → rollback → verify recovery. In a real incident, you'd also file a change management ticket explaining why the rollback was needed and work with the security team on an alternative remediation path.

---

### DAY 6-7 RECAP — LINUX ADMIN MASTERY

#### What You Can Now Talk About in Interviews

- "I manage SELinux in enforcing mode — I write custom policy modules with `audit2allow` and set file contexts with `semanage fcontext`. I never disable SELinux."
- "I use LVM for flexible storage management — I can extend volumes online, create snapshots for pre-change backups, and add new disks to existing volume groups without downtime."
- "I write systemd units from scratch with security hardening (`NoNewPrivileges`, `ProtectSystem=strict`, `MemoryMax`) and use cgroups to prevent resource contention."
- "I troubleshoot with a systematic approach: `ss` for connections, `tcpdump` for packets, `journalctl` for logs, `iostat`/`sar`/`vmstat` for performance, and `ausearch` for SELinux denials."
- "I tune kernel parameters via `sysctl` for web server workloads — `somaxconn`, TCP buffer sizes, `swappiness`, and security hardening like `tcp_syncookies`."
- "I've investigated OOM killer events by correlating `dmesg`, `journalctl -k`, and `sar -r` to find the memory trend leading to the kill, then prevented recurrence with `MemoryMax` in systemd and monitoring alerts."
- "I manage user access with POSIX ACLs for fine-grained permissions, `sudoers.d` drop-in files for team-specific sudo access, and PAM for password complexity and account lockout policies."
- "I manage patching with a staged approach: review security advisories, apply `--security` patches to staging first, verify services, then promote to production. I use OCI OS Management Hub for fleet-wide orchestration with 3-stage lifecycle environments, and Oracle Ksplice for zero-downtime kernel patching."

#### Command Quick Reference

| Task | Command |
|------|---------|
| Check SELinux status | `getenforce`, `sestatus` |
| Find SELinux denials | `sudo ausearch -m avc -ts recent` |
| Generate SELinux policy | `audit2allow -M module_name` |
| Set file context | `semanage fcontext -a -t TYPE "path(/.*)?"` then `restorecon -Rv path` |
| List LVM | `pvs`, `vgs`, `lvs` |
| Extend LV + filesystem | `lvextend -L +1G /dev/vg/lv` then `xfs_growfs /mount` |
| LVM snapshot | `lvcreate -L 500M -s -n snap /dev/vg/lv` |
| View service logs | `journalctl -u service -p err --since "1h ago"` |
| Check OOM kills | `journalctl -k \| grep -i oom` |
| Set cgroup limits | `systemctl set-property svc MemoryMax=512M` |
| Socket analysis | `ss -tlnp` (listening), `ss -tnp` (established) |
| Packet capture | `tcpdump -i any port 8000 -n -c 20` |
| Firewall rich rules | `firewall-cmd --add-rich-rule='rule ...'` |
| Kernel tuning | `sysctl -w param=value` or `/etc/sysctl.d/` |
| CPU bottleneck | `top`, `ps aux --sort=-%cpu`, `strace -c -p PID` |
| Memory analysis | `free -h`, `vmstat 1`, `cat /proc/PID/status` |
| Disk analysis | `iostat -xz 1`, `sar -d 1`, `df -h`, `df -i` |
| User management | `useradd`, `usermod`, `chage`, `passwd` |
| ACLs | `setfacl -m u:user:rwx path`, `getfacl path` |
| Process investigation | `strace -p PID`, `/proc/PID/status`, `lsof -p PID` |
| Check available patches | `dnf check-update`, `dnf updateinfo list security` |
| Apply security patches | `sudo dnf update --security -y` |
| Patch rollback | `dnf history`, `sudo dnf history undo <ID>` |
| Services needing restart | `sudo needs-restarting -s` (services), `-r` (reboot check) |
| Zero-downtime kernel patch | `sudo uptrack-upgrade -y` (Oracle Ksplice) |

#### Skills Mapped to Federal Cloud Engineer Job Description

| JD Requirement | Where You Practiced It |
|---------------|----------------------|
| "Linux Admin" in title | SELinux, LVM, systemd, PAM, user management, NFS |
| "ensuring security" | SELinux enforcing, PAM lockout, firewalld zones, sysctl hardening |
| "Automation" | systemd timers, sysctl drop-ins, logrotate configs |
| "disaster recovery" | LVM snapshots, backup verification, break-fix exercises |
| "troubleshooting" | 8 break-fix labs covering network, disk, memory, CPU, SELinux |
| "cost management" | Understanding resource limits to right-size VMs (cgroups, memory analysis) |
| "patch management" | Enterprise patching workflow with OCI OS Management Hub, Ksplice, `dnf history` rollback |

### Next: Phase 2 — Disaster Recovery Drill & Backup Architecture
