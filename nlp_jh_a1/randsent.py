import random
import bisect
import sys

class GrammarRule:

    def __init__(self, key):
        self.key = key
        self.derivations = []
        self.sumOfDerivationWeights = 0

    def isTerminal(self):
        return len(self.derivations) == 0

    # Each derivation is an array of rules
    def addDerivation(self, derivation):
        self.derivations.append(derivation)
        self.sumOfDerivationWeights = self.sumOfDerivationWeights + derivation.weight

    def chooseRandomDerivation(self):
        cdfValues = []
        cumulativeSum = 0

        for derivation in self.derivations:
            cumulativeSum = cumulativeSum + derivation.weight
            cdfValues.append(cumulativeSum / self.sumOfDerivationWeights)

        randomInteger = random.random()
        choiceIndex = bisect.bisect(cdfValues, randomInteger)
        return self.derivations[choiceIndex]

    def generateSentence(self):
        if self.isTerminal() == True:
            return self.key

        sentence = ""
        derivation = self.chooseRandomDerivation()
        for rule in derivation.rules:
            sentence += rule.generateSentence() + " "

        return sentence

class Derivation:
    def __init__(self, ruleDict, ruleKeys, weight):
        """
            ruleDict is a dictionary which stores rules already defined in the
            grammar to which the derivation being constructed belongs

            ruleKeys is an array of keys of the rules which make up the
            derivation being constructed

            weight is the weight assigned to the given rules which defines
            the relative probability of this derivation being randomly chosen
            from amongst all derivations for the rule from which the
            derivation is derivable
        """
        self.weight = weight
        self.rules = []
        for key in ruleKeys:
            if key in ruleDict:
                rule = ruleDict[key]
            else:
                rule = GrammarRule(key)
                ruleDict[key] = rule
            self.rules.append(rule)


START_SYMBOL_KEY = "ROOT"
COMMENT_SYMBOL = "#"

def validateTokens(tokens, lineno):
    if len(tokens) < 3:
        print("[{}] Syntax error: invalid number of tokens".format(lineno))
        sys.exit(1)
    try:
        weight = float(tokens[0])
        if weight <= 0.:
            print("[{}] Syntax error: Derivation weight must greater than 0".format(lineno))
            sys.exit(1)
    except ValueError:
        print("[{}] Syntax error: First token on line must be derivation weight".format(lineno))
        sys.exit(1)

def parseTokens(line):
    """
        Pre: the first token in the line is not the comment token
    """
    line.strip()
    commentTokenIdx = line.find(COMMENT_SYMBOL)
    if commentTokenIdx != -1:
        line = line[:commentTokenIdx-1]
    return line.split()

def parseLine(ruleDict, line, lineno):
    if line == "" or line[0] == COMMENT_SYMBOL:
        return

    tokens = parseTokens(line)
    print("{}: {}".format(lineno, tokens))
    validateTokens(tokens, lineno)
    weight = float(tokens[0])
    key = tokens[1]
    rules = tokens[2:]
    derivation = Derivation(ruleDict, rules, weight)
    ruleDict[key].addDerivation(derivation)

def generateGrammar(grammarFile):
    ruleDict = {}
    ruleDict[START_SYMBOL_KEY] = GrammarRule(START_SYMBOL_KEY)

    try:
        with open(grammarFile) as f:
            lineno = -1
            for line in f:
                lineno = lineno + 1
                line = line.strip()
                parseLine(ruleDict, line, lineno)

            f.close()
            return ruleDict
    except IOError:
        print("Could not open grammar file.")
        usage()
        sys.exit(1)

def main(argv):
    if len(argv) != 2 or int(argv[1]) <= 0:
        usage()

    grammarFile = argv[0]
    try:
        sentenceCount = int(argv[1])
    except ValueError:
        usage()
        sys.exit(1)

    ruleDict = generateGrammar(grammarFile)

    for i in range(0, sentenceCount):
        print(ruleDict[START_SYMBOL_KEY].generateSentence())

def usage():
    print("Usage: ./randsent path/to/grammar/file number_of_sentences_to_generate")
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])


