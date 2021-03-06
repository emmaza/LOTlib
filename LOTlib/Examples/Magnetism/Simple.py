# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib.Miscellaneous import qq
from LOTlib.Grammar import Grammar

grammar = Grammar()

grammar.add_rule('START', '', ['Pabstraction'], 1.0) # a predicate abstraction

# lambdaUsePredicate is where you can use the predicate defined in lambdaDefinePredicate
grammar.add_rule('Pabstraction',  'apply_', ['lambdaUsePredicate', 'lambdaDefinePredicate'], 1.0, )
grammar.add_rule('lambdaUsePredicate', 'lambda', ['INNER-BOOL'],    5.0, bv_type='INNER-BOOL', bv_args=['OBJECT'], bv_prefix='F')
grammar.add_rule('lambdaUsePredicate', 'lambda', ['Pabstraction'], 1.0,  bv_type='INNER-BOOL', bv_args=['OBJECT'], bv_prefix='F')


# Define a predicate that will just check if something is in a BASE-SET
grammar.add_rule('lambdaDefinePredicate', 'lambda', ['lambdaDefinePredicateINNER'], 1.0,  bv_type='OBJECT', bv_args=None, bv_prefix='z')
# the function on objects, that allows them to be put into classes (analogous to a logical model here)
grammar.add_rule('lambdaDefinePredicateINNER', 'is_in_', ['OBJECT', 'BASE-SET'], 1.0)

grammar.add_rule('INNER-BOOL', 'is_in_', ['OBJECT', 'BASE-SET'], 10.0)

# After we've defined F, these are used to construct the concept
grammar.add_rule('INNER-BOOL', 'and_', ['INNER-BOOL', 'INNER-BOOL'], 1.0)
grammar.add_rule('INNER-BOOL', 'or_', ['INNER-BOOL', 'INNER-BOOL'], 1.0)
grammar.add_rule('INNER-BOOL', 'not_', ['INNER-BOOL'], 1.0)

grammar.add_rule('OBJECT', 'x', None, 1.0)
grammar.add_rule('OBJECT', 'y', None, 1.0)
grammar.add_rule('OBJECT', '', ['BASE-OBJECT'], 1.0) # maybe or maybe not?

# BASE-SET is here a set of BASE-OBJECTS (non-args)
grammar.add_rule('BASE-SET', 'set_add_', ['BASE-OBJECT', 'BASE-SET'], 1.0)
grammar.add_rule('BASE-SET', 'set_', [], 1.0)

grammar.add_rule('BASE-OBJECT', qq('p1'), None, 1.0)
grammar.add_rule('BASE-OBJECT', qq('p2'), None, 1.0)
grammar.add_rule('BASE-OBJECT', qq('n1'), None, 1.0)
grammar.add_rule('BASE-OBJECT', qq('n2'), None, 1.0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib.DataAndObjects import FunctionData

def make_data(n=1, alpha=0.99, *args, **kwargs):
    # Set up data -- true output means attraction (p=positive; n=negative)
    return [ FunctionData(input=[ "p1", "n1" ], output=True, alpha=alpha),
                     FunctionData(input=[ "p1", "n2" ], output=True, alpha=alpha),
                     FunctionData(input=[ "p1", "p1" ], output=False, alpha=alpha),
                     FunctionData(input=[ "p1", "p2" ], output=False, alpha=alpha),

                     FunctionData(input=[ "p2", "n1" ], output=True, alpha=alpha),
                     FunctionData(input=[ "p2", "n2" ], output=True, alpha=alpha),
                     FunctionData(input=[ "p2", "p1" ], output=False, alpha=alpha),
                     FunctionData(input=[ "p2", "p2" ], output=False, alpha=alpha),

                     FunctionData(input=[ "n1", "n1" ], output=False, alpha=alpha),
                     FunctionData(input=[ "n1", "n2" ], output=False, alpha=alpha),
                     FunctionData(input=[ "n1", "p1" ], output=True, alpha=alpha),
                     FunctionData(input=[ "n1", "p2" ], output=True, alpha=alpha),

                     FunctionData(input=[ "n2", "n1" ], output=False, alpha=alpha),
                     FunctionData(input=[ "n2", "n2" ], output=False, alpha=alpha),
                     FunctionData(input=[ "n2", "p1" ], output=True, alpha=alpha),
                     FunctionData(input=[ "n2", "p2" ], output=True, alpha=alpha)] * n


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hypothesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood

class MyHypothesis(BinaryLikelihood, LOTHypothesis):
    def __init__(self, **kwargs ):
        LOTHypothesis.__init__(self, grammar, display='lambda x,y: %s', **kwargs)

def make_hypothesis(**kwargs):
    return MyHypothesis(**kwargs)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":

    from LOTlib.Inference.Samplers.StandardSample import standard_sample

    standard_sample(make_hypothesis, make_data)




