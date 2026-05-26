# P2 Evidence — Container-Layer Pull-Through Cache (Cache #2)

Proof of the container-tier cache (a registry pull-through mirror for k3s). This is
the project's second cache, at a different layer than the service-tier Redis (cache
#1, ADR-020). You provision the mirror infra yourself (Terraform + containerd config).

> 📋 **EVIDENCE CHECKPOINT** — files to commit to `docs/exercises/p2/`:
> - [ ] `pull-time-before-after.txt` — `time` of a cold node image pull WITHOUT the mirror vs WITH it
> - [ ] `dr-rebuild-delta.txt` — node-replacement / DR-rebuild time before vs after the mirror
> - [ ] `containerd-mirror-config.txt` — the containerd registry-mirror config you applied (sanitized)
> - [ ] `digest-pinning.md` — note on pinning images by digest to avoid a stale `:latest`
> - [ ] notes below

## What I built
-

## What broke / what I tuned
- (mirror storage/GC, digest vs tag, containerd config gotchas)

## Key Takeaways
- (write your takeaways here — cache #2 is a kept feature, no dedicated ADR)
