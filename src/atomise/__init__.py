import hashlib
import pathlib

import click
import feedgenerator
import toml

from slugify import slugify

import atomise.sanitise
from atomise.mailbox import NewsletterMailbox, compute_filter

SKIP_FOLDERS = {"\\Trash", "\\Junk", "\\Noselect", "\\NoSelect"}


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default="newsletters.toml",
)
@click.option("-v", "--verbose", count=True)
def main(config, verbose):
    newsletters_config = toml.load(config)

    feeds_dir = pathlib.Path(newsletters_config["feeds_dir"])
    index_dir = pathlib.Path(newsletters_config["index_dir"])

    feeds_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    for mailbox_config in newsletters_config["mailbox"]:
        with NewsletterMailbox(
            host=mailbox_config["host"],
            port=mailbox_config["port"],
            username=mailbox_config["username"],
            password=mailbox_config["password"],
        ) as mailbox:
            if verbose >= 1:
                print(f'Connected to {mailbox_config["username"]} mailbox')

            for newsletter_id in mailbox_config["newsletter"].keys():
                newsletter = mailbox_config["newsletter"][newsletter_id]

                if verbose >= 1:
                    click.echo(f'Loading newsletter {newsletter["title"]}…')

                # Will hold all retrieved messages for this newsletter.
                newsletter_messages = []

                search_filter = compute_filter(
                    from_=newsletter.get("from"),
                    to=newsletter.get("to"),
                    subject=newsletter.get("subject"),
                    body=newsletter.get("body"),
                    imap_raw_search=newsletter.get("imap_raw_search"),
                )

                if verbose >= 3:
                    click.echo(f"-> Query computed from rules: {search_filter}")

                for msg in mailbox.get_messages(
                    folders=newsletter.get("folders"),
                    search_filter=search_filter,
                    mark_seen=newsletter.get("mark_as_read", False),
                ):
                    newsletter_messages.append(msg)

                newsletter_messages.sort(key=lambda m: m.date, reverse=True)

                if verbose >= 2:
                    click.echo(
                        f"-> Loaded {len(newsletter_messages)} messages matching this newsletter rules."
                    )

                    if verbose >= 3:
                        click.echo("-> Loaded messages")
                        for msg in newsletter_messages:
                            click.echo(
                                f"   - {msg.date.strftime('%Y-%m-%d')} {msg.subject}"
                            )

                feed_filename_hash = hashlib.sha1(
                    (newsletters_config["secret"] + newsletter_id).encode()
                ).hexdigest()

                feed_filename = f"{feed_filename_hash}-{slugify(newsletter_id)}.atom"
                feed_url = f"{newsletters_config['base_url']}/{feed_filename}"
                feed_link = newsletter["link"] if "link" in newsletter else feed_url

                feed = feedgenerator.Atom1Feed(
                    title=newsletter["title"],
                    link=feed_link,
                    description=(
                        newsletter["description"] if "description" in newsletter else ""
                    ),
                    feed_url=feed_url,
                )

                for msg in newsletter_messages:
                    uid = (
                        feed_url
                        + "/"
                        + hashlib.sha256(
                            (
                                msg.uid
                                + msg.subject
                                + msg.date_str
                                + msg.text
                                + msg.html
                            ).encode()
                        ).hexdigest()
                    )

                    content = ""

                    if msg.html:
                        content = sanitise.sanitise_email_html(msg.html)

                    elif msg.text:
                        # Very basic HTMLification for text-only mails
                        html = msg.text.replace("\n\n", "</p><p>").replace(
                            "\n", "<br/>"
                        )
                        content = f"<p>{html}</p>"

                    feed.add_item(
                        title=msg.subject,
                        description="",
                        date=msg.date,
                        author_name=msg.from_values.name,
                        author_email=msg.from_values.email,
                        link=feed_link,
                        pubdate=msg.date,
                        unique_id=uid,
                        unique_id_is_permalink=False,
                        content=content,
                    )

                with open(feeds_dir / feed_filename, "w") as f:
                    feed.write(f, "UTF-8")

                if verbose >= 2:
                    click.echo("")

    if verbose >= 1:
        click.echo("Done.")
