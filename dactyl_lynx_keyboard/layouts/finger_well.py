"""The layout of a finger well.
"""
import math
import operator
from collections.abc import Iterable
from functools import reduce
from itertools import chain
from typing import Optional, Tuple

from solid2.core.object_base import OpenSCADObject

from spkb.keyswitch import Keyswitch, MX

from .layout import Layout, XYAdjustCallback


class FingerWellLayout(Layout):
    """The layout of a finger well.
    """
    def __init__(self, columns: int = 6, rows: int = 5, use_1_5u_keys: bool = True, keyswitch: Keyswitch = MX()):
        super(FingerWellLayout, self).__init__(columns=columns, rows=rows, keyswitch=keyswitch)

        self.use_1_5u_keys = use_1_5u_keys

        self.placement_transform = (0, 0, 30.5)

        self.positions_to_skip = ((0, 4), )

    def column_adjust(self, column: float) -> float:
        """Adjust the effective column number of a given column to account for 1.5u keys on the
        outside columns.

        :param column: the column number to adjust
        """
        if self.use_1_5u_keys and column >= 5:
            return column + (column - 4) * 0.25
        else:
            return column

    def row_angle(self, row: float) -> float:
        """Calculate the X rotation angle for the given row.

        :param row: the row number to rotate for
        """
        return math.degrees(self.rad_per_row * (2 - row))

    def column_angle(self, column: float) -> float:
        """Calculate the Y rotation angle for the given column.

        :param column: the row number to rotate for
        """
        return math.degrees(self.rad_per_col * (2 - column))

    def placement_adjust(self, column: float, row: float, shape: OpenSCADObject) -> OpenSCADObject:
        """Adjust the position of the given key/location in the layout.

        :param column: the column to place the key in
        :param row: the row to place the key in
        :param shape: the shape to place
        """
        if column == 2:
            return shape.translate((0, 6.82, -4.0))
        elif column >= 4:
            return shape.translate((0, -20.8, 7.64))
        else:
            return shape

    def layout_place(self, shape: OpenSCADObject) -> OpenSCADObject:
        """Place the layout.

        :param shape: the shape to place
        """
        return shape \
            .up(3) \
            .rotate(math.degrees(math.pi / 10), (0, 1, 0)) \
            .rotate(math.degrees(math.pi / 10), (1, 0, 0)) \
            .translate(self.placement_transform)

    def web_all(self, z_offset: float = 0, thickness: Optional[float] = None, size_adjust: Optional[XYAdjustCallback] = None, position_adjust: Optional[XYAdjustCallback] = None) -> OpenSCADObject:
        """Return the complete "web" between all key positions in this layout.

        :param z_offset: the offset in the Z direction of the corner blocks (before placing at the key positions)
        :param thickness: the thickness of the web; if None, default to self.web_thickness
        :param size_adjust: a callback to adjust the size of the key at this column and row
        :param position_adjust: a callback to adjust the position of the key at this column and row
        """
        web_kwargs = {
            'z_offset': z_offset,
            'thickness': thickness,
            'size_adjust': size_adjust,
            'position_adjust': position_adjust,
        }

        return reduce(
            operator.add,
            chain(
                (
                    self.web_top_left_of(column, row, **web_kwargs)
                    for (column, row) in self.generate_positions()
                    if column > 0 and row > 0 and (column != 1 or row != 4)
                ),
                (
                    self.web_left_of(column, row, **web_kwargs)
                    for (column, row) in self.generate_positions()
                    if column > 0 and (column != 1 or row != 4)
                ),
                (
                    self.web_above(column, row, **web_kwargs)
                    for (column, row) in self.generate_positions()
                    if row > 0
                ),
            )
        )
