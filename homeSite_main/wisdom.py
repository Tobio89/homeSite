import os, random

basedir = os.path.abspath(os.path.dirname(__file__))

def getWisdom():
    wisPath = os.path.join(basedir, '.\static\wisdomSlices')
    pearls = [txtFile for txtFile in os.listdir(wisPath) if txtFile.endswith('.txt')]
    randomPearl = random.choice(pearls)

    with open(os.path.join(wisPath, randomPearl),  'r') as pearlFile:
        pearlText = pearlFile.read()
    return pearlText