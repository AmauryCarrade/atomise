import copy

from lxml_html_clean import clean_html
from bs4 import BeautifulSoup, Tag, NavigableString, PageElement


__excluded_table_tags_names = ["table", "thead", "tbody", "tfoot", "tr", "th", "td"]


def filter_out_tables_from_tree(root_element: PageElement):
    """
    Filters out in-place the given BeautifulSoup tree by removing tables
    structural elements (thread/tbody/tr/etc.). Other elements (tags or
    strings) are left as-is.

    The tree is filtered in-place but elements may be cloned in the process.
    You must not expect old references to elements anywhere in the tree to
    stay relevant as all elements children of a table element will be cloned.

    FIXME This should only remove tables with role="presentation", and their
     structural elements; but keep data tables (and their structural elements).

    :param root_element: The root element to filter out tables from.
    """
    if isinstance(root_element, NavigableString):
        return

    elif isinstance(root_element, Tag):
        # If this is not an excluded tag, we keep it as is but scan its children
        # if there are tags in them.
        # If there are no children, the loop will not loop and recursivity will
        # stop there.
        if root_element.name not in __excluded_table_tags_names:
            for child in root_element.children:
                if isinstance(child, Tag):
                    filter_out_tables_from_tree(child)

        # Else, we want to filter out that element. We’ll insert a copy of every
        # child (if there is any) at its place in the tree, then remove the
        # element from the tree.
        else:
            for child in root_element.children:
                child_copy = copy.copy(child)
                root_element.insert_before(child_copy)
                if isinstance(child_copy, Tag):
                    filter_out_tables_from_tree(child_copy)
            root_element.extract()


def sanitise_email_html(html: str) -> str:
    """
    Sanitises the given “email html” string:
    – clean-up conditional comments;
    – fixes bad HTML;
    – removes scripts and styles;
    – removes tables, as they are often used for email layout;
    – extract body content and returns that only (without “body” tag).

    :param html: The raw HTML to process.
    :return: The body’s content (only), sanitised as explained above.
    """
    html = clean_html(html)

    soup = BeautifulSoup(html, "lxml")

    # Remove styles, scripts (if any)
    for element in soup(["script", "style"]):
        element.decompose()

    # Remove tables with role presentation as they are commonly used on mail
    # layouts.
    filter_out_tables_from_tree(soup)

    # Only keep the body content
    body = soup.body if soup.body else soup
    html = body.prettify().strip()

    # Remove <body> </body>
    if html.startswith("<body>"):
        html = html[len("<body>") :]
    if html.endswith("</body>"):
        html = html[: -len("</body>")]

    return html
