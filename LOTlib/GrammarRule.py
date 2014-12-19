"""
This class is a wrapper for representing "rules" in the grammar.

TODO:
    One day we will change "nt" to returntype to match with the FunctionNodes


"""
from FunctionNode import FunctionNode, BVAddFunctionNode, BVUseFunctionNode
from copy import copy
from LOTlib.Miscellaneous import None2Empty
from uuid import uuid4

class GrammarRule(object):
    """
    Arguments
        nt (str): the nonterminal
        name (str): the name of this function
        to (list<str>): what you expand to (usually a FunctionNode).
        p (float): unnormalized probability of expansion
        resample_p (float):
        bv_prefix (?): may be needed for GrammarRules introduced *by* BVGrammarRules, so that when we
          display them we can map to bv_prefix+depth

    Examples:
        # A rule where "expansion" is a nonempty list is a real expansion:
        >> GrammarRule( "EXPR", "plus", ["EXPR", "EXPR"], ...) -> plus(EXPR,EXPR)
        # A rule where "expansion" is [] is a thunk
        >> GrammarRule( "EXPR", "plus", [], ...) -> plus()
        # A rule where "expansion" is [] is a real terminal (non-thunk)
        >> GrammarRule( "EXPR", "five", None, ...) -> five
        # A rule where "name" is '' expands without parens:
        >> GrammarRule( "EXPR", '', "SUBEXPR", ...) -> EXPR->SUBEXPR

    Note:
        The rule id (rid) is very important -- it's what we use expansion determine equality

    """
    def __init__(self, nt, name, to, p=1.0, resample_p=1.0, bv_prefix=None):
        p = float(p)
        self.__dict__.update(locals())
        for a in None2Empty(to):
            assert isinstance(a,str)
        if name == '':
            assert (to is None) or (len(to) == 1), \
                "*** GrammarRules with empty names must have only 1 argument"

    def __repr__(self):
        """Print string in format: 'NT -> [TO]   w/ p=1.0, resample_p=1.0'."""
        return str(self.nt) + " -> " + self.name + (str(self.to) if self.to is not None else '') + \
            "\tw/ p=" + str(self.p) + ", resample_p=" + str(self.resample_p)

    def __eq__(self, other):
        """Equality is determined through "is" so that we can remove a rule from lists via list.remove()."""
        return self is other

    def short_str(self):
        """Print string in format: 'NT -> [TO]'."""
        return str(self.nt) + " -> " + self.name + (str(self.to) if self.to is not None else '')

    def __ne__(self, other):
        return not self.__eq__(other)

    def make_FunctionNodeStub(self, grammar, gp, parent):
        # NOTE: It is VERY important to copy to, or else we end up wtih garbage
        return FunctionNode(parent, returntype=self.nt, name=self.name, args=copy(self.to),
                            generation_probability=gp, rule=self)


class BVAddGrammarRule(GrammarRule):
    """A kind of GrammarRule that supports introducing BVs.

    This gives a little type checking so that we don't call this with the wrong rules
        
    """
    def __init__(self, nt, name, to, p=1.0, resample_p=1.0,
                 bv_prefix="y", bv_type=None, bv_args=None, bv_p=None):
        """
        Arguments:
            nt(str): the nonterminal
            name(str): the name of this function
            to(list<str>): what you expand to (usually a FunctionNode).
            rid(?): the rule id number
            p(float): unnormalized probability of expansion
            resample_p(float): the probability of choosing this node in an expansion
            bv_type(str): return type of the introduced bound variable
            bv_args(?): what are the args when we use a bv (None is terminals, else a type signature)

        Note:
            If we use this, we should have BV (i.e. argument `bv_type` should be specified).

        """
        p = float(p)
        self.__dict__.update(locals())
        assert bv_type is not None, "Did you mean to use a GrammarRule instead of a BVGrammarRule?"
        assert isinstance(bv_type, str), "bv_type must be a string! Make sure it's not a tuple or list."
        
    def __repr__(self):
        return str(self.nt) + " -> " + self.name + (str(self.to) if self.to is not None else '') + \
            "\tw/ p=" + str(self.p) + ", resample_p=" + str(self.resample_p) + \
            "\tBV:" + str(self.bv_type) + ";" + str(self.bv_args) + ";" + self.bv_prefix
    
    def make_bv_rule(self, grammar):
        """Construct the rule that we introduce at a given depth.

        Note:
            * This is a GrammarRule and NOT a BVGrammarRule because the introduced rules should *not*
                themselves introduce rules!
            * This is a little awkward because it must look back in grammar, but I don't see how to avoid that

        """
        bvp = self.bv_p
        if bvp is None:
            bvp = grammar.BV_P
        return BVUseGrammarRule(self.bv_type, self.bv_args,
                                p=bvp, resample_p=grammar.BV_RESAMPLE_P, bv_prefix=self.bv_prefix)
   
    def make_FunctionNodeStub(self, grammar, gp, parent):
        """Return a FunctionNode with none of the arguments realized. That's a "stub"

        Arguments:
            d(int): the current depth
            gp(float): the generation probability
            parent(?):

        Note:
        * The None's in the next line need to get set elsewhere, since they will depend on the depth and
        other rules
        * It is VERY important to copy to, or else we end up wtih garbage

        """
        return BVAddFunctionNode(parent, returntype=self.nt, name=self.name, args=copy(self.to),
                                 generation_probability=gp, added_rule=self.make_bv_rule(grammar), rule=self)


class BVUseGrammarRule(GrammarRule):
    """TODO: write docstring"""
    def __init__(self, nt, to, p=1.0, resample_p=1.0, bv_prefix=None):
        GrammarRule.__init__(self, nt, 'bv__'+uuid4().hex, to, p, resample_p, bv_prefix)

    def make_FunctionNodeStub(self, grammar, gp, parent):
        # NOTE: It is VERY important to copy to, or else we end up wtih garbage
        return BVUseFunctionNode(parent, returntype=self.nt, name=self.name, args=copy(self.to),
                                 generation_probability=gp, rule=self)
