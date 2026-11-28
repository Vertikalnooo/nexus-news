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

## Evidence: e4ed22eb
All seven workflows passed. 49 tests across offline and PostgreSQL, audit no known vulnerabilities, hash-locked installation and pip check passed, fixed OPUS revision bb09c99d180016eac6819df3dae68edb1690fdee, three RSS previews in audited environment, no sends. Audit run 46085190900, artifact 15238907079, archive SHA256 cf046e43430a39ad528fc2bbd2e7a6679c345c894137c028c547b5ca155bd8e7. Calendar 5 high impact, zero actuals; BLS 133 observations. RC preview baseline passes CI but remaining gates above are not waived. See TELEGRAM_ROLLOUT.md.

## Editorial release gate
Prior sample: 30 headlines, 25 translations returned, 5 rejected by editor. Material errors remain in returned translations. No autonomous publication approval. Gemini quota migration and candidate Transformers CI pending; do not replace lock or apply cloud migrations until verified. Independent verifier interface is not a deployed semantic verifier. Keep scheduler disabled.
