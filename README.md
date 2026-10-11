# Atomise Newsletters

A simple tool to convert newsletters (or any IMAP search, really) into an Atom
feed.

This tool was built with simplicity in mind: it will only convert mails
corresponding to given filter(s) into Atom feed(s), then write these feeds in
a folder. It is then your responsibility to expose these feeds over HTTP(S),
e.g. using nginx.

This tool being stateless, to update continuously the feeds, you must run
it in a cron or systemd timer.


## Installation and usage

To install, for now:
1. clone this repository;
2. run `uv sync`
   ([install `uv` first](https://docs.astral.sh/uv/getting-started/installation/)
   if needs be, or use another package manager, as your convenience);
3. duplicate the `newsletters.example.toml` into your own `newsletters.toml`.

Then, run `atomise`.
```bash
$ uv run atomise
```

It does not print anything by default; add `-v/-vv/-vvv` if you want details.
Run with `--help` for other options.


## State of the project

This project is still in progress. Here’s where we are. These items are not
ordered.

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
- [ ] Write full documentation.
- [ ] Add tests to HTML post-processors, and test more edge cases.
- [ ] Install `atomise` with pip and run it without `uv`.


## Licence

This tool is a free software distributed under the CeCILL-B public licence,
similar to the BSD licence in French law (read in
[French](https://cecill.info/licences/Licence_CeCILL-B_V1-fr.html),
[English](https://cecill.info/licences/Licence_CeCILL-B_V1-en.html)).
