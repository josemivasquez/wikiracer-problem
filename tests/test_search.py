import random
import sys
from typing import Callable, Iterator
from itertools import chain
from collections import defaultdict
from types import ModuleType
from importlib import reload
from urllib.request import urlopen

import pytest
from py_wikiracer.internet import Internet
from py_wikiracer.wikiracer import Parser, BFSProblem, DFSProblem, DijkstrasProblem, WikiracerProblem

REQ_LIMIT = 75 # per test, normally

def test_parser():
    internet = Internet()
    html = internet.get_page("/wiki/Henry_Krumrey")
    assert Parser.get_links_in_page(html) == ['/wiki/Wisconsin_State_Senate', '/wiki/Wisconsin_Senate,_District_20', '/wiki/Wisconsin_State_Assembly', '/wiki/Plymouth,_Sheboygan_County,_Wisconsin', '/wiki/Republican_Party_(United_States)', '/wiki/Sheboygan_County,_Wisconsin', '/wiki/United_States_presidential_election_in_Wisconsin,_1900', '/wiki/Crystal_Lake,_Illinois', '/wiki/Henry_Krumrey', '/wiki/Main_Page']

def test_trivial():
    """
    All pages contain a link to themselves, which any search algorithm should recognize.
    """
    bfs = BFSProblem()
    dfs = DFSProblem()
    dij = DijkstrasProblem()

    assert bfs.bfs(source = "/wiki/ASDF", goal = "/wiki/ASDF") == ["/wiki/ASDF", "/wiki/ASDF"]
    assert dfs.dfs(source = "/wiki/ASDF", goal = "/wiki/ASDF") == ["/wiki/ASDF", "/wiki/ASDF"]
    assert dij.dijkstras(source = "/wiki/ASDF", goal = "/wiki/ASDF") == ["/wiki/ASDF", "/wiki/ASDF"]

    assert bfs.internet.requests == ["/wiki/ASDF"]
    assert dfs.internet.requests == ["/wiki/ASDF"]
    assert dij.internet.requests == ["/wiki/ASDF"]

def test_trivial_2():
    """
    Searches going to page 1 distance away.
    """
    bfs = BFSProblem()
    dfs = DFSProblem()
    dij = DijkstrasProblem()

    assert bfs.bfs(source = "/wiki/Reese_Witherspoon", goal = "/wiki/Academy_Awards") == ["/wiki/Reese_Witherspoon", "/wiki/Academy_Awards"]
    assert dfs.dfs(source = "/wiki/Reese_Witherspoon", goal = "/wiki/Academy_Awards") == ["/wiki/Reese_Witherspoon", "/wiki/Academy_Awards"]
    assert dij.dijkstras(source = "/wiki/Reese_Witherspoon", goal = "/wiki/Academy_Awards") == ["/wiki/Reese_Witherspoon", "/wiki/Academy_Awards"]

    assert bfs.internet.requests == ["/wiki/Reese_Witherspoon"]
    assert dfs.internet.requests == ["/wiki/Reese_Witherspoon"]
    assert dij.internet.requests == ["/wiki/Reese_Witherspoon"]

