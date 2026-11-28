# Telegram rollout (proposal only)
1. Preserve dry-run default. No token in repository, chat, logs, PR CI or model preparation. Use protected environment secrets only after explicit approval.
2. Use a separate private test channel and bot with only posting rights. Validate exact numeric channel ID and bot identity with read-only getMe/getChat/getChatMember; do not send during validation. No redirects; redact token-bearing URLs.
3. Implement transport separately, mock all network calls in CI, deny unapproved destination, enforce HTML length and escaping, timeout, rate cap and explicit approval per draft.
4. Durable outbox: unique draft ID, transactional claim, attempt state and message ID. On ambiguous timeout mark UNKNOWN and require reconciliation; never blindly retry. Handle 429 retry_after with bounded backoff only when rejection is definite.
5. After explicit owner approval only: one test message in private test channel, verify message ID, then manual review mode. Production channel and scheduler require separate approval.
6. Kill switch defaults off; revoke bot posting rights or rotate token if compromised. No paid service.
Current blockers: reviewed lock must be committed and used by runtime; action revisions pinned; actual restricted DB login and runtime integration tested; Neon free quotas and scale-to-zero verified; calendar release verification and editorial quality reviewed. No live sends authorized.
