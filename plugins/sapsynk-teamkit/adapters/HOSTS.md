# Hosts for sapsynk-teamkit

Portable skill: `skills/verify-this`. Original text stays upstream and is linked, not copied: [../upstream/teamkit/skills/verify-this/SKILL.md](../upstream/teamkit/skills/verify-this/SKILL.md). The parent build bundles that source. Repo checkout path of the same file: `upstream/teamkit/skills/verify-this/SKILL.md`.

## Portable

- Six steps stay in order: falsifiable claim, smallest surface, baseline, treatment (same command, data, warmup, environment), artifact comparison, one verdict (`VERIFIED`, `NOT VERIFIED`, `INCONCLUSIVE`).
- Prefer the project `verify-vao` surface when it exists.
- Inline evidence only unless the user agrees to disk. No secrets in artifacts.

## Native (host-dependent)

Browser screenshots, accessibility snapshots, `control-ui` / `control-cli`, CPU profiles, and heap tools exist only when that host provides them. Missing tools make the verdict `INCONCLUSIVE` or a smaller local check. They are not downloaded by this plugin.

## Parity

No cloud/native parity claim. A laptop browser trace and a headless cloud run are different measurements. Say which surface you used.
