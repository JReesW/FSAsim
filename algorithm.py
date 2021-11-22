class StartError(Exception):
    pass


class AcceptError(Exception):
    pass


class Automaton:
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.acceptors = []
        self.start = None
        self.current = None

    def add_transition(self, start, end, via):
        self.transitions[(start, via)] = end

    def add_state(self, label, pos):
        self.states[label] = pos

    def remove_state(self, label):
        del self.states[label]

        self.transitions = {(s, v): e for (s, v), e in self.transitions.items() if label not in [s, e]}
        self.acceptors = [a for a in self.acceptors if a != label]
        if self.start == label:
            self.start = None

    def add_acceptor(self, label):
        self.acceptors.append(label)

    def remove_acceptor(self, label):
        self.acceptors.remove(label)

    def transition(self, label, letter):
        if (label, letter) in self.transitions:
            return self.transitions[(label, letter)]
        else:
            return None

    def run(self, string):
        if self.start is None:
            raise StartError
        if len(self.acceptors) == 0:
            raise AcceptError

        self.current = self.start
        steps = []

        for c in string:
            next = self.transition(self.current, c)
            if next is not None:
                steps.append((self.current, next))
                self.current = next
            else:
                return steps, (self.current, "Failed")

        if self.current in self.acceptors:
            return steps, (self.current, "Succeeded")
        else:
            return steps, (self.current, "Failed")


# test = Automaton()
#
# test.add_state("q0", (0, 0))
# test.add_state("q1", (0, 0))
# test.add_state("q2", (0, 0))
# test.add_state("q3", (0, 0))
#
# test.add_transition("q0", "q1", "0")
# test.add_transition("q0", "q0", "1")
# test.add_transition("q1", "q1", "0")
# test.add_transition("q1", "q2", "1")
# test.add_transition("q2", "q3", "0")
# test.add_transition("q2", "q0", "1")
# test.add_transition("q3", "q3", "0")
# test.add_transition("q3", "q3", "1")
#
# # test.start = "q0"
# # test.acceptors = ["q3"]
# test.remove_state("q2")
#
#
# print(test.states)
# print(test.transitions)
