
"""
	An example of generating first order logic expressions
"""

from LOTlib.Grammar import Grammar

# Create a  grammar:
G = Grammar()

G.add_rule('BOOL', 'x', None, 2.0) # X is a terminal, so arguments=None

 # Each of these is a function, requiring some arguments of some type
G.add_rule('BOOL', 'and_', ['BOOL', 'BOOL'], 1.0)
G.add_rule('BOOL', 'or_', ['BOOL', 'BOOL'], 1.0)
G.add_rule('BOOL', 'not_', ['BOOL'], 1.0)

G.add_rule('BOOL', 'exists_', ['FUNCTION', 'SET'], 0.50)
G.add_rule('BOOL', 'forall_', ['FUNCTION', 'SET'], 0.50) 

G.add_rule('SET', 'S', None, 1.0)

# And allow us to create a new kind of function
G.add_rule('FUNCTION', 'lambda', ['BOOL'], 1.0, bv_name='BOOL', bv_args=None) # bvtype means we introduce a bound variable below
G.BV_WEIGHT = 2.0 # When we introduce bound variables, they have this (relative) probability


for i in xrange(1000):
	x = G.generate('BOOL')
	
	print x.log_probability(), x
	