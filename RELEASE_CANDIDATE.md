# NEXUS preview RC candidate (not approved)
Scope: offline and public RSS preview only. No Telegram transport, paid APIs, scheduler activation or cloud migration.
Baseline 417c5ee: 45 offline tests and 3 PostgreSQL integration tests passed; dependency lock failed due to pip-tools incompatibility. OPUS status must be verified.
Required gates on final HEAD:
- All seven CI workflows pass; inspect logs, not just status.
- Download and review generated SHA-256 lock; commit reviewed lock and use it in actual runtime build. Audit must pass without ignored findings. Pin model revision and actions; CPU wheel source must match audited environment.
- PostgreSQL role tests pass; verify function owner is dedicated non-login least-privilege role before cloud migration. Test actual restricted login, not only SET ROLE.
- Test runtime with local database and prebuilt model, no secrets during installation. Runtime refuses dynamic installation; disabled scheduler template intentionally cannot run until rebuilt.
- Confirm macro preview and RSS end-to-end, persistent dedup, no sends.
- Verify Neon free quotas and scale-to-zero before any cloud connection. No live activation without owner approval.
Rollback: leave main unchanged, leave scheduler disabled, discard isolated test database. No cloud migration in this RC.
