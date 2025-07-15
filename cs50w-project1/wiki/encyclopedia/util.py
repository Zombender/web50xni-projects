import re
from random import choice
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from markdown import markdown

def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                       for filename in filenames if filename.endswith(".md")))

def get_random_entry():
    entries = list_entries()
    try:
        return choice(entries)
    except IndexError:
        return None

def check_existent_entry(title: str) -> bool:
    """
    Returns true if an entry already exists, otherwise returns false
    """
    _, filenames = default_storage.listdir("entries")
    filenames = [filename.lower()[:-3] for filename in filenames]
    if title.lower() in filenames:
        return True
    return False

def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry_marksafe(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        content = f.read().decode('utf-8')
        return markdown(content)
    except FileNotFoundError:
        return None


