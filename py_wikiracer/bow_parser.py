
IRRELEVANT_WORDS = {'of', 'is', 'have', 'has', 'as', 'by', 'the', 'this', 'who',
                    'in', 'that', 'to', 'with', 'a', 'and', 'at', 'from',
                    'its', 'on', 'an', 'it', 'was', 'were', 'his', 'he',
                    'for', 'would', 'any', 'some', 'one', 'him', 'are', 'or', 'be', 'its', 'not'}

'''
            'for', 'him', 'are', 'but', 'have', 'this', 'which', 'also', 'into', 'such',
            'most', 'more', 'than', 'they', 'their', 'all', 'her', 'she', 'many', 'other',
            'there', 'been', 'see', 'about', 'when', 'often', 'always', 'any', 'main', 'what', 'when', 'why',
            'do', 'does', 'while', 'can', 'that', 'these', 'this', 'being', 'use', 'made', 'kit',

            'articles', 'links', 'wikipedia', 'list', 'editor', 'new', 'except', 'unsourced', 'wikidata',
            'description', 'edit', 'used'
'''


CHARS_TO_ERASE = '(),.\n;:\'\"-'
DISALLOWED = [":", "#", "/", "?"]

def link_from_a_tag(a):
    for at in a.attrs:
        if at[0] == 'href':
            return at[1]
    return None

def valid_link(link):
    if link[:6] != '/wiki/':
        return False
    if any([i in DISALLOWED for i in link[6:]]):
        return False
    return True




# Expect a tag tree that is a root with a list of p children with a list of data or a node
class Bow_Parser:
    @staticmethod
    def check_format_p(p):
        for ch in p.children:
            if ch.tag is None:
                # Ch is a Data Node
                valid = ch.attrs is None and len(ch.children) == 0 and isinstance(ch.data, str)
                assert ch.parent == p
                if not valid:
                    return False

            elif ch.tag == 'a':
                # Ch is a link node
                link = link_from_a_tag(ch)
                valid = (link_from_a_tag(ch) is not None and link[:6] == '/wiki/' and
                         len(ch.children) == 1 and ch.data is None)
                assert ch.parent == p
                if not valid:
                    return False

            else:
                # Ch is another node
                return False

        return True

    def tag_tree_2_bow(self, tag_tree):
        words_bow = []
        adj_bow = []
        for ch in tag_tree.root.children:
            ch_words_bow, ch_adj_bow = self.p_2_bow(ch)
            words_bow.extend(ch_words_bow)
            adj_bow.extend(ch_adj_bow)

        return words_bow, adj_bow

    def p_2_bow(self, p):
        if not self.check_format_p(p):
            return [], []

        words_bow = []
        adj_bow = []
        for ch in p.children:
            if ch.tag == 'a':
                # Ch is a link
                link = link_from_a_tag(ch)
                if not valid_link(link):
                    continue
                adj_bow.append(link)
                continue

            # Ch is a data node
            words = ch.data
            for c in CHARS_TO_ERASE:
                words = words.replace(c, '')

            words = words.strip(' ')
            words = words.lower()
            if len(words) <= 1:
                continue

            words = words.split(' ')

            for w in words:
                if w in IRRELEVANT_WORDS:
                    continue
                if w.isnumeric():
                    continue
                words_bow.append(w)

        return words_bow, adj_bow
