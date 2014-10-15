__author__ = 'eric'

from collections import defaultdict
from LOTlib.Miscellaneous import logplusexp, Infinity
from Inference import normalizingConstant

# maps output number (e.g. 8) to a number of yes/no's (e.g. [10/2] )
human_in_data = [2, 4, 6]
human_out_data = {
    8: (10, 2),
    12: (5, 7),
    14: (8, 4)
}


# TODO: make this generate some hypotheses
def generateHypotheses(grammar, input_data):
    return set()


# return likelihood of generating data given a grammar, summed over all hypotheses generated
# Note: this depends on the compute_likelihood function being appropriate ...
# ==> returns a dictionary with each output key returning the summed likelihood of that single data point
def likelihoodGivenGrammar(grammar, input_data, output_data):
    hypotheses = generateHypotheses(grammar, input_data)
    Z = normalizingConstant(hypotheses)

    likelihoods = defaultdict(lambda: -Infinity)
    for h in hypotheses:
        w = h.posterior_score - Z
        for o in output_data.keys():
            weighted_likelihood = h.compute_likelihood(o) + w
            likelihoods[0] = logplusexp(likelihoods[o], weighted_likelihood)
    return likelihoods


# for fixed grammar and model parameters (e.g. for a fixed model you could import) compute the match to human data
def likelihoodOfHumanDataGivenGrammar(grammar, input_data, output_data):
    model_likelihoods = likelihoodGivenGrammar(grammar, input_data, output_data)

    human_likelihoods = {}
    for o in output_data.keys():
        likelihood = output_data[o][0] / (output_data[o][0]+output_data[o][1])       # number of 'yes' responses / number of 'no'
        human_likelihoods[o] = likelihood

    # TODO: calculate similarity between model_likelihoods & human_likelihoods
    return 0

