
from LOTlib.Miscellaneous import attrmem
from LOTlib.Hypotheses.Hypothesis import Hypothesis
from collections import Counter

class StochasticSimulation(Hypothesis):
    """
    If you inherit this, you get a function called simulate that returns the output of many function calls
    """

    @attrmem('simulation_counts')
    def simulate(self, nsamples=1024, normalize=True, *input):
        """ Overwrite call with a dictionary of outputs """

        output = Counter()
        for _ in xrange(nsamples):
            v = super(type(self), self).__call__(*input)
            output[v] += 1

        # renormalize
        if normalize:
            z = float(sum(output.values()))
            for k, v in output.items():
                output[k] = v/z

        return output
