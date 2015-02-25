import csv, math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider
from LOTlib.Miscellaneous import logsumexp
from MCMCSummary import MCMCSummary


class VectorSummary(MCMCSummary):
    """
    Summarize & plot data for MCMC with a VectorHypothesis (e.g. GrammarHypothesis).

    """
    def __init__(self, skip=100, cap=100):
        MCMCSummary.__init__(self, skip=skip, cap=cap)

    def zip_vector(self, idxs):
        """Return a n-long list - each member is a time series of samples for a single vector item.

        In `self.samples`, we have a list of samples; basically instead of this:
            [sample1, sample2, sample3, ...]

        We want to return this:
            [[s1[0], s2[0], s3[0], ...], [s1[1], s2[1], s3[1], ...], ...]

        """
        zipped_vector = zip(*[[s.value[i] for i in idxs] for s in self.samples])
        zipped_vector = [np.array(l) for l in zipped_vector]
        return zipped_vector

    def median_value(self, idxs=None):
        """Return a vector for the median of each value item accross `self.samples`, items in `idxs`."""
        if idxs is None:
            idxs = range(1, self.samples[0].n)
        vector_data = self.zip_vector(range(1, idxs))
        return [np.mean(v) for v in vector_data]

    def mean_value(self, idxs=None):
        """Return a vector for the mean of each value item accross `self.samples`, items in `idxs`."""
        if idxs is None:
            idxs = range(1, self.samples[0].n)
        vector_data = self.zip_vector(idxs)
        return [np.mean(v) for v in vector_data]

    def mean_gh(self, idxs=None):
        value = self.mean_value(idxs)
        gh = self.samples[idxs[-1]].__copy__()
        gh.set_value(value)
        gh.update_posterior()
        return gh

    # --------------------------------------------------------------------------------------------------------
    # Plotting methods

    def plot(self, plot_type='violin'):
        assert plot_type in ('violin', 'values', 'post', 'MLE', 'MAP', 'barplot'), "invalid plot type!"
        if plot_type == 'violin':
            return self.violinplot_value()
        if plot_type == 'values':
            self.lineplot_value()
        if plot_type in ('post', 'MLE', 'MAP'):
            self.lineplot_gh_metric(metric=plot_type)
        if plot_type == 'barplot':
            self.plot_predictive()

    def violinplot_value(self):
        """
        TODO: doc?

        """
        # Numpy array of sampled values for each vector element altered in proposals
        s0 = self.samples[0]
        propose_idxs = s0.propose_idxs

        def draw_violinplot(value):
            """Clear axis & draw a labelled violin plot of the specified data.

            Note:
              * [fixed] If we haven't accepted any proposals yet, all our data is the same and this causes
                a singular matrix 'LinAlgError'

            """
            vector_data = self.zip_vector(propose_idxs)
            data = [vector[0:value] for vector in vector_data]

            ax.clear()
            ax.set_title('Distribution of values over GrammarRules generated by MH')
            try:
                vplot = ax.violinplot(data, points=100, vert=False, widths=0.7,
                                      showmeans=True, showextrema=True, showmedians=True)
            except Exception:     # seems to get LinAlgError, ValueError when we have single-value vectors
                vplot = None
            ax.set_yticks(range(1, len(propose_idxs)+1))
            y_labels = [s0.rules[i].short_str() for i in propose_idxs]
            ax.set_yticklabels(y_labels)

            fig.canvas.draw_idle()
            return vplot

        # Set up initial violinplot
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2, left=0.1)
        violin_stats = draw_violinplot(self.sample_count)

        # Slider updates violinplot as a function of how many samples have been generated
        slider_ax = plt.axes([0.1, 0.1, 0.8, 0.02])
        slider = Slider(slider_ax, "after N samples", valmin=1., valmax=self.sample_count, valinit=1.)
        slider.on_changed(draw_violinplot)

        plt.show()
        return violin_stats

    def lineplot_value(self):
        """
        http://matplotlib.org/examples/pylab_examples/subplots_demo.html

        """
        # Numpy array of sampled values for each vector element altered in proposals
        s0 = self.samples[0]
        propose_idxs = s0.propose_idxs
        n = len(propose_idxs)
        y_labels = [s0.rules[i].short_str() for i in propose_idxs]
        vector_data = self.zip_vector(propose_idxs)

        # N subplots sharing both x/y axes
        f, axs = plt.subplots(n, sharex=True, sharey=True)
        axs[0].set_title('\tGrammar Priors as a Function of MCMC Samples')
        y_min = math.ceil(min([v for vector in vector_data for v in vector]))
        y_max = math.ceil(max([v for vector in vector_data for v in vector]))
        for i in range(n):
            axs[i].plot(vector_data[i])
            axs[i].set_yticks(np.linspace(y_min, y_max, 5))
            # axs[i].scatter(vector_data[i])
            rule_label = axs[i].twinx()
            rule_label.set_yticks([0.5])
            rule_label.set_yticklabels([y_labels[i]])

        # Fine-tune figure; make subplots close to each other and hide x ticks for all but bottom plot.
        f.subplots_adjust(hspace=0)
        plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
        plt.show()

    def lineplot_gh_metric(self, metric='post'):
        """
        Draw a line plot for the GrammarHypothesis, evaluated by GH.posterior_score, MAP, or MLE.

        """
        assert metric in ('post', 'MLE', 'MAP'), "invalid plot metric!"
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2, left=0.1)
        ax.set_title('Evaluation for GrammarHypotheses Sampled by MCMC')

        if metric == 'post':
            mcmc_values = [gh.posterior_score for gh in self.samples]
        elif metric == 'MAP':
            mcmc_values = [gh.max_a_posteriori() for gh in self.samples]
        elif metric == 'MLE':
            mcmc_values = [gh.max_like_estimate() for gh in self.samples]
        else:
            mcmc_values = []
        ax.plot(mcmc_values)
        plt.show()

    # --------------------------------------------------------------------------------------------------------
    # These don't work

    def plot_predictive(self):
        """Visualize p(y \in C) over each y in the domain.

        This will be either the MLE GrammarHypothesis, the MAP, the most recent, or the mean averaged vector.

        This should be like the bar graphs in Josh Tenenbaum / Kevin Murphy's 'Bayesian Concept Learning'.

        Notes
        -----
        * this should be 3 barplots: bayesian model averaging (weighted likelihood), MLE, & MAP

        """
        # Update the bar plots when you move the slider



        # draw_barplots(self.sample_count-1)


        return None

    '''
    # Slider updates violinplot as a function of how many samples have been generated
    slider_ax = plt.axes([0.1, 0.1, 0.8, 0.02])
    slider = Slider(slider_ax, "after N samples",
                valmin=1., valmax=self.sample_count, valinit=self.sample_count-1)
    slider.on_changed(draw_barplots)
    '''
    # plt.show()

    def draw_barplots(self, idx, plot_type='recent'):
        fig, ax = plt.subplots()
        # fig.subplots_adjust(bottom=0.2, left=0.1)
        idxs = range(0, int(idx))
        if plot_type == 'recent':
            gh = self.samples[int(idx)]
        if plot_type == 'mean':
            gh = self.mean_gh(idxs)     # TODO: does this work?????
        if plot_type == 'MAP':
            gh = self.get_top_samples(n=1, s_idxs=idxs, key=(lambda x: x.posterior_score))[0]
        if plot_type == 'MLE':
            gh = self.get_top_samples(n=1, s_idxs=idxs, key=(lambda x: x.likelihood))[0]

        print '!'*100
        print int(idx)
        print gh.value
        print [r.p for sublist in gh.grammar.rules.values() for r in sublist]
        # print gh.posterior_score, gh.likelihood, gh.prior
        # print gh.get_top_hypotheses()
        # print '!'*100

        domain = range(1, gh.hypotheses[0].domain+1)
        p_in_concept = gh.in_concept_avg(domain)

        ax.set_title('Distribution of values at '+str(idx)+' over GrammarRules generated by MH')
        ax.bar(domain, [p_in_concept[key] for key in p_in_concept.keys()])
        ax.set_yticks(np.arange(0., 1.2, .2))
        # fig.canvas.draw()
        return fig

    # ============================================================================================================
    # CSV-saving methods

    def csv_compare_model_human(self, filename, data, gh):
        i = self.count

        gh.update()
        for h in gh.hypotheses:
            h.compute_prior(recompute=True)
            h.update_posterior()

        with open(filename, 'a') as f:
            writer = csv.writer(f)
            hypotheses = gh.hypotheses
            for d in data:
                posteriors = [sum(h.compute_posterior(d.input)) for h in hypotheses]
                Z = logsumexp(posteriors)
                weights = [(post-Z) for post in posteriors]

                for o in d.output.keys():
                    # Probability for yes on output `o` is sum of posteriors for hypos that contain `o`
                    p_human = float(d.output[o][0]) / float(d.output[o][0] + d.output[o][1])
                    p_model = sum([math.exp(w) if o in h() else 0 for h, w in zip(hypotheses, weights)])
                    writer.writerow([i, d.input, o, p_human, p_model])

    def csv_initfiles(self, filename):
        """
        Create new csv files for filename_values, filename_bayes, filename_data_MAP, filename_data_h0.

        """
        with open(filename+'_values.csv', 'wb') as w:
            writer = csv.writer(w)
            writer.writerow(['i', 'nt', 'name', 'to', 'p'])
        with open(filename+'_bayes.csv', 'wb') as w:
            writer = csv.writer(w)
            writer.writerow(['i', 'Prior', 'Likelihood', 'Posterior Score'])
        with open(filename+'_data_MAP.csv', 'wb') as w:
            writer = csv.writer(w)
            writer.writerow(['i', 'input', 'output', 'human p', 'model p'])
        with open(filename+'_data_h0.csv', 'wb') as w:
            writer = csv.writer(w)
            writer.writerow(['i', 'input', 'output', 'human p', 'model p'])

    def csv_appendfiles(self, filename, data):
        """
        Append Bayes data to `_bayes` file, values to `_values` file, and MAP hypothesis human
        correlation data to `_data_MAP` file.

        """
        i = self.count
        gh = self.samples[-1]

        if (i < 10000 and i % 100 is 0) or (i % 1000 is 0):
            with open(filename+'_values.csv', 'a') as w:
                writer = csv.writer(w)
                writer.writerows([[i, r.nt, r.name, str(r.to), gh.value[j]] for j,r in enumerate(gh.rules)])
            with open(filename+'_bayes.csv', 'a') as w:
                writer = csv.writer(w)
                if self.sample_count:
                    writer.writerow([i, gh.prior, gh.likelihood, gh.posterior_score])

        if (i % 30000) is 0:
            MAP_gh = sorted(self.samples, key=(lambda x: -x.posterior_score))[0]
            self.csv_compare_model_human(filename+'_data_MAP.csv', data, MAP_gh)
