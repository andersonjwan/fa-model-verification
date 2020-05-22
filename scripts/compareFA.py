#!/usr/bin/env python3.7

# module(s)
import sys
from itertools import chain, combinations, product
from parseJFLAP import *

# algorithm defined in more-itertools
def powerSet(mainSet):
    s = list(mainSet)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

def buildState(mainTuple):
    sortedTuple = sorted(mainTuple)
    state = str()

    for member in sortedTuple:
        state = state + member

    return state

def computeStates(nfa):
    states = list(powerSet(nfa.states))
    return states

    result = set()

    for member in states:
        tempState = tuple()

        for tupleMember in member:
            tempState = tempState + (tupleMember, )

        result.add(buildState(tempState))

    print(result)
    return result

def computeStateTransition(stateTuple, dfaTransitions, alphabet):
    newTrans = dict()

    for symbol in alphabet:
        destination = tuple()

        for member in stateTuple:
            # iterate through states in state set
            for state, stateTrans in dfaTransitions.items():
                if member == state:
                    if symbol in stateTrans:
                        for element in stateTrans[symbol]:
                            if element not in destination:
                                destination = destination + (element, )

        newTrans[symbol] = destination

    return newTrans

def computeTransitions(nfa, states):
    dfaTransitions = dict()
    transitions = nfa.transitions

    # initialize transition
    for state in states:
        dfaTransitions[state] = dict()

    # build from previous states
    for state, stateTrans in transitions.items():
        newTrans = dict()

        if stateTrans:
            # dictionary not empty
            for symbol, symbolTrans in stateTrans.items():
                toState = tuple()

                for symbolState in symbolTrans:
                    toState = toState + (symbolState, )

                # symbol built
                newTrans[symbol] = toState

        dfaTransitions[state] = newTrans

    # build from new states
    for stateTuple, stateTrans in dfaTransitions.items():
        if isinstance(stateTuple, tuple):
            newTrans = computeStateTransition(stateTuple, dfaTransitions, nfa.input_symbols)

            # add new transitions to state
            if dfaTransitions[stateTuple]:
                # dictionary is not empty
                dfaTransitions[stateTuple].update(newTrans)
            else:
                dfaTransitions[stateTuple] = newTrans

    return dfaTransitions

def computeFinalStates(nfa, dfaStates):
    finals = set()

    # add base final states
    for state in nfa.final_states:
        finals.add(state)

    for state in nfa.final_states:
        for dfaState in dfaStates:
            if state in dfaState:
                finals.add(buildState(dfaState))

    return finals

def NFAtoDFA(nfa):
    dfaStates = list()
    dfaSymbols = set()
    dfaTransitions = dict()

    # build the set of states
    dfaStates = computeStates(nfa)

    # set the symbols
    dfaSymbols = nfa.input_symbols

    # set transitions
    dfaTransitions = computeTransitions(nfa, dfaStates)

    # set initial state
    dfaInitialState = nfa.initial_state

    # set final state
    dfaFinalStates = computeFinalStates(nfa, dfaStates)

    # format states
    formatStates = set()
    for member in dfaStates:
        formatStates.add(buildState(member))

    formatTransitions = dict()

    # initialize keys
    for state, stateTrans in dfaTransitions.items():
        if isinstance(state, tuple):
            tempTrans = dict()
            for symbol, symbolTrans in stateTrans.items():
                tempTrans[symbol] = buildState(symbolTrans)

        if isinstance(state, tuple):
            formatTransitions[buildState(state)] = tempTrans

    # build DFA
    dfa = DFA(
        states = formatStates,
        input_symbols = dfaSymbols,
        transitions = formatTransitions,
        initial_state = dfaInitialState,
        final_states = dfaFinalStates
    )

    return dfa

def to_complement(dfa):
    accepted = set()
    rejected = set()

    # build accepted states set
    for state in dfa.final_states:
        accepted.add(state)

    # build rejected state set
    for state in dfa.states:
        if state not in dfa.final_states:
            rejected.add(state)

    # build complement DFA
    comp_dfa = DFA(
        states = dfa.states,
        input_symbols = dfa.input_symbols,
        transitions = dfa.transitions,
        initial_state = dfa.initial_state,
        final_states = rejected
    )

    return comp_dfa

def remove_braces(string):
    result = str()

    for character in string:
        if character != '{' and character != '}':
            result = result + character

    return "{" + result + "}"

def cross_states(spc_states, sys_states):
    states = list()

    for state in product(spc_states, sys_states):
        if state not in states:
            states.append(state)

    # remove repeating sets
    size = len(states)
    for i in range(0, size):
        for j in range(i, size):
            if i != j and set(states[i]).issubset(states[j]):
                states.remove(states[i])
                size = size - 1
                break # break second for loop (nested)

    # add deadlock state
    states.append(("{}", "{}"))

    # build set
    result = set()
    for state in states:
        # build string
        temp = str()

        for member in state:
            temp = temp + member

        # add string to set
        result.add(temp)

    return result

