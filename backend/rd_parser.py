#  backend/rd_parser.py  - ad-hoc recursive-descent syntactic parser for Korean sentences
#
#
__author__ = 'jwainwright'

import functools, re, sys
from io import StringIO
from collections import defaultdict

#  This is an alternative to the nltk chunking approach, allowing more contextual control over parsing
#
# The high-level sentence structure will roughly be as follows:
#
#  sentence ::=  [subordinateClause]* mainClause
#  mainClause ::= clause SENTENCE_END
#  subordinateClause ::= clause CLAUSE_CONNECTOR
#  clause ::= [phrase]* verbPhrase
#

class Terminal(object):
    "wraps lexical terminal token"


class Lexer(object):
    "lexical analyzer wraps morhpheme:POS list from KHaiii analyzer, doing any needed lexixcal transformation & providing token-by-token access"

    def __init__(self, posList):   # in the form ['phoneme:POStag', ,...]
        self.posList = posList
        self.cursor = 0
        self.lexer = None
        self.lastTriedToken = None

    # -------- parser API ---------

    def next(self, tokenPat=None):
        "yields and consumes next token (as a terminal node), or fails if tokenPat supplied and next token doesn't match"
        node = self.peek(tokenPat)
        if node:
            self.cursor += 1
        return node

    def peek(self, tokenPat=None):
        "yields but doesn't consume next token"
        token = self.posList[self.cursor]
        self.lastTriedToken = token
        if tokenPat and not re.fullmatch(tokenPat, token):
            return None
        #
        return [ParseTree('terminal', token, self.cursor, self.cursor, self, None)]

    def last(self):
        "yields last token again"

    def mustBe(self, tokenPat):
        "yields & consumes next token if it matches give pattern, else doesn't consome & returns None"

    def backTrack(self, token):
        "backtracks over given token"

    def mark(self):
        "return marker for current lexical progress"
        # for now, just the phoneme:tag tuple cursor
        return self.cursor

    def backTrackTo(self, marker):
        "backracks lexer state to given marker"
        # for now, just restore cursor
        self.cursor = marker

