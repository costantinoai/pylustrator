"""An annotation must move by the drag, once.

`ax.annotate(..., textcoords="offset points")` -- which is also what
`ax.bar_label` produces -- keeps its anchor in data coordinates and its position
as an offset from that anchor. The two were treated as one coordinate system, so
the anchor was set from an offset in points: dragging such a label moved it far
outside the axes, where it was clipped and appeared to vanish.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import unittest

import matplotlib

matplotlib.use("QtAgg")
import matplotlib.pyplot as plt  # noqa: E402 -- the backend must be chosen first

from base_test_class import BaseTest  # noqa: E402


class TestAnnotation(BaseTest):
    def _figure(self):
        import pylustrator
        from pylustrator import QtGuiDrag

        pylustrator.start()
        fig = plt.figure(figsize=(5, 3))
        axes = fig.subfigures(1, 1).add_subplot()
        axes.bar([0, 1], [10, 20])
        axes.annotate(
            "***", (0, 10), xytext=(0, 6), textcoords="offset points", ha="center"
        )
        fig.canvas.draw()
        QtGuiDrag.pyl_show(hide_window=True)
        fig.canvas.draw()
        self.fig = fig
        return fig, axes

    @staticmethod
    def _corner(artist):
        box = artist.get_window_extent()
        return box.x0, box.y0

    def test_dragging_an_annotation_moves_it_by_the_drag(self):
        fig, axes = self._figure()
        note = [text for text in axes.texts if text.get_text() == "***"][0]
        before = self._corner(note)

        self.move_element((20, 20), note)
        fig.canvas.draw()

        after = self._corner(note)
        self.assertAlmostEqual(after[0] - before[0], 20, places=3)
        self.assertAlmostEqual(after[1] - before[1], 20, places=3)

        # A drag reports the same target points on every motion event, so
        # setting them repeatedly must not walk the annotation across the axes.
        for _ in range(3):
            self.move_element((0, 0))
        fig.canvas.draw()
        self.assertAlmostEqual(self._corner(note)[0], after[0], places=3)
        self.assertAlmostEqual(self._corner(note)[1], after[1], places=3)
        # The offset from the anchor is what the editor writes, so the anchor
        # and the offset must both be recorded for the move to be reproducible.
        changes = "\n".join(fig.change_tracker.sorted_changes())
        self.assertIn("position=", changes)
        self.assertIn(".xy = ", changes)
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
