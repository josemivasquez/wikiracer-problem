from py_wikiracer.internet import Internet
from typing import List, Dict, Set, Optional

from queue import PriorityQueue
from html.parser import HTMLParser
from collections import Counter
import re


def get_the_path(source, goal, node_to_parent):
    right_path = [goal]
    current_node = node_to_parent[goal]
    while current_node != source:
        right_path.append(current_node)
        current_node = node_to_parent[current_node]
    right_path.append(current_node)
    right_path.reverse()
    return right_path


def get_adjacents(node, internet):
    return Parser.get_links_in_page(internet.get_page(node))


class Parser:
    @staticmethod
    def get_links_in_page(html: str) -> List[str]:
        links = []
        disallowed = Internet.DISALLOWED

        disallowed_str = ''
        for ch in disallowed:
            disallowed_str += ch

        pattern_str = r'<[ \w]+href=\"(/wiki/[^' + disallowed_str + r'\"\']+)\"[^>]*>'
        pattern = re.compile(pattern_str)

        for p in pattern.findall(html):
            if p not in links:
                links.append(p)
        return links

class Frontier:
    def __init__(self):
        self.f_pq = PriorityQueue()
        self.f_set = set()

    def add(self, priority, item):
        self.f_pq.put((-priority, item))
        self.f_set.add(item)

    def get(self):
        to_remove = self.f_pq.get()
        to_remove = (-to_remove[0], to_remove[1])
        self.f_set.remove(to_remove[1])
        return to_remove

    def __contains__(self, item):
        return item in self.f_set

    def empty(self):
        return self.f_pq.empty()


from py_wikiracer.tag_tree_parser import TagTreeParser
from py_wikiracer.bow_parser import Bow_Parser

tag_tree_parser = TagTreeParser()
bow_parser = Bow_Parser()

def get_wiki_node(link, internet):
    html = internet.get_page(link)
    tag_tree = tag_tree_parser.get_tag_tree(html)
    words_bow, adjacents_bow = bow_parser.tag_tree_2_bow(tag_tree)
    words_counter = Counter(words_bow)
    adjacents_counter = Counter(adjacents_bow)
    node = WikiNode(html, link, words_counter, adjacents_counter)
    return node

class WikiNode:
    def __init__(self, html, link, words, adjacents):
        self.html = html
        self.link = link
        self.words = words
        self.adjacents = adjacents

class Scorer:
    def __init__(self):
        self.groups = []

    @staticmethod
    def match_words(link, counter) -> float:
        total_reps = sum(counter.values())
        link_words = link[6:].lower().split('_')
        points = 0

        for word, reps in counter.items():
            if word in link_words:
                points += reps

        local_score = points / total_reps * 50
        return local_score

    @staticmethod
    def match_adjacents(link, counter) -> float:
        assert all([])
        total_reps = sum(counter.values())
        points = 0

        for link_c, reps in counter.items():
            if link == link_c:
                points += reps

        return points / total_reps * 100

    @staticmethod
    def like_date(link) -> bool:
        if link[6:][:4].isdigit():
            return True

        link_words = set(link[6:].lower().split('_'))
        if len(link_words) < 3:
            return False

        for word in link_words:
            if len(word) == 4 and word.isdigit():
                return True

        return False

    def on_group(self, link: str) -> bool:
        link_words = set(link[6:].lower().split('_'))
        if len(link_words) < 3:
            return False

        for group in self.groups:
            if len(link_words & group) > 2:
                return True

        self.groups.append(link_words)
        return False

class InversePQ:
    def __init__(self):
        self.pq = PriorityQueue()

    def put(self, item):
        priority, data = item
        self.pq.put((-priority, data))

    def get(self):
        priority, data = self.pq.get()
        return -priority, data