class ParseTree(object):
    "nodes in the result of a parse"

    nullNode = None

    def __init__(self, type, label, startMark, endMark, lexer, notes=''):
        self.type = type
        self.label = label
        self.startMark, self.endMark = startMark, endMark
        self.lexer = lexer
        self.notes = notes
        #
        self.children = []

    # def __repr__(self):
    #     return '{0}: {1} [{2}]'.format(self.type, self.label, ', '.join(c.label for c in self.children if not c.isEmpty()))

    def __repr__(self):
        return '{0}{1}'.format(self.label,
                               " [{0}]".format(', '.join(c.__repr__() for c in self.children)) if not self.isEmpty() else "")

    def append(self, node):
        "adds child node"
        self.children.append(node)

    def insert(self, index, node):
        "inserts child node before given index"

    def delete(self, index):
        "deletes indexed child"

    def length(self):
        "return count of child nodes"
        return len(self.children)

    def terminalSpan(self):
        "return number of terminal symbols this node & it's sub-tree covers"
        return self.endMark - self.startMark

    def isLeaf(self):
        return self.type == 'terminal'

    def word(self):
        assert self.isLeaf()
        return self.label.split(':')[0]

    def tag(self):
        assert self.isLeaf()
        return self.label.split(':')[-1]

    def isSubtree(self):
        return self.type != 'terminal'

    def isEmpty(self):
        return len(self.children) == 0

    def pprint(self, level=0, closer='', file=sys.stdout):
        indent = '  ' * level
        if self.isEmpty():
            print(indent + self.label + closer, file=file)
        else:
            print(indent + self.label + ' (', file=file)
            for c in self.children:
                c.pprint(level + 1, closer + (')' if c == self.children[-1] else ''), file=file)

    def mapNodeNames(self):
        "maps ParseTree node names under tag-mapping 'nodeRename' definitions"
        #
        def camelCaseSpacer(label):
            matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', label)
            return ' '.join(m.group(0) for m in matches)
        #
        from tagmap import TagMap
        #
        def walkTree(t, parentList):
            # walk tree looking for terminal nodes with tags that are in the nodeNameMap table
            #   search up for ancestor node with label in the above-selected nodeNameMap entry, taking label rename
            for i, st in enumerate(t.children):
                if st.isSubtree():
                    st.label = camelCaseSpacer(st.label)
                    walkTree(st, [st] + parentList)
                else:
                    nm = TagMap.nodeNameMaps.get(st.tag())
                    if nm:
                        # we have a terminal node for a synthetic tag, run up parents looking for the map's old label
                        for p in parentList:
                            if p.label in nm:
                                # found matching parent node, rename node
                                p.label = nm[p.label]
                                return
        #
        walkTree(self, [self])

    def getReferences(self):
        "traverse Parseree for reference link defs"
        #
        references = {}
        wikiKeys = {}
        posTable = {}
        ruleAnnotations = {}
        #
        from chunker import Chunker
        from tagmap import TagMap
        #
        def walkTree(t):
            # walk tree looking for terminal nodes with tags that are in the refMap or wikiKey tables & build reference items
            for i, st in enumerate(t.children):
                if st.isSubtree():
                    # add any tree node grammar rule annotations & refs
                    tag = st.label
                    annotation = Chunker.ruleAnnotations.get(tag)
                    if annotation:
                        ruleAnnotations[tag] = dict(descr=annotation['descr'],
                                                    refList=TagMap.getRefsMapEntries(annotation['refs']))
                    # recurse down th etree
                    walkTree(st)
                else:
                    refList = []
                    wk = TagMap.wikiKeyMap.get(st.tag())
                    if wk != "none":
                        if wk:
                            word = wk
                        else:
                            word = (st.word() + '다') if st.tag()[0] == 'V' and st.tag()[-1] != '다' else st.word()
                        # add dictionary links
                        for d in TagMap.dictionaries:
                            refList.append(dict(title=d['title'], slug=d['slug'].replace("${word}", word)))
                        #
                        wikiKeys[st.word()] = word
                    #
                    refs = TagMap.refsMap.get(st.tag())
                    if refs:
                        refList.extend(refs)
                    if refList:
                        references[st.word()] = refList
                    # add POS reference table entries
                    posEntry = {}
                    tm = TagMap.tagMappings.get(st.tag())
                    if tm:
                        posEntry['notes'] = tm.notes
                    posDef = TagMap.partsOfSpeech.get(st.tag())
                    if posDef:
                        posEntry['wikiPOS'] = posDef[0]
                        posEntry['descr'] = posDef[2]
                    posTable[st.tag()] = posEntry
        #
        walkTree(self)
        #
        return dict(references=references, wikiKeys=wikiKeys, posTable=posTable, ruleAnnotations=ruleAnnotations, )

    def phraseList(self):
        "generates phrase list from given ParseTree"
        # generate phrase-descriptors from top-level subtrees
        hiddenTags = { 'Substantive', 'Constituent', 'NounPhrase', 'Connection', }
        def flattenPhrase(t, phrase):
            for st in t.children:
                if st.isSubtree():
                    phrase = flattenPhrase(st, phrase)
                    if st.label not in hiddenTags:
                        phrase.append({"type": 'tree', "tag": st.label})
                else:
                    phrase.append({"type": 'word', "word": st.word().strip(), "tag": st.tag()})
            return phrase
        #
        phrases = []
        for t in self.children:
            if t.isSubtree():
                phrase = flattenPhrase(t, [])
                if t.label not in hiddenTags:
                    phrase.append({"type": 'tree', "tag": t.label})
                phrases.append(phrase)
            else:
                phrases.append({"type": 'word', "word": t.word().strip(), "tag": t.tag()})
        #
        return phrases

    def buildParseTree(self, wordDefs={}, showAllLevels=False):
        "constructs display structures from parse-tree"
        # first, recursively turn the parse tree into a Python nested dict so it can be JSONified
        #  gathering terminals list & adding level from root & parent links along the way
        terminals = []; height = [0]; allNodes = []; nodeIDs = {}
        #
        from tagmap import TagMap
        #
        def asDict(st, parent=None, level=0, isLastChild=True):
            height[0] = max(height[0], level)
            if not showAllLevels:
                # elide degenerate tree nodes (those with singleton children)
                while st.isSubtree() and st.length() == 1:
                    st = st.children[0]
            if st.isSubtree():
                # build subtree node
                tag = st.label
                # ad-hoc label mappings
                if tag == 'S' or level == 0 and tag == 'Main Clause':
                    tag = 'Sentence'
                elif level == 0 and tag == 'Stand Alone Phrase':
                    tag = 'Phrase'
                elif tag == 'Predicate' and not isLastChild:
                    tag = 'Verb Phrase'
                # build tree node
                node = dict(type='tree', tag=tag, level=level, layer=1, parent=parent)
                node['children'] = [asDict(c, node, level+1, isLastChild=i == st.length()-1) for i, c in enumerate(st.children)]
                nodeID = nodeIDs.get(id(node))
                if not nodeID:
                    nodeIDs[id(node)] = nodeID = len(nodeIDs) + 1
                node['id'] = nodeID
                allNodes.append(node)
                return node
            else:
                # build terminal node
                word = st.word().strip()
                tag = st.tag()
                tm = TagMap.POS_labels.get(word + ":" + tag)
                tagLabel = (tm.posLabel if tm else TagMap.partsOfSpeech.get(tag)[0]).split('\n')
                # add word definition for nouns & verbs if available
                if tag[0] in ('V', 'N', 'M') and word in wordDefs:
                    tagLabel.append(wordDefs[word])
                node = dict(type='word', word=word, tag=tag, tagLabel=tagLabel, children=[], parent=parent, level=-1, layer=0)
                nodeID = nodeIDs.get(id(node))
                if not nodeID:
                    nodeIDs[id(node)] = nodeID = len(nodeIDs) + 1
                node['id'] = nodeID
                terminals.append(node)
                allNodes.append(node)
                return node
        tree = asDict(self)

        # breadth-first traversal up from terminals to set layer-assignemnt for each node
        nodes = list(terminals)
        maxLayer = 0
        while nodes:
            parents = []
            for n in nodes:
                parent = n['parent']
                if parent:
                    parent['layer'] = max(n['layer'] + 1, parent['layer'])
                    maxLayer = max(maxLayer, parent['layer'])
                    parents.append(parent)
            nodes = list(parents)

        # add nodes to their assigned layer, drop parent field circular refs so structures can be JSONified
        layers = [list() for i in range(maxLayer + 1)]
        for n in allNodes:
            layers[n['layer']].append(n['id'])
            n['parent'] = nodeIDs[id(n['parent'])] if n['parent'] else None
        #
        return dict(tree=tree, layers=layers)


