# WHOOP export email privacy policy

Goal: import WHOOP Data Export files without broadly fetching a mailbox.

Rules for humans and agents:

- Search narrowly before reading messages.
- Only fetch messages that match the known WHOOP export sender/subject/name pattern.
- Do not scan unrelated mailbox contents.
- Do not store mail credentials in this repo.
- Do not commit `.eml`, `.em1`, attachments, tokens, or exports.

Recommended search strategy:

- Sender contains WHOOP / no-reply WHOOP export sender once confirmed from a sample `.eml`.
- Subject/body contains the exact export name or marker from the sample mail.
- Date window should be narrow when possible.
- Fetch only the matching message and attachment.

Setup step:

1. Open the sample mail file in VS Code.
2. Identify stable fields: From, Subject, attachment filename, key body phrase.
3. Save only those matching rules in local config, not the mail itself.

Do not commit sample emails. If you need to document a matcher, extract only stable non-sensitive fields such as sender domain, subject prefix, and attachment filename pattern. `.em1` is treated as a user-provided variant of `.eml` and should follow the same privacy rules.