def cross_transitions(spc_trans, sys_trans, states):
    transitions = dict()

    # build base dictionary
    for state in states:
        transitions.update({state: None})

    # build transitions
    for spc_key, spc_val in spc_trans.items():
        for spc_val_key, spc_val_val in spc_val.items():
            for sys_key, sys_val in sys_trans.items():
                temp_trans = dict()
                for sys_val_key, sys_val_val in sys_val.items():
                    if spc_val_key == sys_val_key:
                        temp_trans[spc_val_key] = spc_val_val + sys_val_val

                # add transition functions to state
                if transitions[spc_key + sys_key] != None:
                    transitions[spc_key + sys_key] = {**(transitions[spc_key + sys_key]), **temp_trans}
                else:
                    transitions[spc_key + sys_key] = temp_trans

    return transitions

def cross_finals(spc_finals, sys_finals):
    finals = set()

    for spc_state in spc_finals:
        for sys_state in sys_finals:
            finals.add(spc_state + sys_state)

    return finals

def to_intersection(spc_dfa, sys_dfa):
    # build cartesian product of states
    inter_states = cross_states(spc_dfa.states, sys_dfa.states)

    # build transitions
    inter_transitions = cross_transitions(spc_dfa.transitions, sys_dfa.transitions, inter_states)

    # set initial state
    inter_initial = spc_dfa.initial_state + sys_dfa.initial_state

    # set final states
    inter_finals = cross_finals(spc_dfa.final_states, sys_dfa.final_states)

    # build intersection DFA
    inter_dfa = DFA(
        states = inter_states,
        input_symbols = spc_dfa.input_symbols,
        transitions = inter_transitions,
        initial_state = inter_initial,
        final_states = inter_finals
    )

    return inter_dfa

def convert_graph(comp):
    graph = dict()

    # build base state(s)
    for state in comp.transitions:
        graph.update({state: list()})

    # add transition state(s)
    for state in graph:
        for key, value in comp.transitions.items():
            if(state == key):
                for curr_key, curr_val in value.items():
                    graph[state].append({curr_key: curr_val})

    return graph


# find_path method implementation used from
# https://www.python.org/doc/essays/graphs/
# with some variation

def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not start in graph:
        return None
    for trans, node in graph[start].items():
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath:
                return newpath

    return None

def path_to_string(path, dfa):
    string = ""

    if len(path) > 1:
        for i in range(len(path) - 1):
            state = path[i]
            transitions = dfa.transitions[state]

            for symbol in transitions:
                if transitions[symbol] == path[i + 1]:
                    string = string + symbol
    else:
        string = "EPS"

    return string

def write_DFA(dfa, filename):
    with open(filename, "w") as f:
        f.write("% Input alphabet\n")

        for symbol in dfa.input_symbols:
            f.write(symbol + '\n')

        f.write("% Intersectional Language\n")

        f.write("% Transition function\n")
        for state, transitions in dfa.transitions.items():
            for symbol, toState in transitions.items():
                f.write(state + " " + symbol + " " + toState + "\n")

        f.write("% Initial state\n")
        f.write(dfa.initial_state + '\n')

        f.write("% Final states\n")
        for state in dfa.final_states:
            f.write(state + '\n')

def rename_deadlocks(dfa):
    replacement = "{}"

    if "" in dfa.states:
        dfa.states.add(replacement)
        dfa.states.remove("")

    for state, transitions in dfa.transitions.items():
        for symbol in transitions:
            if transitions[symbol] == "":
                transitions[symbol] = replacement

    if "" in dfa.transitions.keys():
        dfa.transitions[replacement] = dfa.transitions.pop("")

def is_subset(spec, sys):
    # find the complement of the first automaton
    comp_automaton = to_complement(spec)

    # find the intersection of the complement and system automaton
    inter_automaton = to_intersection(comp_automaton, sys)

    # convert transitions to graph
    inter_graph = convert_graph(inter_automaton)

    # find shortest path to accepting state
    for final_state in inter_automaton.final_states:
        path = find_path(inter_automaton.transitions, inter_automaton.initial_state, final_state)

        if(path != None):
            break;

    if path != None:
        result = path_to_string(path, inter_automaton)
    else:
        result = None

    return result

def main(args):
    # read the arguments
    if(len(args) > 2):
        specAutomata = args[1]
        systemAutomata = args[2]

        spc_nfa = parseFA(specAutomata, 'q')
        sys_nfa = parseFA(systemAutomata, 's')

        # convert specification automaton to DFA
        spc_dfa = NFAtoDFA(spc_nfa)
        sys_dfa = NFAtoDFA(sys_nfa)

        # rename deadlock state
        rename_deadlocks(spc_dfa)
        rename_deadlocks(sys_dfa)

        sys_result = is_subset(spc_dfa, sys_dfa)
        spc_result = is_subset(sys_dfa, spc_dfa)

        if sys_result == None and spc_result == None:
            print("PASS" + ";" + "None" + ";" "None", end='')
        elif sys_result == None and spc_result != None:
            print("FAIL" + ";" + spc_result + ";" + "None", end='')
        elif sys_result != None and spc_result == None:
            print("FAIL" + ";" + "None" + ";" + sys_result, end='')
        elif sys_result != None and spc_result != None:
            print("FAIL" + ";" + spc_result + ";" + sys_result, end='');
        else:
            print("FAIL" + ";" + "None" + ";" + "None", end='')

main(sys.argv)
