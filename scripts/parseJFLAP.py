import xml.etree.ElementTree as ET

# automata modules
from automata.base.automaton import Automaton
from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

def addUnique(targetSet, targetMember):
    if targetMember not in targetSet:
        targetSet.add(targetMember)

def parseStates(automataTree, prefix):
    states = set()
    root = automataTree.find('automaton')

    # iterate through states and extract id's
    for state in root.findall('state'):
        name = prefix + state.get('id')

        # attempt to add name to set
        addUnique(states, name)

    return states

def parseAlphabet(automataTree):
    symbols = set()
    root = automataTree.find('automaton')

    # iterate through transitions and extract symbol(s)
    for transition in root.findall('transition'):
        symbol = transition.find('read').text

        if symbol == None:
            symbol = "EPSILON"

        # attempt to add symbol to set
        addUnique(symbols, symbol)

    return symbols

def parseTransitions(automataTree, states, prefix):
    transitions = dict()
    root = automataTree.find('automaton')

    # initialize dictionary
    for state in states:
        transitions[state] = dict()

    # iterate through transitions and build dictionary
    for transition in root.findall('transition'):
        tempTrans = dict()

        # collect transition information
        transKey = prefix + transition.find('from').text
        tempTransKey = transition.find('read').text
        tempTransValue = prefix + transition.find('to').text

        if tempTransKey == None:
            tempTransKey = "EPSILON"

        # add transition to transitions
        if transitions[transKey] != None:
            if tempTransKey not in transitions[transKey]:
                # first symbol occurence
                tempSet = set()
                addUnique(tempSet, tempTransValue)

                tempTrans[tempTransKey] = tempSet
                transitions[transKey].update(tempTrans)
            else:
                # same symbol, different to state
                addUnique(transitions[transKey][tempTransKey], tempTransValue)
        else:
            # build transition
            tempSet = set()
            addUnique(tempSet, tempTransValue)

            tempTrans[tempTransKey] = tempSet
            transitions[transKey] = tempTrans

    return transitions

def parseInitialState(automataTree, prefix):
    initial = str()
    root = automataTree.find('automaton')

    # iterate through states and find initial
    for state in root.findall('state'):
        if state.find('initial') != None:
            initial = prefix + state.get('id')

    return initial

def parseFinalStates(automataTree, prefix):
    finals = set()
    root = automataTree.find('automaton')

    # iterate through states and find finals
    for state in root.findall('state'):
        if state.find('final') != None:
            # add state to set
            final = prefix + state.get('id')
            addUnique(finals, final)

    return finals

def parseFA(fileJFLAP, prefix):
    # create tree object
    automataTree = ET.parse(fileJFLAP)

    # parse states
    parsedStates = parseStates(automataTree, prefix)

    # parse alphabet
    parsedAlphabet = parseAlphabet(automataTree)

    # parse transitions
    parsedTransitions = parseTransitions(automataTree, parsedStates, prefix)

    # parse initial state
    parsedInitial = parseInitialState(automataTree, prefix)

    # parse final states
    parsedFinals = parseFinalStates(automataTree, prefix)

    # build NFA
    nfa = NFA(
        states = parsedStates,
        input_symbols = parsedAlphabet,
        transitions = parsedTransitions,
        initial_state = parsedInitial,
        final_states = parsedFinals
    )

    return nfa
