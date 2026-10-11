from functools import cached_property
from typing import Union, List, Optional, Generator, Iterator

import click
from imap_tools import MailBox, MailboxFolderSelectError, AND, OR, MailMessage
from imap_tools.query import LogicOperator

StrOrListOfStr = Union[str, List[str]]


def _to_list_if_not_already(obj: Optional[StrOrListOfStr]) -> list:
    return (
        obj
        if isinstance(obj, list)
        else [obj] if obj is not None and len(obj) > 0 else []
    )


def compute_filter(
    from_: Optional[StrOrListOfStr] = None,
    to: Optional[StrOrListOfStr] = None,
    subject: Optional[StrOrListOfStr] = None,
    body: Optional[StrOrListOfStr] = None,
    imap_raw_search: Optional[str] = None,
) -> Union[LogicOperator, str]:
    # Build an IMAP search to find emails for that newsletter in
    # each folder we want to search into.
    if imap_raw_search:
        return imap_raw_search
    else:
        from_ = _to_list_if_not_already(from_)
        to = _to_list_if_not_already(to)
        subject = _to_list_if_not_already(subject)
        body = _to_list_if_not_already(body)

        filter_args = []

        if len(from_) > 0:
            filter_args.append(OR(from_=from_))
        if to:
            filter_args.append(OR(to=to))
        if subject:
            filter_args.append(OR(subject=subject))
        if body:
            filter_args.append(OR(body=body))

        return AND(*filter_args)


class NewsletterMailbox:
    # Folders we never scan: trash, junk and non-selectable containers.
    _SKIP_FOLDERS_FLAGS = {"\\Trash", "\\Junk", "\\Noselect", "\\NoSelect"}

    def __init__(self, host, port, username, password):
        self._mailbox = MailBox(host=host, port=port)
        self._mailbox.login_utf8(username=username, password=password)

        self._initial_folder = self._mailbox.folder.get()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._mailbox.logout()

    def get_messages(
        self,
        folders: Optional[StrOrListOfStr] = None,
        search_filter: Optional[Union[LogicOperator, str]] = None,
        mark_seen: bool = False,
    ) -> Iterator[MailMessage]:
        # Go back to the default folder, to start from a clean state.
        self._mailbox.folder.set(self._initial_folder)

        # List folders to search into.
        folders = _to_list_if_not_already(folders)
        orig_folders = folders.copy()

        if folders:
            folders = self._get_existing_folders(folders)
        else:
            folders = self._all_folders

        removed_folders = set(orig_folders) - set(folders)
        if removed_folders:
            click.echo(
                f"-> These folders were requested but does not exist: {', '.join(removed_folders)}",
                err=True,
            )

        # Yield messages matching these filters for each folder.
        for folder in folders:
            try:
                self._mailbox.folder.set(folder)
            except MailboxFolderSelectError:
                click.echo(f"Unknown folder: {folder}", err=True)
                continue

            yield from self._mailbox.fetch(
                search_filter or "NOT ALL",
                mark_seen=mark_seen,
                bulk=10,
                charset="utf-8",
            )

    @cached_property
    def _all_folders(self):
        return list(
            map(
                lambda folder_info: folder_info.name,
                filter(
                    lambda folder_info: not {f for f in folder_info.flags if f}
                    & self._SKIP_FOLDERS_FLAGS,
                    self._mailbox.folder.list(),
                ),
            )
        )

    def _get_existing_folders(self, folders_names):
        return list(
            filter(lambda folder_name: folder_name in self._all_folders, folders_names)
        )
