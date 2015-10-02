import re
from sys import stdin

NULL = 'E'

# Transitions are represented by nested key value pairs: the first key is the
# start state, the second key is the symbol to follow, the value is a list of
# resulting states. For example, transitions[2]['a'] will be a list of
# integers representing the states reachable from state 2 on input 'a'.

class FiniteAutomaton:
    def __init__(self, initial_state, transitions, final_states, alphabet):
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.alphabet = alphabet

    def null_closure(self, states):
        """Get states reachable from states along NULL transition"""
        closure = list(states)
        unchecked = list(states)
        while unchecked:
            state = unchecked.pop()
            null_transitions = self.move([state], NULL)
            for transition in null_transitions:
                if transition not in closure:
                    closure.append(transition)
                    unchecked.append(transition)
        closure.sort()
        return closure

    def move(self, states, symbol):
        """Get states reachable from input states with symbol input"""
        destinations = set()
        for state in states:
            # get reachable states- default to empty dictionary
            transitions = self.transitions.get(state, dict())
            destinations.update(transitions.get(symbol, []))
        return list(destinations)

    def add_transition(self, start, symbol, end):
        if start not in self.transitions:
            # no transitions from this state yet, add to dictionary
            self.transitions[start] = {symbol: [end]}
        elif symbol not in self.transitions[start]:
            # no transitions from this state along this symbol yet, add
            # list with single end state along this symbol
            self.transitions[start][symbol] = [end]
        else:
            # There are already transitions from this state along this input,
            # Append this end state to the list
            self.transitions[start][symbol].append(end)

        # Make sure state is in the transitions dictionary
        if end not in self.transitions:
            self.transitions[end] = dict()

    def __str__(self):
        """How to print a dfa"""
        # Build the string line by line. Join at the end.
        lines = []
        lines.append("Initial State: {{{}}}".format(self.initial_state))
        lines.append(
            "Final States: {{{}}}".format(
                ",".join(map(str, self.final_states))))
        
        # column headers
        lines.append(
            "State\t{}".format("\t".join(self.alphabet)))

        # For each state, print transitions
        for state_name in range(1, len(self.transitions) + 1):
            line = "{}".format(state_name)
            for symbol in self.alphabet:
                line += "\t{{{}}}".format(
                    ",".join(map(str, self.transitions.get(
                        state_name, dict()).get(symbol, []))))
            lines.append(line)

        return "\n".join(lines)


def nfa_to_dfa(nfa):
    # create empty automaton to build from
    alphabet = nfa.alphabet
    dfa = FiniteAutomaton(1, dict(), None, alphabet)

    initial_state = nfa.null_closure([nfa.initial_state])
    print "E-closure(IO) = {{{}}} = 1\n".format(
        ",".join(map(str, initial_state)))
    dfa_states = {tuple(initial_state): 1}
    # Rather than "marking" states, keep them in a queue
    unmarked = [initial_state]

    # Continue while there are "unmarked" states
    while(unmarked):
        start = unmarked.pop()
        initial_state_name = dfa_states[tuple(start)]
        print "Mark {}".format(initial_state_name)
        for symbol in alphabet:
            move = nfa.move(start, symbol)
            if move:
                print_transition(start, symbol, move)
                new_state = nfa.null_closure(move)
                if tuple(new_state) not in dfa_states:
                    # this set of nfa states is a new dfa state
                    new_state_name = len(dfa_states) + 1
                    dfa_states[tuple(new_state)] = new_state_name
                    unmarked.append(new_state_name)
                else:
                    # This state already exists
                    new_state_name = dfa_states[tuple(new_state)]
                print_null_closure(move, new_state, new_state_name)
                # Add transition to dfa
                dfa.add_transition(initial_state_name, symbol, new_state_name)
        print

    # Set final states
    nfa_final_states = set(nfa.final_states)
    for state_set, state_name in dfa_states.items():
        if nfa_final_states.intersection(state_set):
            dfa.final_states.append(state_name)
    print "dfa final states = {}".format(dfa.final_states)

    print dfa
                                       
                
def print_transition(start, symbol, end):
    template_string = "{{{}}} --{}--> {{{}}}"
    print template_string.format(",".join(map(str, start)),
                                 symbol,
                                 ",".join(map(str, end)))


def print_null_closure(state, closure, name):
    template_string = "E-closure{{{}}} = {{{}}} = {}"
    print template_string.format(
        ",".join(map(str, state)), ",".join(map(str, closure)), name)


def file_to_nfa(flo):
    # get initial states
    match = re.match(r"Initial State\:\s*\{(.*)\}", flo.readline())
    initial_state = int(match.groups()[0])

    # get final states
    match = re.match(r"Final States\:\s*\{(.*)\}", flo.readline())
    final_states = [int(state) for state in match.groups()[0].split(',')]
    # get state count
    match = re.match(r"Total States\:\s*(\d*)$", flo.readline())
    num_states = int(match.groups()[0])

    # get state names
    match = re.match(r"State\s*(.*)\s*$", flo.readline())
    symbol_names = [name.strip() for name in match.groups()[0].split()]

    # get transitions
    state_pattern = r"(\d*)\s*" + r"\s*".join(r"\{(.*)\}" for _ in symbol_names)
    reo = re.compile(state_pattern)
    transitions = {}
    for state_string in flo.readlines():
        groups = reo.match(state_string).groups()
        from_state = int(groups[0])
        end_state_strings = groups[1:]
        transitions[from_state] = {}
        for symbol, end_states in zip(symbol_names, end_state_strings):
            if end_states:
                transitions[from_state][symbol] = [
                    int(state) for state in end_states.split(",")]

    # return nfa
    alphabet = [symbol for symbol in symbol_names if symbol != 'E']
    return FiniteAutomaton(initial_state, transitions, final_states, alphabet)


def main():
    nfa = file_to_nfa(stdin)
    print nfa_to_dfa(nfa)


if __name__ == "__main__":
    main()
