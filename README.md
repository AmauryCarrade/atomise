# Atomise Newsletters

A simple tool to convert newsletters (or any IMAP search, really) into an Atom
feed.

This tool was built with simplicity in mind: it will only convert mails
corresponding to given filter(s) into Atom feed(s), then write these feeds in
a folder. It is then your responsibility to expose these feeds over HTTP(S),
e.g. using nginx.

This tool being stateless, to update continuously the feeds, you should run
the script in a cron or systemd timer.

## State of the project

This project is still in progress. Here’s where we are.

- [x] Read mails into Atom feeds.
- [x] Post-process HTML mails for decent display in Atom/RSS feeds reader.
- [x] Mark mails as read when they are exported into an Atom feed.
- [x] Multiple mailbox support.
- [ ] OAuth mailbox support (read: Gmail).
- [ ] Post-process HTML mails to remove extra or useless elements (e.g.
      “Unsubscribe” link).
- [ ] Atom feed size limits.
- [ ] Per-feed update delay, to avoid searching the mailbox at all if the script
      is called again too soon.
- [ ] Generate recap and index file with generated feeds’ URLs, for convenience.