def test_bfs_basic():
    """
    BFS depth 2 search
    """
    bfs = BFSProblem()
    assert bfs.bfs(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == ['/wiki/Calvin_Li', '/wiki/Chinese_language', '/wiki/Wikipedia']
    assert bfs.internet.requests == ['/wiki/Calvin_Li', '/wiki/Chinese_name', '/wiki/Chinese_surname', '/wiki/Li_(surname_%E6%9D%8E)', '/wiki/Wuhan', '/wiki/Hubei', '/wiki/Central_Academy_of_Drama', '/wiki/All_Men_Are_Brothers_(TV_series)', '/wiki/Chinese_language']

def test_dfs_basic():
    """
    DFS depth 2 search
    """
    dfs = DFSProblem()
    assert dfs.dfs(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == ['/wiki/Calvin_Li', '/wiki/Main_Page', '/wiki/Wikipedia']
    assert dfs.internet.requests == ['/wiki/Calvin_Li', '/wiki/Main_Page']

def test_dijkstras_basic():
    """
    DFS depth 2 search
    """
    dij = DijkstrasProblem()
    # This costFn is to make sure there are never any ties coming out of the heap, since the default costFn produces ties and we don't define a tiebreaking mechanism for priorities
    assert dij.dijkstras(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia", costFn = lambda y, x: len(x) * 1000 + x.count("a") * 100  + x.count("u") + x.count("h") * 5 - x.count("F")) == ['/wiki/Calvin_Li', '/wiki/Main_Page', '/wiki/Wikipedia']
    assert dij.internet.requests == ['/wiki/Calvin_Li', '/wiki/Hubei', '/wiki/Wuxia', '/wiki/Wuhan', '/wiki/Pinyin', '/wiki/Firefox', '/wiki/Tencent', '/wiki/Wu_Yong', '/wiki/Cao_Cao', '/wiki/John_Woo', '/wiki/Kelly_Lin', '/wiki/Sina_Corp', '/wiki/Huo_Siyan', '/wiki/Shawn_Yue', '/wiki/Main_Page']

class CustomInternet():
    def __init__(self):
        self.requests = []
    def get_page(self, page):
        self.requests.append(page)
        return f'<a href="{page}"></a>'

def test_none_on_fail():
    """
    Program should return None on failure
    """
    bfs = BFSProblem()
    dfs = DFSProblem()
    dij = DijkstrasProblem()

    # Testing hack: override the internet to inject our own HTML
    bfs.internet = CustomInternet()
    dfs.internet = CustomInternet()
    dij.internet = CustomInternet()

    assert bfs.bfs(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == None
    assert dfs.dfs(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == None
    assert dij.dijkstras(source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia") == None

    assert bfs.internet.requests == ["/wiki/Calvin_Li"]
    assert dfs.internet.requests == ["/wiki/Calvin_Li"]
    assert dij.internet.requests == ["/wiki/Calvin_Li"]

def test_dfs_complex():
    """
    A complex DFS example to test your searching algorithm.
    """
    dfs = DFSProblem()
    assert dfs.dfs(source = "/wiki/Calvin_Li", goal = "/wiki/Quebecor") == ['/wiki/Calvin_Li', '/wiki/Main_Page', '/wiki/Wikimedia_Foundation', '/wiki/VIAF_(identifier)', '/wiki/Virtual_International_Authority_File', '/wiki/Interested_Parties_Information', '/wiki/Law', '/wiki/Human_science', '/wiki/Truth', '/wiki/Verstehen', '/wiki/Phronesis', '/wiki/Knowledge', '/wiki/Max_Weber', '/wiki/Trove_(identifier)', '/wiki/Trove', '/wiki/The_Sydney_Morning_Herald', '/wiki/OzTAM', '/wiki/Canwest', '/wiki/Pembroke_Daily_Observer', '/wiki/Postmedia_News', '/wiki/Postmedia_Network', '/wiki/Dose_(magazine)', '/wiki/Northern_News', '/wiki/Jam!', '/wiki/Quebecor']
    assert dfs.internet.requests == ['/wiki/Calvin_Li', '/wiki/Main_Page', '/wiki/Wikimedia_Foundation', '/wiki/VIAF_(identifier)', '/wiki/Virtual_International_Authority_File', '/wiki/Interested_Parties_Information', '/wiki/Law', '/wiki/Human_science', '/wiki/Truth', '/wiki/Verstehen', '/wiki/Phronesis', '/wiki/Knowledge', '/wiki/Max_Weber', '/wiki/Trove_(identifier)', '/wiki/Trove', '/wiki/The_Sydney_Morning_Herald', '/wiki/OzTAM', '/wiki/Canwest', '/wiki/Pembroke_Daily_Observer', '/wiki/Postmedia_News', '/wiki/Postmedia_Network', '/wiki/Dose_(magazine)', '/wiki/Northern_News', '/wiki/Jam!']


def test_wikiracer_1():
    """
    Tests wikiracer speed on one input.
    A great implementation can do this in less than 8 internet requests.
    A good implementation can do this in less than 15 internet requests.
    A mediocre implementation can do this in less than 30 internet requests.

    To make your own test cases like this, I recommend finding a starting page,
    clicking on a few links, and then seeing if your program can get from your
    start to your end in only a few downloads.
    """
    limit = 15

    racer = WikiracerProblem()
    racer.wikiracer(source="/wiki/Computer_science", goal="/wiki/Richard_Soley")
    assert len(racer.internet.requests) <= limit



def test_wikiracer_2():
    """
    Tests wikiracer speed on one input.
    A great implementation can do this in less than 25 internet requests.
    A good implementation can do this in less than 80 internet requests.
    A mediocre implementation can do this in less than 300 internet requests.
    """
    limit = 80

    racer = WikiracerProblem()
    racer.wikiracer(source="/wiki/Waakirchen", goal="/wiki/A")
    assert len(racer.internet.requests) <= limit