class Stain:
    def __init__(self, seed, internet, scorer):
        self.seed = seed
        self.scorer = scorer

        self.frontier = InversePQ()
        self.frontier_set = set()

        self.visited = set()
        self.heritage = dict()

        self.words = Counter()

        self.downloaded = None
        self.guide = None

        self.frontier.put((0, seed))
        self.frontier_set.add(seed)

        self.proportions = []

    def download(self, internet):
        w, link = self.frontier.get()
        self.downloaded = get_wiki_node(link, internet)

    def expand(self):
        expansion = self.downloaded
        self.downloaded = None

        for adj in expansion.adjacents.keys():
            if adj in self.visited or adj in self.frontier_set:
                continue

            score = self.link_scorer(adj)
            self.frontier.put((score, adj))
            self.frontier_set.add(adj)

    def link_scorer(self, link):
        proportions = self.proportions
        score = 0
        scorer = self.scorer
        guide = self.guide

        # For self
        # Consider just words, the adjacents is generating now
        self_words_score = scorer.match_words(link, self.words)
        self_score = self_words_score

        # For guide
        # Consider both

        adjacents = Counter(guide.frontier_set)
        # assert all([i == 1 for i in guide.frontier.f_counter.values()])

        if guide.downloaded is not None:
            adjacents |= guide.downloaded.adjacents

        guide_words_score = scorer.match_words(link, guide.words)
        guide_adj_score = scorer.match_adjacents(link, adjacents)

        guide_score = guide_words_score * proportions[0][0] + guide_adj_score * proportions[0][1]
        score = self_score * proportions[1][0] + guide_score * proportions[1][1]

        score *= 100

        if self.scorer.like_date(link):
            score *= 0.0
        if self.scorer.on_group(link):
            score *= 0.0

        # score += parent_score

        return score

    def set_guide(self, guide):
        self.guide = guide

    def no_way(self):
        return len(self.frontier_set) == 0

    def get_path(self, join, back):
        path = []
        current_node = join
        while current_node != self.seed:
            path.append(current_node)
            current_node = self.heritage[current_node]
        path.append(current_node)

        if back:
            path.reverse()

        return path


class SourceStain(Stain):
    def __init__(self, *args):
        super().__init__(*args)
        self.proportions = [
            [0.02, 0.98],
            [0, 1]
        ]

    def download(self, internet) -> Optional[str]:
        super().download(internet)

        self.words.update(self.downloaded.words)
        self.visited.add(self.downloaded.link)

        # print('Source Downloaded: ', self.downloaded.link)

        # For save one download
        for adj_link in self.downloaded.adjacents.keys():
            if adj_link in self.visited:
                continue
            self.heritage[adj_link] = self.downloaded.link
            if adj_link in self.guide.solutions:
                return adj_link

        return None


class TargetStain(Stain):
    def __init__(self, *args):
        super().__init__(*args)
        self.solutions = {self.seed}
        self.proportions = [
            [0.15, 0.85],
            [1, 0]
        ]

    def download(self, internet):
        super().download(internet)
        # Visit the Node
        self.visited.add(self.downloaded.link)

        # print('Target Downloaded: ', self.downloaded.link)

        # Check for back and do heritage
        back = None
        for adj_link in self.downloaded.adjacents.keys():
            if adj_link in self.solutions:
                back = adj_link
            if adj_link in self.visited or adj_link in self.frontier_set:
                continue

        # (or) For the first cicle
        # Update words and add solutions
        if back or self.downloaded.link == self.seed:
            self.words.update(self.downloaded.words)
            self.solutions.add(self.downloaded.link)
            self.heritage[self.downloaded.link] = back
            # print('New Target: ', self.downloaded.link)

        return back or self.downloaded.link == self.seed


class WikiracerProblem:
    def __init__(self):
        self.internet = Internet()


    # Time for you to have fun! Using what you know, try to efficiently find the shortest path between two wikipedia pages.
    # Your only goal here is to minimize the total amount of pages downloaded from the Internet, as that is the dominating time-consuming action.

    # Your answer doesn't have to be perfect by any means, but we want to see some creative ideas.
    # One possible starting place is to get the links in `goal`, and then search for any of those from the source page, hoping that those pages lead back to goal.

    # Note: a BFS implementation with no optimizations will not get credit, and it will suck.
    # You may find Internet.get_random() useful, or you may not.

    def wikiracer(self, source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia"):
        target = goal

        # Bidirectional Search (1 - 1)
        scorer = Scorer()
        source_stain = SourceStain(source, self.internet, scorer)
        target_stain = TargetStain(target, self.internet, scorer)

        source_stain.set_guide(target_stain)
        target_stain.set_guide(source_stain)

        if source != goal:
            source_stain.visited.add(source)

        join = None
        while join is None:
            if source_stain.no_way():
                return None
            join = source_stain.download(self.internet)
            if join is not None:
                break
            back = target_stain.download(self.internet)
            source_stain.expand()
            if back:
                target_stain.expand()

        source_path = source_stain.get_path(join, True)
        target_path = target_stain.get_path(join, False)

        # Loop case
        if not len(source_path) == len(target_path) == 1:
            target_path = target_path[1:]

        return source_path + target_path
