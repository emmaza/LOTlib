
from copy import deepcopy, copy
from math import log
from LOTlib.Miscellaneous import attrmem, logsumexp, sample_one
from Levenshtein import distance
from LOTlib.Hypotheses.Proposers import ProposalFailedException
from LOTlib.Hypotheses.Likelihoods.MultinomialLikelihood import MultinomialLikelihood
from LOTlib.Hypotheses.StochasticSimulation import StochasticSimulation
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Hypotheses.Proposers import IDR_proposal

class InnerHypothesis(LOTHypothesis):
    """
    The type of each function F. This is NOT recursive, but it does allow recurse_ (to refer to the whole lexicon)
    """
    def __init__(self, grammar=None, display="lambda recurse_: %s", **kwargs):
        LOTHypothesis.__init__(self, grammar=grammar, display=display, **kwargs)


    def propose(self, **kwargs):
        ret_value, fb = None, None
        while True: # keep trying to propose
            try:
                ret_value, fb = IDR_proposal(self.grammar, self.value, **kwargs)
                break
            except ProposalFailedException:
                pass

        ret = self.__copy__(value=ret_value)

        return ret, fb

from collections import Counter
from LOTlib.Hypotheses.Lexicon.RecursiveLexicon import RecursiveLexicon
class IncrementalLexiconHypothesis(StochasticSimulation, MultinomialLikelihood, RecursiveLexicon):
        """ A hypothesis where we can incrementally add words and propose to only the additions
        """

        def __init__(self, grammar=None, **kwargs):
            RecursiveLexicon.__init__(self, recurse_bound=5, maxnodes=50, variable_weight=3.0, **kwargs)
            self.grammar=grammar
            self.N = 0
            self.outlier = -100 # read in MultinomialLikelihood

        def make_hypothesis(self, **kwargs):
            return InnerHypothesis(**kwargs)

        def propose(self):

            new = deepcopy(self)  ## Now we just copy the whole thing
            while True:
                try:
                    i = sample_one(range(self.N)) # random one
                    # i = max(self.value.keys()) # only propose to last
                    x, fb = self.get_word(i).propose()
                    new.set_word(i, x)

                    new.grammar = self.value[0].grammar # keep the grammar the same object

                    return new, fb

                except ProposalFailedException:
                    pass

        def dispatch_word(self, word, *input):
            """ We override this so that the hypothesis defaultly calls with the last word via __call__"""
            self.recursive_call_depth += 1

            if self.recursive_call_depth > self.recursive_depth_bound:
                return ''
            else:
                return self.value[word](self.dispatch_word, *input)  # pass in "self" as lex, using the recursive version

        def recursive_call(self, word, *args):
            raise NotImplementedError

        def __call__(self, nsamples=1024, *args):
            """
            Wrap in self as a first argument that we don't have to in the grammar. This way, we can use self(word, X Y) as above.
            NOTE: This overwrites much of the logic of StochasticSimulation since we have a special call function
            """



            output = Counter()
            for _ in xrange(nsamples):
                self.recursive_call_depth = 0
                v = self.dispatch_word(self.N-1, *args)
                output[v] += 1

            # renormalize
            z = float(sum(output.values()))
            for k, v in output.items():
                output[k] = v / z

            return output

