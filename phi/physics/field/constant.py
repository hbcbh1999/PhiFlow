import numbers

import numpy

from phi import math, struct
from .flag import DIVERGENCE_FREE
from .field import Field, propagate_flags_children


@struct.definition()
class ConstantField(Field):

    def __init__(self, value=1.0, name=None, flags=(DIVERGENCE_FREE,), **kwargs):
        data = _convert_constant_to_data(value)
        Field.__init__(self, **struct.kwargs(locals(), ignore='value'))

    def sample_at(self, points, collapse_dimensions=True):
        return _expand_axes(self.data, points, collapse_dimensions=collapse_dimensions)

    @property
    def rank(self):
        return None

    @property
    def component_count(self):
        return self.data.shape[-1]

    def unstack(self):
        flags = propagate_flags_children(self.flags, self.rank, 1)
        return [ConstantField(c, '%s[%d]' % (self.name, i), flags=flags, batch_size=self._batch_size) for i, c in enumerate(math.unstack(self.data, -1))]

    @property
    def points(self):
        return None

    def compatible(self, other_field):
        return True

    def __repr__(self):
        return repr(self.data)


def _convert_constant_to_data(value):
    if isinstance(value, numbers.Number):
        value = math.to_float(math.expand_dims(value))
    if isinstance(value, (list, tuple)):
        value = math.to_float(numpy.array(value))
    if len(math.staticshape(value)) < 2:
        value = math.expand_dims(value)
    return value


def _expand_axes(data, points, collapse_dimensions=True):
    assert math.spatial_rank(data) >= 0
    data = math.expand_dims(data, 1, math.spatial_rank(points) - math.spatial_rank(data))
    if collapse_dimensions:
        return data
    else:
        points_axes = math.staticshape(points)[1:-1]
        data_axes = math.staticshape(data)[1:-1]
        for d_points, d_data in zip(points_axes, data_axes):
            assert d_points % d_data == 0
        tilings = [1] + [d_points // d_data for d_points, d_data in zip(math.staticshape(points)[1:-1], math.staticshape(data)[1:-1])] + [1]
        data = math.tile(data, tilings)
        return data
