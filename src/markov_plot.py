import pickle
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def plot_markov_first_order(pkl_file, top_k=40, prob_threshold=0.01, title=None):
    """
    Input:
    `pkl_file`: path to the input file
    `top_k`: grabs the top 40 paths
    'prob_threshold': ignore probabilities under this
    'title': title of the plot
    """
    with open(pkl_file, "rb") as f:
        transition_dict, start_dist = pickle.load(f)

    if not transition_dict:
        print("Empty Markov model.")
        return

    states = list(transition_dict.keys())

    totals = {s: sum(transition_dict[s].values()) for s in states}
    sorted_states = sorted(totals.keys(), key=lambda x: totals[x], reverse=True)
    selected_states = sorted_states[: min(top_k, len(sorted_states))]

    G = nx.DiGraph()

    for s in selected_states:
        G.add_node(str(s), weight=totals[s])

    for s in selected_states:
        row = transition_dict[s]
        for t, p in row.items():
            if p >= prob_threshold and t in selected_states:
                G.add_edge(str(s), str(t), weight=p, label=f"{p:.2f}")

    pos = nx.spring_layout(G, seed=42, k=0.7)

    node_sizes = [3000 * totals[s] for s in selected_states]
    edge_widths = [5 * G[u][v]["weight"] for u, v in G.edges()]

    plt.figure(figsize=(14, 12))

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="skyblue", alpha=0.9,
                           edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_size=10)

    nx.draw_networkx_edges(G, pos, width=edge_widths, arrowsize=20, arrowstyle='-|>', alpha=0.8)
    nx.draw_networkx_edge_labels(G, pos,
                                 edge_labels={e: G[e[0]][e[1]]["label"] for e in G.edges()},
                                 font_size=8)

    plt.title(title if title else f"Markov Chain (NetworkX): {pkl_file}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(f"{title}.jpg")
    plt.show()

def plot_markov_second_order(pkl_file, top_k=40, prob_threshold=0.01, title=None):
    """
    Input:
    `pkl_file`: path to the input file
    `top_k`: grabs the top 40 paths
    'prob_threshold': ignore probabilities under this
    'title': title of the plot
    """

    with open(pkl_file, "rb") as f:
        transition_dict, start_dist = pickle.load(f)

    if not transition_dict:
        print("Transition dict empty.")
        return

    states = list(transition_dict.keys())

    totals = {s: sum(transition_dict[s].values()) for s in states}
    sorted_states = sorted(states, key=lambda s: totals[s], reverse=True)
    selected_states = sorted_states[: min(top_k, len(sorted_states))]

    G = nx.DiGraph()

    for state in selected_states:
        a, b = state
        label = f"({a}, {b})"
        G.add_node(label, weight=totals[state], raw_state=state)

    for (a, b) in selected_states:
        for c, prob in transition_dict[(a, b)].items():
            if prob >= prob_threshold:
                next_state = (b, c)
                if next_state in selected_states:
                    src = f"({a}, {b})"
                    dst = f"({b}, {c})"
                    G.add_edge(src, dst, weight=prob)

    pos = nx.spring_layout(G, seed=42, k=1.0)

    node_sizes = [3000 * G.nodes[n]["weight"] for n in G.nodes()]
    edge_widths = [6 * G[u][v]["weight"] for u, v in G.edges()]

    plt.figure(figsize=(16, 14))

    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color="lightgreen",
        edgecolors="black",
        alpha=0.9
    )

    nx.draw_networkx_labels(
        G, pos,
        font_size=10
    )

    nx.draw_networkx_edges(
        G, pos,
        width=edge_widths,
        arrowsize=25,
        arrowstyle='-|>',
        alpha=0.7
    )

    # Edge labels
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(u, v): f"{G[u][v]['weight']:.2f}" for u, v in G.edges()},
        font_size=8
    )

    plt.title(title if title else f"Second-Order Markov Graph: {pkl_file}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(f"{title}.jpg")
    plt.show()


if __name__ == "__main__":
    pathFirst = "../models/classical_jazz_nes_pop_highest_first"
    pathSecond = "../models/classical_jazz_nes_pop_highest_second"

    plot_markov_first_order(f"{pathFirst}/duration.pkl", top_k=40, prob_threshold=0.01,
                            title="First-Order Duration Markov Chain - All Genre")
    plot_markov_first_order(f"{pathFirst}/pitch.pkl", top_k=40, prob_threshold=0.01,
                            title="First-Order Pitch Markov Chain - All Genre")

    plot_markov_second_order(f"{pathSecond}/duration.pkl", top_k=40,
                             prob_threshold=0.01, title="Second-Order Duration Markov Chain - All Genre")
    plot_markov_second_order(f"{pathSecond}/pitch.pkl", top_k=40,
                             prob_threshold=0.01, title="Second-Order Pitch Markov Chain - All Genre")