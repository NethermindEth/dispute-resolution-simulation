import numpy as np
import matplotlib.pyplot as plt

import solara


C = solara.reactive(0.25)
p_ctp = solara.reactive(0.85)
p_cfp = solara.reactive(0.1)
t_dtp = solara.reactive(6)
t_dfp = solara.reactive(114)
apr = solara.reactive(6.5)
Xi = solara.reactive(2000)
operator_pctg = solara.reactive(5)
#r = 32 * apr * operator_pctg / 12
tilde_cw = solara.reactive(5)
commission_wl = solara.reactive(3)
wl_cost_type = solara.reactive("Fixed dollar cost")
#c_w = tilde_cw * Xi_inverse if fixed_cost_in_dollars else r*commission_wl
c_h_dollars = solara.reactive(1500)
#c_h = c_h_dollars * Xi_inverse
alpha = solara.reactive(2)
a_max = solara.reactive((1-p_cfp.value) / p_cfp.value)
a_min = solara.reactive((1-p_ctp.value) / p_ctp.value)

max_n = solara.reactive(10)


@solara.component
def Page():
    with solara.AppBarTitle():
        solara.Text('Numerical Simulation for Validator Dispute Resolution')

    with solara.Column(margin=10):
        with solara.Row():
            solara.InputFloat("Court fees (ETH)", value=C, continuous_update=True)
            solara.InputFloat("p_CTP", value=p_ctp, continuous_update=True)
            solara.InputFloat("p_CFP", value=p_cfp, continuous_update=True)
            solara.InputFloat("t_DTP", value=t_dtp, continuous_update=True)
            solara.InputFloat("t_DFP", value=t_dfp, continuous_update=True)

        with solara.Row():
            solara.InputFloat("Staking APR (%)", value=apr, continuous_update=True)
            solara.InputFloat("ETH/USD mean exchange rate*", value=Xi, continuous_update=False) # prevent div by zero
            Xi_inverse = 1/Xi.value

        with solara.Row():
            solara.InputFloat("Lido operator reward (%)", value=operator_pctg, continuous_update=True)
            r = 32 * apr.value / 100 * operator_pctg.value / 100 / 12

            solara.InputFloat("Cost of honest operator (USD)", value=c_h_dollars, continuous_update=True)
            c_h = c_h_dollars.value * Xi_inverse

            solara.Select("White label cost type", value=wl_cost_type, values=["Fixed dollar cost", "Percent of APR"])
            if wl_cost_type.value == "Fixed dollar cost":
                solara.InputFloat("Fixed cost of white-labeling (USD)", value=tilde_cw, continuous_update=True)
                c_w = tilde_cw.value * Xi_inverse
            else:
                solara.InputFloat("White-labeling Commission (%)", value=commission_wl, continuous_update=True)
                c_w = r * commission_wl.value / 100

        with solara.Row():
            solara.SliderFloat("Reward to accuser's bond ratio (alpha)", value=alpha, min=a_min.value, max=a_max.value, step=0.01)

        with solara.Row():
            solara.InputInt("Max validator count", value=max_n, continuous_update=True)
            n_range = np.arange(1,max_n.value+1)

        with solara.Row():
            solara.Markdown("\* *Specifically, this parameter represents the inverse of the mean USD/ETH exchange rate. It can also be referred to as the harmonic mean of the ETH/USD exchange rate*")

        # calculations
        R_min_perf = (r-c_w) * t_dtp.value * n_range - C.value
        R_min_imperf = R_min_perf / (p_ctp.value - (1-p_ctp.value)/alpha.value)
        R_min_honest = (C.value + c_h - r*t_dfp.value*n_range) / ((1-p_cfp.value)/alpha.value - p_cfp.value)
        R_min_aggregate = np.maximum.reduce([R_min_perf, R_min_imperf, R_min_honest, np.zeros(max_n.value)])

        accuser_return_t = (alpha.value + 1) * p_ctp.value - 1
        accuser_return_f = (alpha.value + 1) * p_cfp.value - 1

        with solara.Card():
            solara.Markdown(f"###Expected return for an honest case: {100*accuser_return_t:.3f} %")
            solara.Markdown(f"###Expected return for a false case: {100*accuser_return_f:.3f} %")


        # plot
        fig = plt.figure(figsize=(20,8))
        ax = fig.subplots()
        ax.plot(n_range, np.maximum.reduce([R_min_perf, np.zeros(max_n.value)]), '--', label='white-label perfect court')
        ax.plot(n_range, np.maximum.reduce([R_min_imperf, np.zeros(max_n.value)]), '--', label='white-label imperfect court')
        ax.plot(n_range, np.maximum.reduce([R_min_honest, np.zeros(max_n.value)]), '--', label='honest opertor')
        ax.plot(n_range, R_min_aggregate, '-', label='aggregate bound')
        ax.grid()
        ax.set_xlabel('Number of validators (n)', fontsize=14)
        ax.set_ylabel('Minimum reward (ETH)', fontsize=14)
        ax.legend(loc='lower right', fontsize=14)
        ax.set_title("Minimum accuser's reward", fontsize=18)
        plt.close(fig)

        with solara.Card():
            solara.FigureMatplotlib(fig)
