import re
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word.decode('ascii'))
    return str('-'.join(result))


def uniquify(seq):
    """Removes duplicate items from a list whilst preserving order. """
    seen = set()
    if not seq:
        return []
    return [x for x in seq if x not in seen and not seen.add(x)]
