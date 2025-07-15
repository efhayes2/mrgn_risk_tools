import matplotlib.pyplot as plt
import numpy as np

class InterestRateCurve:
    def __init__(self, x_nodes_bps, y_nodes_bps, max_rate_bps, label=None):
        """
        Initialize the interest rate curve.
        Automatically appends (0,0) and (10000, max_rate).
        """
        self.max_rate_bps = max_rate_bps
        self.label = label or "Curve"

        self.x_nodes = [0] + x_nodes_bps + [10_000]
        self.y_nodes = [0] + y_nodes_bps + [self.max_rate_bps]

        self._sort_nodes()

    def _sort_nodes(self):
        """Sort internal nodes by x (utilization)."""
        sorted_pairs = sorted(zip(self.x_nodes, self.y_nodes))
        self.x_nodes, self.y_nodes = zip(*sorted_pairs)

    def insert_node_at(self, new_x):
        """
        Insert (new_x, interpolated_y) into the curve if x isn't present.
        Supports both interpolation and truncation.
        """
        if new_x in self.x_nodes:
            return

        if new_x < self.x_nodes[0] or new_x > self.x_nodes[-1]:
            raise ValueError(f"x = {new_x} out of curve bounds.")

        # Find the segment (x0, x1) such that x0 < new_x < x1
        for i in range(1, len(self.x_nodes)):
            x0, x1 = self.x_nodes[i - 1], self.x_nodes[i]
            if x0 < new_x < x1:
                y0, y1 = self.y_nodes[i - 1], self.y_nodes[i]
                slope = (y1 - y0) / (x1 - x0)
                y_new = y0 + slope * (new_x - x0)
                self.x_nodes = list(self.x_nodes) + [new_x]
                self.y_nodes = list(self.y_nodes) + [y_new]
                self._sort_nodes()
                return

    def interpolate(self, max_x=10_000, resolution=1000):
        """
        Interpolates (linearly) the curve up to max_x (exclusive).
        Returns arrays: x_interp, y_interp.
        """
        x_interp = np.linspace(0, max_x, resolution)
        y_interp = np.interp(x_interp, self.x_nodes, self.y_nodes)
        return x_interp, y_interp

    @staticmethod
    @staticmethod
    def plot_curves_up_to_percent_cutoff(curves, lower_percent=40.0, upper_cutoff=100.0, title=None):
        """
        Plot multiple curves on the same graph between lower_percent and upper_cutoff.
        Automatically inserts interpolation points at both ends if missing.

        Args:
            curves: list of InterestRateCurve instances
            lower_percent (float): minimum utilization % to show (e.g., 40.0)
            upper_cutoff (float): maximum utilization % to show (e.g., 90.05, 100.0)
            title (str): optional plot title
        """
        x_cutoff_bps = 10_000.0 if upper_cutoff == 100.0 else upper_cutoff * 100.0
        x_lower_bps = lower_percent * 100.0

        if not (0.0 <= x_lower_bps < x_cutoff_bps <= 10_000.0):
            raise ValueError("Bounds must satisfy 0 <= lower < upper <= 100")

        # Ensure curves contain nodes at both boundaries
        for curve in curves:
            if upper_cutoff < 100.0:
                curve.insert_node_at(x_cutoff_bps)
            curve.insert_node_at(x_lower_bps)

        # Plot
        plt.figure(figsize=(10, 6))

        for curve in curves:
            x_interp = np.linspace(x_lower_bps, x_cutoff_bps, 1000)
            y_interp = np.interp(x_interp, curve.x_nodes, curve.y_nodes)

            plt.plot(
                [x / 100.0 for x in x_interp],
                [y / 100.0 for y in y_interp],
                label=curve.label
            )

            # Plot only visible scatter points
            plt.scatter(
                [x / 100.0 for x in curve.x_nodes if x_lower_bps <= x <= x_cutoff_bps],
                [curve.y_nodes[i] / 100.0 for i, x in enumerate(curve.x_nodes) if x_lower_bps <= x <= x_cutoff_bps],
                s=40
            )

        title = title or f"Interest Rate Curves from {lower_percent:.2f}% to {upper_cutoff:.2f}% Utilization"
        plt.xlabel("Utilization Rate (%)")
        plt.ylabel("Borrow Rate (%)")
        plt.title(title)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


def main():
    # Curve 1: MarginFi
    x1 = [9200]
    y1 = [750]
    max_rate1 = 30_000
    marginfi = InterestRateCurve(x1, y1, max_rate1, label="MarginFi")

    # Curve 2: Kamino
    x2 = [9100, 9300, 9300]
    y2 = [787, 1346, 2873]
    max_rate2 = 17_500
    kamino = InterestRateCurve(x2, y2, max_rate2, label="Kamino")

    curves = [marginfi, kamino]

    # Plot from 40% to 90% utilization
    # InterestRateCurve.plot_curves_up_to_percent_cutoff(curves, lower_percent=50.0, upper_cutoff=90.0)

    # Plot from 50% to 95%
    InterestRateCurve.plot_curves_up_to_percent_cutoff(curves, lower_percent=50.0, upper_cutoff=91.5)


if __name__ == "__main__":
    main()

