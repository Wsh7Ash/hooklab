# Changelog

All notable changes are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-29

### Added

- `hooklab check`: grades a hook plan on 12 rules with blocking, major and minor severities.
- `hooklab run`: executes a plan's exercise under `sys.setprofile`, captures named locals at call and the return value at return, and verifies expectations.
- `hooklab emit`: generates Frida agents, GDB Python scripts and LD_PRELOAD C interposers from the same plan, refusing anything it cannot emit safely.
- `hooklab report`: plan markdown with hooks table, expectations, cleanup and grade.
- Bounded capture with an explicit truncation flag, and a profiler restore path.
- 50 skills across `resolve`, `instrument`, `hook`, `capture`, `verify` and `teardown`.

### Fixed

- Three corpus pattern labels were shorter than the validator's eight-character floor and were rejected; the labels were lengthened rather than the floor relaxed.
- Draft-only extra keys (`when_note`, `when_extra`) were removed from corpus entries.
