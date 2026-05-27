import numpy as np
from scipy.stats import norm
import sys

# --- 2d10 + modifier probability engine ---

def roll_probability(modifier=4):
    """Build probability distribution for 2d10 + modifier."""
    probabilities = {}
    for i in range(1, 11):
        for j in range(1, 11):
            total = i + j + modifier
            probabilities[total] = probabilities.get(total, 0) + 1
    for key in probabilities:
        probabilities[key] /= 100.0
    return probabilities


def cumulative_probabilities(probabilities):
    """Build CDF: cdf[k] = P(roll <= k)."""
    min_roll = min(probabilities.keys())
    max_roll = max(probabilities.keys())
    cdf = {}
    cumulative = 0
    for roll in range(min_roll, max_roll + 1):
        cumulative += probabilities.get(roll, 0)
        cdf[roll] = cumulative
    return cdf


def cdf_lookup(cdf, k):
    """CDF lookup: P(roll <= k). Returns 0 below min, 1 above max."""
    if k < min(cdf.keys()):
        return 0.0
    if k > max(cdf.keys()):
        return 1.0
    return cdf.get(k, 0.0)


def expected_points_per_roll(TN, cdf):
    """
    E[points] = P(roll>=TN) + P(roll>=TN+5) + P(roll>=TN+10)
    """
    p1 = 1 - cdf_lookup(cdf, TN - 1)
    p2 = 1 - cdf_lookup(cdf, TN + 4)
    p3 = 1 - cdf_lookup(cdf, TN + 9)
    return p1 + p2 + p3


def variance_points_per_roll(TN, cdf):
    """
    Var(X) = E[X^2] - E[X]^2
    E[X^2] = p1 + 3*p2 + 5*p3
    """
    p1 = 1 - cdf_lookup(cdf, TN - 1)
    p2 = 1 - cdf_lookup(cdf, TN + 4)
    p3 = 1 - cdf_lookup(cdf, TN + 9)
    e_x = p1 + p2 + p3
    e_x2 = p1 + 3 * p2 + 5 * p3
    return e_x2 - e_x ** 2


def recommend(N, Y, X, modifier=4):
    """
    Given N players, Y rounds, and X success probability,
    output a markdown table of (TN, PN) pairs.
    """
    probabilities = roll_probability(modifier)
    cdf = cumulative_probabilities(probabilities)
    min_roll = min(probabilities.keys())
    max_roll = max(probabilities.keys())

    z = norm.ppf(1 - X)

    lines = []
    lines.append(f"## 2d10 + {modifier} | {N} Players | {Y} Rounds | {X*100:.0f}% Success")
    lines.append("")
    lines.append("| Target Number | Avg pts/roll | Avg total | Swing | Total Points |")
    lines.append("|--------------:|-------------:|----------:|------:|-------------:|")

    for TN in range(min_roll, max_roll + 1):
        mu = expected_points_per_roll(TN, cdf)
        var = variance_points_per_roll(TN, cdf)
        if var < 0:
            var = 0

        total_mu = N * Y * mu
        total_std = np.sqrt(N * Y * var)
        PN = total_mu + z * total_std

        if PN < 1:
            pn_str = "<1"
        else:
            pn_str = f"{PN:.1f}"

        lines.append(
            f"| {TN} | {mu:.3f} | {total_mu:.2f} | {total_std:.2f} | {pn_str} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Plot Meter Calculator: recommend TN/PN pairs for a 2d10 dice system."
    )
    parser.add_argument("-n", "--players", type=int, required=True,
                        help="Number of players (N)")
    parser.add_argument("-y", "--rounds", type=int, required=True,
                        help="Number of rounds (Y)")
    parser.add_argument("-x", "--probability", type=float, required=True,
                        help="Desired success probability as decimal (e.g. 0.8 for 80%%)")
    parser.add_argument("-m", "--modifier", type=int, default=4,
                        help="Roll modifier added to 2d10 (default: 4)")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Output file path (default: stdout)")

    args = parser.parse_args()

    if not (0 < args.probability < 1):
        print("Error: probability must be between 0 and 1 (exclusive).", file=sys.stderr)
        sys.exit(1)

    result = recommend(args.players, args.rounds, args.probability, args.modifier)

    if args.output is None:
        args.output = f"meter_n{args.players}_y{args.rounds}_x{int(args.probability*100)}_m{args.modifier}.md"

    with open(args.output, "w") as f:
        f.write(result)
    print(f"Written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
