from html.parser import HTMLParser
from py_wikiracer.parser_constants import start_listen, start_ignore, TO_SKIP_TAGS


class TagNode:
    def __init__(self):
        self.tag = None
        self.attrs = None
        self.data = None
        self.parent = None
        self.children = []

    def __str__(self):
        if self.tag is None:
            return f'Data: {self.data}'
        else:
            return f'Tag: {self.tag} , Attrs: {self.attrs}'


class TagTree:
    def __init__(self, root=None):
        self.root = root

    def __str__(self):
        stack = [(0, self.root)]
        response = ''
        while True:
            if len(stack) == 0:
                break
            current_level, cn = stack.pop()
            for ch in reversed(cn.children):
                stack.append((current_level + 1, ch))
            response += '\t' * current_level + str(cn) + '\n'
        return response


class TagTreeParser(HTMLParser):
    def __init__(self, start_listen_test: callable = start_listen,
                 start_ignore_test: callable = start_ignore,
                 to_skip_tags: tuple = TO_SKIP_TAGS):
        super().__init__()

        self.tag_root = None
        self.current_tag = None
        self.tag_stack = None
        self.listen = None
        self.ignore = None

        self.start_listen_test = start_listen_test
        self.start_ignore_test = start_ignore_test
        self.to_skip_tags = set(to_skip_tags)

        self.__reset()

    def __reset(self):
        # Init all the variable structures
        self.tag_root = None
        self.current_tag = None

        self.tag_stack = []
        self.listen = False
        self.ignore = False

    def do_root(self, tag, attrs):
        self.tag_root = TagNode()
        self.tag_root.tag = tag
        self.tag_root.attrs = attrs
        self.current_tag = self.tag_root

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Handling skip
        # Only can be possible skip a complete family of tags
        if tag in self.to_skip_tags:
            return

        # Handling listen start
        if self.start_listen_test(tag, attrs) and not self.listen:
            self.tag_stack.append('$')
            self.tag_stack.append(tag)
            self.listen = True
            self.do_root(tag, attrs)
            return

        if not self.listen:
            return

        # Handling ignore start
        if self.start_ignore_test(tag, attrs) and not self.ignore:
            self.tag_stack.append('@')
            self.tag_stack.append(tag)
            self.ignore = True
            return

        self.tag_stack.append(tag)

        if self.ignore:
            return

        new_node = TagNode()
        new_node.tag = tag
        new_node.attrs = attrs
        new_node.parent = self.current_tag
        self.current_tag.children.append(new_node)
        self.current_tag = new_node

    def handle_endtag(self, tag: str) -> None:
        # Handling skip
        if tag in self.to_skip_tags:
            return

        if not self.listen:
            return

        assert tag == self.tag_stack.pop()

        # Handling ignore ends
        if self.tag_stack[-1] == '@':
            self.tag_stack.pop()
            self.ignore = False
            return

        if self.ignore:
            return

        self.current_tag = self.current_tag.parent

        # Handling listen ends
        if self.tag_stack[-1] == '$':
            self.tag_stack.pop()
            assert len(self.tag_stack) == 0
            self.listen = False
            return

    def handle_data(self, data: str) -> None:
        if not self.listen or self.ignore:
            return

        # Direct rule to eliminate all the data at the first level
        if len(self.tag_stack) == 2:
            return

        data_node = TagNode()
        data_node.data = data
        data_node.parent = self.current_tag
        self.current_tag.children.append(data_node)

    def get_tag_tree(self, html):
        self.feed(html)
        tag_tree = TagTree(self.tag_root)
        self.reset()
        self.__reset()
        return tag_tree



"""
    def parse_html(self, html):
        tag_tree = self.get_tag_tree(html)
    
        self.filter_children()
        return self.parse_tag_tree(tag_tree)
    
    def parse_tag_tree(self, tag_tree):
        tags2parser = {
            'p': self.parse_parag_node
        }
    
        results = []
        for children in tag_tree.root.children:
            if children.tag in tags2parser:
                result = tags2parser[children.tag](children)
                results.append(result)
    
        return results
    
    def parse_parag_node(self, parag):
        text = ''
        links = []
        stack = [parag]
        while True:
            if len(stack) == 0:
                return text, links
            cn = stack.pop()
            if cn.tag == 'a':
                a_text = self.parse_link_node(cn)
                links.append((len(text), link_from_a_tag(cn)))
                text += a_text
                continue
            if cn.tag == 'sup':
                continue
            if cn.tag is None:
                text += cn.data
                continue
            for ch in reversed(cn.children):
                stack.append(ch)
    
    @staticmethod
    def parse_link_node(link):
        rs = ''
        stack = [link]
        while True:
            if len(stack) == 0:
                return rs
            cn = stack.pop()
            if cn.tag is None:
                rs += cn.data
                continue
    
            for ch in reversed(cn.children):
                stack += cn.children
"""
