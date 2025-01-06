# ----------------- TO SKIP -------------------

SELF_CLOSING_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                     'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
SKIP_ON_P = {'b', 'i'}
TO_SKIP_TAGS = tuple(SELF_CLOSING_TAGS) + tuple(SKIP_ON_P)

# ----------------- TO IGNORE -------------------
BY_NOW_IGNORING = {'h1', 'h2', 'h3', 'h4', 'h5', 'figure', 'table', 'ul', 'span', 'ol', 'dl'}

IGNORE_ON_P = {'sup'}
IGNORED_ALL = {'style', 'blockquote'}
IGNORED_TAGS = IGNORE_ON_P.union(IGNORED_ALL).union(BY_NOW_IGNORING)

IGNORED_ATTRS = {
    ('class', 'navbox-styles'), ('role', 'navigation'),
    ('class', 'reflist'), ('class', 'refbegin'),
    ('class', 'shortdescription nomobile noexcerpt noprint searchaux'),
    ('class', 'hatnote navigation-not-searchable'),
    ('class', 'toclimit-3'),
    ('class', 'barbox tright'),
    ('class', 'excerpt-block'),
    ('class', 'thumb tmulti tright'),
    ('style', 'clear:both;'),
    ('class', 'reflist reflist-lower-alpha'),
    ('href', '/wiki/Help:Pronunciation_respelling_key'),
    ('class', 'mw-empty-elt'),
    ('class', 'side-box side-box-right plainlinks sistersitebox'),
    ('class', 'thumb tmulti tleft')
}

def start_ignore(tag, attrs):
    return tag in IGNORED_TAGS or any([at in IGNORED_ATTRS for at in attrs])
    # return False


# ----------------- TO LISTEN -------------------
START_ATTR = ('class', 'mw-content-ltr mw-parser-output')
START_TAG = 'div'

# To start Test
def start_listen(tag, attrs):
    return tag == START_TAG and START_ATTR in attrs

