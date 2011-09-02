from pypy.interpreter.mixedmodule import MixedModule


class Module(MixedModule):
    applevel_name = 'numpy'

    interpleveldefs = {
        'array': 'interp_numarray.SingleDimArray',
        'dtype': 'interp_dtype.W_Dtype',
        'ufunc': 'interp_ufuncs.W_Ufunc',

        'zeros': 'interp_numarray.zeros',
        'empty': 'interp_numarray.zeros',
        'ones': 'interp_numarray.ones',
        'fromstring': 'interp_support.fromstring',
    }

    # ufuncs
    for exposed, impl in [
        ("abs", "absolute"),
        ("absolute", "absolute"),
        ("add", "add"),
        ("arccos", "arccos"),
        ("arcsin", "arcsin"),
        ("arctan", "arctan"),
        ("copysign", "copysign"),
        ("cos", "cos"),
        ("divide", "divide"),
        ("exp", "exp"),
        ("fabs", "fabs"),
        ("floor", "floor"),
        ("maximum", "maximum"),
        ("minimum", "minimum"),
        ("multiply", "multiply"),
        ("negative", "negative"),
        ("reciprocal", "reciprocal"),
        ("sign", "sign"),
        ("sin", "sin"),
        ("subtract", "subtract"),
        ("tan", "tan"),
        ("equal", "equal")
    ]:
        interpleveldefs[exposed] = "interp_ufuncs.get(space).%s" % impl

    appleveldefs = {
        'average': 'app_numpy.average',
        'mean': 'app_numpy.mean',
    }
