import re
from py_wikiracer.internet import Internet
from py_wikiracer.wikiracer import Parser, BFSProblem, DFSProblem, DijkstrasProblem, WikiracerProblem
from time import time
from itertools import chain, combinations, permutations
from html.parser import HTMLParser
from collections import Counter

par = Parser()
internet = Internet()
bfs = BFSProblem()
dfs = DFSProblem()
dij = DijkstrasProblem()
racer = WikiracerProblem()

# pages = ['Jesus', 'Interbank', 'United_States', 'Candy', 'Altoids', 'Adolf_Hitler', 'John_von_Neumann', 'Donald_Knuth', 'Peru']
# pages = ['Jesus', 'Peace_churches', 'United_States', 'Candy', 'Altoids', 'Adolf_Hitler', 'Mao_Zedong']
# Manuel Chinese friend Test
wiki = lambda page: '/wiki/' + page
get_html = lambda page: internet.get_page(wiki(page))
pages = ['Peru', 'Git', 'Adolf_Hitler', 'Mao_Zedong',  'United_Nations',  'Brazil', 'Altoids']


if __name__ == '__main__':
    allCombinations = list(permutations(pages, 2))
    for combination in allCombinations:
        racer = WikiracerProblem()
        path = racer.wikiracer(source=r'/wiki/'+combination[0], goal=r'/wiki/'+combination[1])
        print(combination, len(racer.internet.requests))


'''
('Peru', 'Git') 45
('Peru', 'Adolf_Hitler') 5
('Peru', 'Mao_Zedong') 3
('Peru', 'United_Nations') 1
('Peru', 'Brazil') 1
('Peru', 'Altoids') 35
('Git', 'Peru') 17
('Git', 'Adolf_Hitler') 7
('Git', 'Mao_Zedong') 11
('Git', 'United_Nations') 9
('Git', 'Brazil') 7
('Git', 'Altoids') 13
('Adolf_Hitler', 'Peru') 5
('Adolf_Hitler', 'Git') 33
('Adolf_Hitler', 'Mao_Zedong') 1
('Adolf_Hitler', 'United_Nations') 3
('Adolf_Hitler', 'Brazil') 3
('Adolf_Hitler', 'Altoids') 27
('Mao_Zedong', 'Peru') 1
('Mao_Zedong', 'Git') 23
('Mao_Zedong', 'Adolf_Hitler') 1
('Mao_Zedong', 'United_Nations') 3
'''