ParseTree.nullNode = ParseTree('null', 'null', 0, 0, None)

# --------------  utility grammar-definition functions ---------------

# define the main decorator for grammar-rule methods on Parser subclasses
#   automatically handles dynamic-programming caching & backtracking
def grammarRule(rule):
    #
    @functools.wraps(rule)
    def backtrack_wrapper(self, *args, **kwargs):
        indent = '  ' * len(self.recursionState)
        startMark = self.lexer.mark()
        startToken = self.lexer.peek()
        # check already-parsed cache
        priorParse =  self.parsedPhraseCache.get((rule, startMark))
        if priorParse:
            # found prior parsing of requested rule at this phoneme, push lexer past prior parsing & return prior parsing
            parsing, endMark = priorParse
            self.lexer.backTrackTo(endMark)
            # if self.verbose > 0:
            #     traceBack = " -> ".join(r.__name__ for r, m in reversed(self.recursionState))
            #     self.log(indent, '* found', parsing[0], 'at', startToken, traceBack)
            return parsing
        #
        if self.verbose > 1:
            self.log(indent, '--- at ', self.lexer.posList[self.lexer.cursor], 'looking for ', rule.__name__)
        # recursion into the same rule at the same token implies match failure (for now).  Recursive rules should generally be right-recursive.
        if (rule, startMark) in self.recursionState:
            if self.verbose > 2:
                self.log(indent, '    recursion on same token encountered, failing')
            parsing = []
        else:
            # track recursion
            self.recursionState.append((rule, startMark))

            # actually apply the grammar rule function
            result = rule(self, *args, **kwargs)

            self.recursionState.pop(-1)

            # make a ParseTree node for the result, backtracking on rule failure (empty result)
            node = self.makeNode(rule.__name__, startMark, result)
            if not node:
                self.fails[startMark].add(rule) # note we failed this production at this point to break later recursive attempts at same thing
                self.lexer.backTrackTo(startMark)
                if self.verbose > 2:
                    self.log(indent, '    nope, backtracking to ', self.lexer.posList[self.lexer.cursor])
                parsing = []
            else:
                traceBack = " -> ".join(r.__name__ for r, m in reversed(self.recursionState))
                if self.verbose > 0:
                    self.log(indent, '* found', node, 'at', startToken, traceBack)
                parsing = [node]
                # cache parse result & it's end-mark
                self.parsedPhraseCache[(rule, startMark)] = (parsing, self.lexer.mark())
        #
        #
        return parsing
    #
    return backtrack_wrapper

# ----------- rule construction helper functions --------------

def eval(rule):
    "evaluate rule, either a parser rule method or ParseTree node"
    return rule() if callable(rule) else rule

def optional(rule):
    "marks the rule as optional, zero or one instances"
    return eval(rule) or [ParseTree.nullNode]

def option(rule):
    "wraps alternates in anyOneOf rules"
    result = eval(rule)
    yield result

