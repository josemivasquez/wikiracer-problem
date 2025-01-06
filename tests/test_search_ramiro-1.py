from itertools import chain, combinations
from py_wikiracer.wikiracer import Parser, WikiracerProblem
from py_wikiracer.internet import Internet

def test_wikiracer_multiple():
    pages = ['Jesus', 'Adolf_Hitler','Mao_Zedong','Johnny_Damon','Chicago_Blackhawks','United_Nations','Madonna','Brazil','Home_Depot','Altoids']

    allCombinations = list(combinations(pages,2))
    paths = []
    
    for combination in allCombinations:
        racer = WikiracerProblem()
        paths.append(racer.wikiracer(source=r'/wiki/'+combination[0], goal=r'/wiki/'+combination[1]))
        print(combination, len(racer.internet.requests))

    for i, path in enumerate(paths):
        print(f"\n####### {i} #######")
        source = path.pop(0)
        print(source)
        while len(path) > 0:
            destination = path.pop(0)
            print(destination)
            links = Parser.get_links_in_page(Internet().get_page(source))
            assert destination in links
            source = destination
        print(f"#################\n")
