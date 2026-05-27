# Plot Meter Calculator

A tool for tabletop RPG designers to balance plot advancement mechanics. Given a **2d10 + modifier** dice system with tiered success thresholds, it recommends **Total Points** values for any **Target Number** that achieve a desired probability of party success.

## The System

Each round, every player rolls 2d10 + modifier against a Target Number:

| Roll Result | Points Earned |
|---|---:|
| Below TN | 0 |
| TN or higher | 1 |
| TN + 5 or higher | 2 |
| TN + 10 or higher | 3 |

The party accumulates points across all players and rounds. If total points reach the **Total Points** threshold, the plot succeeds.

## Getting Started

```
git clone https://github.com/HarryCordewener/Convergence-Meter-Calculations.git
cd Convergence-Meter-Calculations
pip install numpy scipy
```

## Usage

```
python meter.py -n PLAYERS -y ROUNDS -x PROBABILITY [-m MODIFIER] [-o OUTPUT]
```

### Required Arguments

| Flag | Description |
|---|---|
| `-n`, `--players` | Number of players (N) |
| `-y`, `--rounds` | Number of rounds (Y) |
| `-x`, `--probability` | Desired success probability as a decimal (e.g. `0.8` for 80%) |

### Optional Arguments

| Flag | Description | Default |
|---|---|---|
| `-m`, `--modifier` | Flat bonus added to each 2d10 roll | 4 |
| `-o`, `--output` | Write markdown to a specific file path | `meter_n{N}_y{Y}_x{X%}_m{M}.md` |

### Examples

Basic usage (4 players, 5 rounds, 80% success):

```
python meter.py -n 4 -y 5 -x 0.8
```

Outputs to `meter_n4_y5_x80_m4.md`.

With a custom modifier:

```
python meter.py -n 3 -y 8 -x 0.75 -m 6
```

Outputs to `meter_n3_y8_x75_m6.md`.

Explicit output path:

```
python meter.py -n 4 -y 5 -x 0.8 -o results.md
```

## Reading the Output

The table shows every valid Target Number (6–24) and the corresponding Total Points threshold that gives the party exactly X% chance of accumulating enough points.

| Column | Meaning |
|---|---|
| **Target Number** | The DC for individual rolls |
| **Avg pts/roll** | Average points one player earns per round at this TN |
| **Avg total** | Average total party points across all rounds |
| **Swing** | Standard deviation of total points (measures outcome variance) |
| **Total Points** | Set this as the success threshold for the desired probability |

### How to pick a row

- **Easy encounter**: pick a low TN (6–10). Individual rolls succeed often, but Total Points is high so the party still needs consistent effort.
- **Hard encounter**: pick a high TN (14–18). Individual rolls fail often, but Total Points is low to compensate.
- **Dramatic encounter**: pick mid-range TN (11–13) for maximum variance — outcomes swing the most.

## Math

The calculator uses the normal approximation to the sum of N×Y independent discrete random variables (one per player-round). For each TN it computes the mean and variance of points-per-roll, scales by N×Y, then solves:

```
Total Points = Avg[total] + z(1-X) × Swing
```

Where `z(1-X)` is the inverse normal CDF at `1-X`. Since X > 0.5 in typical use, `z` is negative, placing Total Points below the mean — ensuring most runs succeed.