def anyOneOf(*options):
    """match the longest match of the options supplied.
      Note that each option MUST BE a rule wrapped in the option() generator in order to ensure correct evaluation"""
    # eager match: eval all options, take the longest matching
    longest = None; length = 0
    for i, o in enumerate(options):
        node = o.__next__()
        if node and not all(n == ParseTree.nullNode for n in node):
            l = sum(n.terminalSpan() for n in node)
            if not longest or l > length:
                longest, length = node, l
            # restart matching
            first = [n for n in node if n != ParseTree.nullNode][0]
            first.lexer.backTrackTo(first.startMark)
    #
    if longest:
        # seek to end of selected longes match
        seq = [n for n in longest if n != ParseTree.nullNode]
        seq[0].lexer.backTrackTo(seq[-1].endMark)
        return longest

def oneOrMore(rule):
    "one or more instances of the rule"
    nodes = []
    while True:
        node = eval(rule)
        if node and node[0] != ParseTree.nullNode:
            nodes.extend(node)
        if not node or not callable(rule):
            break

    return nodes

def zeroOrMore(rule):
    "zero or more instances of the rule"
    return rule and oneOrMore(rule) or [ParseTree.nullNode]

def sequence(*rules):
    """an ordered sequence of rule calls.
       Note that the argument rules MUST ALL be invocations of other helper functions above OR a call of a bare rule
       in order to ensure correct order of sequence matching"""
    nodes = []
    for r in rules:
        node = eval(r)
        if node:
            nodes.extend(node)
        else:
            # any miss fails whole seq
            return []
    return nodes

# ---------------

class Parser(object):
    """Performs ad-hoc recursive descent of a given sentence POS-list.
       Subclasses usually provide grammar rule methods and at least a 'sentence' rule method to start the parsing."""

    def __init__(self, posList):
        self.posList = posList
        self.lexer = Lexer(posList)
        self.fails = defaultdict(set)  # tracks history of failed profuctions at each cursor position to break recursions
        self.recursionState = []  # tracks recursion state to break recursive rules
        self.parsedPhraseCache = {}
        self.logIO = StringIO()
        #
        self.log('Input posList:', posList)
        self.log('\nParse log:')

    def mark(self):
        "return marker for current parsing state"
        # for now, just lexer state
        return self.lexer.mark()

    def backTrackTo(self, marker):
        "backtrack parsing to state indicate by given marker"
        # for now, just back-tracks lexer
        self.lexer.backTrackTo(marker)

    @grammarRule
    def unrecognized(self):
        "in case of parse-failure under grammar, produce degenerate parse just of all terminals in sentence"
        # allows lexical analysis display, at least
        self.lexer.backTrackTo(0)
        nodes = []
        while not self.lexer.peek(r'.*:SF.*'):
            nodes.extend(self.lexer.next())
        return nodes

    def parse(self, verbose=0):
        "begin parse, return ParseTree root node"
        self.verbose = verbose
        #
        parsing = self.input()
        # check
        result = {}
        if not parsing:
            # failed altogether, signal but gather degenerate "parse" of all terminals
            self.log('\n*** parse failed')
            result['error'] = "Sorry, failed to parse sentence"
            result['parseTree'] = self.unrecognized()[0]
        #
        elif not self.lexer.peek(r'.*:SF.*'):
            # early termination, signal but gather degenerate "parse" of all terminals
            result['error'] = "Sorry, incomplete parsing"
            self.log('\n*** incomplete parsing, last tried token = ', self.lastTriedToken().__repr__())
            self.log('\nPartial parseTree:\n'); parsing[0].pprint(file=self.logIO)
            result['parseTree'] = self.unrecognized()[0]
        #
        else:
            # all good
            parsing[0].pprint(file=self.logIO)
            result['parseTree'] = parsing[0]
        #
        result['log'] = self.logIO.getvalue()
        return result

    def log(self, *args):
        "log a trace or error msg"
        # out to both stdout and the log buffer
        print(*args)
        print(*args, file=self.logIO)

    def makeNode(self, label, startMark, constituents):
        "makes a node with given label & constituents as children"
        label = label[0].capitalize() + label[1:]
        nn = ParseTree('node', label, startMark, self.lexer.mark(), self.lexer)
        constituents = constituents if type(constituents) == list else [constituents]
        for c in constituents:
            if c and c != ParseTree.nullNode:
                nn.append(c)
        return None if nn.isEmpty() else nn

    def lastTriedToken(self):
        return self.lexer.lastTriedToken

if __name__ == "__main__":
    #
    posList = [('저', 'MM'),
             ('작', 'VA'),
             ('은', 'ETM'),
             ('소년', 'NNG'),
             ('의', 'JKG'),
             ('남동생', 'NNG'),
             ('은', 'TOP_6'),
             ('밥', 'NNG'),
             ('을', 'JKO'),
             ('먹', 'VV'),
             ('다', 'EF'),
             ('.', 'SF')]

    p = Parser([":".join(p) for p in posList])
    p.parse()














