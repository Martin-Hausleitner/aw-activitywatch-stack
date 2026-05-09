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

Pending: paste/provide the `.eml`/`.em1` sample so the exact matcher can be documented.
