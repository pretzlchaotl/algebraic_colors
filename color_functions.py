import sys
from numbers import *
from math import (
    pi, nan, inf, isnan, isfinite, 
    modf, copysign, 
    cos, sin, 
    atan2, hypot, sqrt, 
    )
from random import random as rdrd
from operator import itemgetter, attrgetter
from functools import lru_cache
from itertools import repeat, filterfalse, permutations, count, chain
from more_itertools import unique_everseen, flatten, all_equal, minmax
from numpy import ndarray, around


__all__ = []
def modulefunc(f, name: str=None):
    if not name and isinstance(f, str) and f:
        name = f
    __all__.append(name or f.__name__)
    return f

#member_groups = {}

#def _new_member_group(name: str):
#    name = name.strip(r"//    \\")
#    _current_group = name
#    member_groups.setdefault(name, {})
#    _add_member = member_groups[_current_group].__setitem__
#_new_member_group("SETUP")


float_ndigits = sys.float_info.dig

class _Constants:
    __slots__ = "VCAP", "PRECISION"
    @property
    def vcap(self): return self.VCAP or 1    # (self.VCAP == 0 means actual VCAP == inf)
    @property
    def prec(self):
        nd = self.PRECISION
        if nd is None: return float_ndigits
        return nd
    
    def __init__(self, vcap, precision):
        if not isfinite(vcap):
            vcap = 0
        elif not (vcap % 1.0):
            vcap = int(vcap)
        if precision is not None:
            precision = int(precision)
        self.VCAP = vcap
        self.PRECISION = precision
    
    def check_equal(self, p, q, tolerance=6):
        if p is q or p==q: return True
        nd = self.PRECISION
        if nd is None:
            nd = tolerance
        return abs(p - q) < 10**nd
    
    def prec_round(self, x, ndigits=None):
        if ndigits is None:
            ndigits = self.prec
        return round(x, ndigits)
    
    def prec_round_atleast_nd(self, x, at_least_ndigits=0):
        ndigits = self.PRECISION
        if ndigits is None: return x
        nd = sorted([ndigits, at_least_ndigits])[-1]
        try: return round(x, nd)
        except TypeError: return around(x, nd)
    
    def maybe_round(self, x, ndigits=None):
        if ndigits is None:
            ndigits = self.PRECISION
        return x if ndigits is None else round(x, ndigits)


constants = modulefunc(_Constants(0, 8), 'constants')
setattr(_Constants, '__new__', lambda cls, *a, **k: constants)

check_equal = modulefunc(constants.check_equal, 'check_equal')
prec_round = modulefunc(constants.prec_round, 'prec_round')


_π2lfs = pi / 2.0
_π3rds = pi / 3.0
_π6ths = pi / 6.0

_cos_π3rds = cos(_π3rds)
_sin_π3rds = sin(_π3rds)

_wholecolors_12_chars = "roylgtcabimf"

tuple(map(modulefunc, [
    'nan', 'isnan', 
    '_π2lfs', '_π3rds', '_π6ths', '_cos_π3rds', '_sin_π3rds', 
    '_wholecolors_12_chars', 
    ]))


_round = round

@modulefunc
def _cpx_round(x, ndigits): return _round(x.real, ndigits) + 1j*_round(x.imag, ndigits)
@modulefunc
def rounded(x, ndigits=...):
    if ndigits is ...:
        ndigits = constants.PRECISION
    if ndigits is None: return x
    try: return _round(x, ndigits)
    except TypeError: return _cpx_round(x, ndigits)
@modulefunc
def rounds(seq, ndigits=...):
    if ndigits is ...:
        ndigits = constants.PRECISION
    if ndigits is None: return seq
    try: return tuple(_round(p, ndigits) for p in seq)
        #map(rounded, seq, repeat(ndigits)))
    except TypeError: return tuple(_cpx_round(p, ndigits) for p in seq)
@modulefunc
def round_rgb(r, g, b, *, ndigits=...):
    if ndigits is ...:
        ndigits = constants.PRECISION
    return round(r, ndigits), round(g, ndigits), round(b, ndigits)



@modulefunc
def get_H(rgb):
    H = getattr(rgb, "H", None) or getattr(rgb, "h", None)
    if H is not None: return H
    return rgb_to_h(rgb)
@modulefunc
def get_hsv(rgb):
    hsv = getattr(rgb, "HSV", None) or getattr(rgb, "hsv", None)
    if hsv is not None: return hsv
    return rgb_to_hsv(rgb)
@modulefunc
def get_hv(rgb):
    hv = getattr(rgb, "HV", None) or getattr(rgb, "hsv", None)
    if hv is not None: return hv
    return rgb_to_hv(rgb)


@modulefunc
def float_gcd(p, q):
    if p < 0:
        p = abs(a)
    if q < 0:
        q = abs(q)
    if p < q:
        p, q = q, p
    while q:
        q, p = (p % q), q
    return p
@modulefunc
def float_gcd_unsigned(p, q):
    "Assumes p >= 0 <= q"
    if p < q:
        p, q = q, p
    while q:
        q, p = (p % q), q
    return p or 1.0

@modulefunc
def float_gcd_reduce(iterable):
    return reduce(float_gcd, iterable) or 1.0
@modulefunc
def float_gcd_unsigned_reduce(iterable):
    return reduce(float_gcd_unsigned, iterable) or 1.0


def _h_modf(H):
    if isnan(H): return nan, None
    H %= 6
    f, i = modf(H)
    return f, i

def _zinfdiv(p, q): return (p / q) if q else inf if p else 0.0


@modulefunc
def randhue(): return rdrd()*6.0


"//    NORMALIZERS    \\"

@modulefunc
def normalize_rgb_generic(rgb, *, vcap=None, floored=False, rationoid=False):
    "Does not refer to global constants."
    r, g, b = rgb
    w, V = minmax(rgb)
    if isnan(V):
        if isnan(w): return 0.0, 0.0, 0.0
        return w, w, w
    if w and (floored or (w < 0)):
        r -= w
        g -= w
        b -= w
        V -= w
    if cd := rationoid and float_gcd_unsigned(float_gcd_unsigned(r, g), b):
        r /= cd
        g /= cd
        b /= cd
        V /= cd
    if Vx := vcap and (V > vcap) and (vcap / V):
        r *= Vx
        g *= Vx
        b *= Vx
    return r, g, b

@modulefunc
def normalize_rgb(rgb, *, floored=False, rationoid=False):
    "Gets vcap from global constants."
    return normalize_rgb_generic(rgb, vcap=constants.VCAP, floored=floored, rationoid=rationoid)

@modulefunc
def normalize_rgb_floored(rgb):
    r, g, b = rgb
    w, V = minmax(rgb)
    if isnan(V):
        if isnan(w): return 0.0, 0.0, 0.0
        return w, w, w
    if w:
        r -= w
        g -= w
        b -= w
        V -= w
    return r, g, b

@modulefunc
def normalize_rgb_rationoid(rgb):
    r, g, b = rgb
    w, V = minmax(rgb)
    if isnan(V):
        if isnan(w): return 0.0, 0.0, 0.0
        return w, w, w
    if cd := float_gcd_unsigned(float_gcd_unsigned(r, g), b):
        r /= cd
        g /= cd
        b /= cd
        V /= cd
    return r, g, b


@modulefunc
def normalize_hv(H, V):
    if isnan(H): return nan, 0.0
    if isnan(V):
        V = 0.0
    elif V < 0:
        V = -V
        H += 3.0
    VCAP = constants.VCAP
    if VCAP and V > VCAP:
        V = VCAP
    return H, V

@modulefunc
def normalize_hsv(H, S, V):
    VCAP = constants.VCAP
    if isnan(V):
        V = (VCAP or 1.0)
    elif V < 0:
        V = -V
        H += 3.0
    if VCAP and V > VCAP:
        V = VCAP
    if isnan(H): return nan, 1.0, V
    if S < 0:
        S = 0.0
    elif S > 1:
        S = 1.0
    return H % 6.0, S, V


"//    CONVERSIONS    \\"

@modulefunc
def rgb_to_hv(rgb):
    r, g, b = rgb
    w, V = minmax(rgb)
    if w: return rgb_to_hsv(rgb)[::2]
    if not V: return nan, 0.0
    if V==r: return ((g - b) / V) % 6.0, V
    if V==g: return ((2.0*V + b - r) / V) % 6.0, V
    if V==b: return ((4.0*V + r - g) / V) % 6.0, V
    raise ValueError(f"{V} ∉ ({r, g, b})")

@modulefunc
def hv_to_rgb(H, V):
    f, i = _h_modf(H)
    match i:
        case 0: return             V,           V*f,            0.0
        case 1: return V*(1.0-f),              V,            0.0
        case 2: return          0.0,              V,           V*f
        case 3: return          0.0,  V*(1.0-f),              V
        case 4: return          V*f,           0.0,              V
        case 5: return             V,           0.0,  V*(1.0-f)
    return V, V, V


@modulefunc
def rgb_to_hsv(rgb):
    r, g, b = rgb
    w, V = minmax(rgb)
    C = (V - w)
    S = (C / V) if V else 0.0
    if V==w or isnan(V): return nan, S, V
    if V==r: return ((g - b) / C) % 6.0, S, V
    if V==g: return ((2.0*C + b - r) / C) % 6.0, S, V
    if V==b: return ((4.0*C + r - g) / C) % 6.0, S, V
    raise ValueError(f"{V} ∉ ({r, g, b})")
    "Tested the old↓ algorithm against the simplified version above, and the simple one "\
    "produced the same outputs but with much fewer (almost none) float rounding errors.  "\
    "Some triadic decimals got a random 5 stuck on the end, but that was it.  Old scrungly "\
    "version was all over the place with repeating 9’s where this↑ one popped out clean, "\
    "one- or two-digit decimals/"
    '''    if V==r: return ((V-b) / C) - ((V-g) / C) % 6.0, S, V
          if V==g: return (2.0 + ((V-r) / C) - ((V-b) / C)) % 6.0, S, V
          if V==b: return (4.0 + ((V-g) / C) - ((V-r) / C)) % 6.0, S, V    '''
 

@modulefunc
def hsv_to_rgb(H, S, V):
    f, i = _h_modf(H)
    match i:
        case 0: return V,                           V*(1.0 - S*(1.0-f)),  V*(1.0 - S)
        case 1: return V*(1.0 - S*f),          V,                            V*(1.0 - S)
        case 2: return V*(1.0 - S),             V,                            V*(1.0 - S*(1.0-f))
        case 3: return V*(1.0 - S),             V*(1.0 - S*f),           V
        case 4: return V*(1.0 - S*(1.0-f)),  V*(1.0 - S),             V
        case 5: return V,                            V*(1.0 - S),             V*(1.0 - S*f)
    return V, V, V


@modulefunc
def rgb_to_hs(rgb):
    r, g, b = rgb
    w, V = minmax(rgb)
    C = (V - w)
    if V==w or isnan(V): return nan, V
    if V==r: return ((g - b) / C) % 6.0, V
    if V==g: return ((2.0*C + b - r) / C) % 6.0, V
    if V==b: return ((4.0*C + r - g) / C) % 6.0, V
    raise ValueError(f"{V} ∉ ({r, g, b})")

@modulefunc
def hs_to_rgb(H, S):
    f, i = _h_modf(H)
    match i:
        case 0: return 1.0,                     (1.0 - S*(1.0-f)),  (1.0 - S)
        case 1: return (1.0 - S*f),          1.0,                      (1.0 - S)
        case 2: return (1.0 - S),             1.0,                      (1.0 - S*(1.0-f))
        case 3: return (1.0 - S),             (1.0 - S*f),            1.0
        case 4: return (1.0 - S*(1.0-f)),  (1.0 - S),               1.0
        case 5: return 1.0,                     (1.0 - S),              (1.0 - S*f)
    return 1.0, 1.0, 1.0


@modulefunc
def rgb_to_h(rgb):
    r, g, b = rgb
    w, V = minmax(rgb)
    C = V - w
    if not C: return nan
    if V==r: return ((g - b) / C) % 6.0
    if V==g: return ((2.0*C + b - r) / C) % 6.0
    if V==b: return ((4.0*C + r - g) / C) % 6.0
    raise ValueError(f"{V} ∉ ({r, g, b})")

@modulefunc
def h_to_rgb(H):
    f, i = _h_modf(H)
    match i:
        case 0: return      1.0,          f,      0.0
        case 1: return (1.0-f),       1.0,      0.0
        case 2: return      0.0,       1.0,         f
        case 3: return      0.0,  (1.0-f),      1.0
        case 4: return          f,       0.0,      1.0
        case 5: return      1.0,       0.0,  (1.0-f)
    return 1.0, 1.0, 1.0

@modulefunc
def h_to_r(H):
    f, i = _h_modf(H)
    match i:
        case None | 5 | 0: return 1.0
        case 1: return (1.0-f)
        case 2 | 3: return 0.0
        case 4: return f
    return 1.0
@modulefunc
def h_to_g(H):
    f, i = _h_modf(H)
    match i:
        case None | 1 | 2: return 1.0
        case 3: return (1.0-f)
        case 4 | 5: return 0.0
        case 0: return f
    return 1.0
@modulefunc
def h_to_b(H):
    f, i = _h_modf(H)
    match i:
        case None | 3 | 4: return 1.0
        case 5: return (1.0-f)
        case 0 | 1: return 0.0
        case 2: return f
    return 1.0


@modulefunc
def hv_to_r(H, V): return h_to_r(H) * V
@modulefunc
def hv_to_g(H, V): return h_to_g(H) * V
@modulefunc
def hv_to_b(H, V): return h_to_b(H) * V

@modulefunc
def hs_to_r(H, S):
    f, i = _h_modf(H)
    match i:
        case None | 5 | 0: return 1.0
        case 1: return (1.0 - S*f)
        case 2 | 3: return (1.0 - S)
        case 4: return (1.0 - S*(1.0-f))
    return 1.0
@modulefunc
def hs_to_g(H, S):
    f, i = _h_modf(H)
    match i:
        case None | 1 | 2: return 1.0
        case 3: return (1.0 - S*f)
        case 4 | 5: return (1.0 - S)
        case 0: return (1.0 - S*(1.0-f))
    return 1.0
@modulefunc
def hs_to_b(H, S):
    f, i = _h_modf(H)
    match i:
        case None | 3 | 4: return 1.0
        case 5: return (1.0 - S*f)
        case 0 | 1: return (1.0 - S)
        case 2: return (1.0 - S*(1.0-f))
    return 1.0

@modulefunc
def hsv_to_r(H, S, V): return hs_to_r(H, S) * V
@modulefunc
def hsv_to_g(H, S, V): return hs_to_g(H, S) * V
@modulefunc
def hsv_to_b(H, S, V): return hs_to_b(H, S) * V


"//    EXTRA    CONVERSIONS    \\"

@modulefunc
def rgb_to_wv(rgb): return minmax(rgb)
@modulefunc
def rgb_to_w(rgb): return min(rgb)
@modulefunc
def rgb_to_v(rgb): return max(rgb)

@modulefunc
def rgb_to_c(rgb):
    w, V = minmax(rgb)
    return V - w
@modulefunc
def rgb_to_cs(rgb):
    w, V = minmax(rgb)
    C = V - w
    return C, ((C / V) if V else 0.0)
@modulefunc
def rgb_to_s(rgb):
    w, V = minmax(rgb)
    return (((V - w) / V) if V else 0.0)
@modulefunc
def rgb_to_sv(rgb):
    w, V = minmax(rgb)
    return (((V - w) / V) if V else 0.0), V

@modulefunc
def wv_to_c(w, V): return V - w
@modulefunc
def wv_to_cs(w, V):
    C = V - w
    return C, ((C / V) if V else 0.0)
@modulefunc
def wv_to_s(w, V): return ((V - w) / V) if V else 0.0

@modulefunc
def vc_to_s(V, C): return (C / V) if V else 0.0
@modulefunc
def vc_to_w(V, C): return V - C

@modulefunc
def cs_to_wv(C, S):
    V = (C / S) if S else 0.0
    return V - C, V
@modulefunc
def cs_to_v(C, S): return (C / S) if S else 0.0
@modulefunc
def cs_to_w(C, S): return ((C / S) if S else 0.0) - C

@modulefunc
def sv_to_w(S, V): return V - S*V
@modulefunc
def sv_to_c(S, V): return S * V


@modulefunc
def _rgbcv_to_h(r, g, b, C, V):
    if not C: return nan
    if V==r: return ((g - b) / C) % 6.0
    if V==g: return ((2.0*C + b - r) / C) % 6.0
    if V==b: return ((4.0*C + r - g) / C) % 6.0
    return nan

@modulefunc
def _hwv_to_rgb(H, w, V):
    f, i = _h_modf(H)
    match (i):
        case (0): return             V,          V*f,            w
        case (1): return V*(1.0-f),             V,             w
        case (2): return            w,             V,           V*f
        case (3): return            w,  V*(1.0-f),             V
        case (4): return         V*f,              w,             V
        case (5): return            V,              w,  V*(1.0-f)
    return V, V, V


#@modulefunc
def rgb_to_xy_0(r, g, b): return ((2.0*r - g - b) / 2.0), ((g - b) * sqrt(3.0) / 2.0)
@modulefunc
def rgb_to_xy(r, g, b):
    return (r - g*_cos_π3rds - b*_cos_π3rds), (g*_sin_π3rds - b*_sin_π3rds)

@modulefunc
def xy_to_rgb(x, y): return hv_to_rgb(atan2(y, x) * 3.0 / pi, hypot(y, x))

@modulefunc
def rgb_to_xy_viahue(rgb):
    hpi = rgb_to_h(rgb) * _π3rds
    return cos(hpi), sin(hpi)
@modulefunc
def rgb_to_x_viahue(rgb): return cos(rgb_to_h(rgb) * _π3rds)
@modulefunc
def rgb_to_y_viahue(rgb): return sin(rgb_to_h(rgb) * _π3rds)


@modulefunc
def hv_to_xy(H, V=1):
    th = H * _π3rds
    return cos(th) * V, sin(th) * V
@modulefunc
def h_to_xy(H):
    th = H * _π3rds
    return cos(th), sin(th)

@modulefunc
def hv_to_x(H, V=1): return cos(H * _π3rds) * V
@modulefunc
def hv_to_y(H, V=1): return sin(H * _π3rds) * V
@modulefunc
def h_to_x(H): return cos(H * _π3rds)
@modulefunc
def h_to_y(H): return sin(H * _π3rds)

@modulefunc
def xy_to_r(x, y): return hv_to_r(atan2(y, x) * 3.0 / pi, hypot(y, x))
@modulefunc
def xy_to_g(x, y): return hv_to_g(atan2(y, x) * 3.0 / pi, hypot(y, x))
@modulefunc
def xy_to_b(x, y): return hv_to_b(atan2(y, x) * 3.0 / pi, hypot(y, x))

@modulefunc
def xy_to_hv(x, y): return atan2(y, x) / _π3rds, hypot(y, x)
@modulefunc
def xy_to_h(x, y): return atan2(y, x) / _π3rds
@modulefunc
def xy_to_v(x, y): return hypot(y, x)

#@modulefunc
def rgb_to_x_0(r, g, b): return (2.0*r - g - b) / 2.0
@modulefunc
def rgb_to_x(r, g, b): return r - (g + b) * _cos_π3rds
#return (r - g*_cos_π3rds - b*_cos_π3rds)
#@modulefunc
def gb_to_y0(g, b): return (g - b) * sqrt(3.0) / 2.0
@modulefunc
def gb_to_y(g, b): return (g - b) * _sin_π3rds


"(r,g,b,w,k) → RGB"

@modulefunc
def hkw_to_rgb(h, k=0, w=0, *, V=255):
    V += w
    return _hwv_to_rgb(h, w, V*(V / (V + k)))

@modulefunc
def rgbkw_to_rgb(r, g, b, k=0, w=0, *, M=255):
    if w:
        r += w
        g += w
        b += w
    V = max(r, g, b)
    MkV = M*(V + k)
    return (r * MkV), (g * MkV), (b * MkV)

#@modulefunc
def rgb_to_rgbkw(r, g, b, *, M=255):
    raise ValueError("Idk yet.")

def _rgb_to_fiwv(rgb):
    w, V = minmax(rgb)
    if w == V: return nan, nan, w, V
    r, g, b = rgb
    if V == r:
        if b == w: return g/V, 0, w, V
        if g == w: return 1.0-(b/V), 5, w, V
    if V == g:
        if r == w: return b/V, 2, w, V
        if b == w: return 1.0-(r/V), 1, w, V
    if V == b:
        if g == w: return r/V, 4, w, V
        if r == w: return 1.0-(g/V), 3, w, V
    return nan, nan, w, V

def _rgb_to_h_via_fiwv(rgb):
    w, V = minmax(rgb)
    if w == V: return nan
    r, g, b = rgb
    if V == r:
        if b == w: return (g/r)
        if g == w: return -(b/r)
    if V == g:
        if r == w: return 2.0 + (b/g)
        if b == w: return 2.0 - (r/g)
    if V == b:
        if g == w: return 4.0 + (r/b)
        if r == w: return 4.0 - (g/b)
    return nan




#################################################################
#    Maybe a bad place to stash a test function so high up the file, but it’s convenient.   #
def _test_refactored_functions():
    
    from itertools import product
    hues = [nan] + [i*0.25 for i in range(6*4)]
    vals = list(range(2, 7, 2))
    dom = list(product(hues, vals))
    fmt = '.2f'
    for h0 in hues:
        r0, g0, b0 = rgb0 = h_to_rgb(h0)
        continue
    print() / print()
    
    stastoste = (0, 6, 1)
    for r in range(*stastoste):
        for g in range(*stastoste):
            for b in range(*stastoste):
                hsv0 = rgb_hsv((r,g,b))
                hls1 = rgb_hls((r,g,b))
                #hls1 = itemgetter(0,2,1)(hls1)
                print()
                print(f"rgb_hsv({r,g,b})  =  {hsv0}")
                print(f"rgb_hls({r,g,b})  =  {hls1}")
    print() / print()
#################################################################

################################################################# 


"//    MIDPOINT    FINDERS    \\"

@modulefunc
def midpoint(p, q, ratio=0.5):
    if p == q: return p
    return p + (q - p) * ratio
@modulefunc
def inverse_midpoint(r, p, ratio=0.5):
    if p == r: return p
    return p + (r - p) / ratio

@modulefunc
def moddiff(p, q, m=6.0):
    "Shortest modular distance between two reals, signed."
    p %= m
    q %= m
    if p == q or isnan(p) or isnan(q): return 0.0
    r = (q - p) % m
    if r > m/2: return r - m
    return r''

@modulefunc
def modmid(p, q, m=6.0, ratio=0.5):
    "Returns the nearest halfway point between two reals modulo 'm'."
    if abs(ratio) > 1:
        ratio = ratio / abs(ratio + 1)
    p %= m
    q %= m
    if p == q or isnan(q): return p
    if isnan(p): return q
    d = (q - p) % m
    m2 = m/2
    if d == m2: return nan
    if d > m2:
        d -= m
    return (p + d * ratio) % m

@modulefunc
def inverse_modmid_L(r, q, m=6.0, ratio=0.5):
    if abs(ratio) > 1:
        ratio = ratio / abs(ratio + 1)
    return inverse_modmid(r, q, m=m, ratio=1-ratio)
@modulefunc
def inverse_modmid(r, p, m=6.0, ratio=0.5):
    if abs(ratio) > 1:
        ratio = ratio / abs(ratio + 1)
    r %= m
    p %= m
    if p == r or isnan(r): return (p + m/2) % m
    if isnan(p): return r
    d = (r - p) % m
    m2 = m/2
    if d == m2: return nan
    if d > m2:
        d -= m
    return (p + (d / ratio)) % m
inverse_modmid_R = modulefunc(inverse_modmid, "inverse_modmid_R")




"//    Fraction Reduction    \\"
'''
def find_fractional(x: float, maxdenom=60, modulus=6, precision=9, *, _recur=0):
    x %= modulus
    if not round(x % 1.0, precision):
        numer, denom = x, 1.0
        return frac_reduce(numer, denom)
    mods_x =  (modulus % x)
    if not round(mods_x, precision):    #    6 % 1.5 = 0
        denom = modulus / x    #    6 / 1.5 = 4
        numer = modulus    #    6
        return frac_reduce(numer, denom)
    for denom in range(2, maxdenom):
        modunit = 1 / denom
        if (not round((x % modunit), precision)) or (not round((x * denom) % 1.0, precision)):    #    0.833 % 0.1667 = 0.0
            numer = denom * x    #    6 * 0.833 == (0.833 / (1 / 6)) = 5
            return frac_reduce(numer, denom)    #    
    if not _recur and (x > 1.0):
        #print(f"{x = }")
        numer, denom = find_fractional(x % 1.0, maxdenom=maxdenom, modulus=modulus, _recur=True)
        return (denom * (x // 1) + numer, denom)
    return None

def igcd(a, b): return gcd(int(a), int(b))

def frac_reduce(numer, denom):
    comdiv = igcd(numer, denom)
    return (numer / comdiv), (denom / comdiv)
'''

"//    //    //    //    ||||    \\    \\    \\    \\"
"//    ARITHMETIC  OPERATIONS    \\"


@modulefunc
def residue6(p):
    p %= 6.0
    if p > 3: return p - 6.0
    return p


"//    Hue→float    FUNCTIONS    \\"

@modulefunc
def f_h_hcos(h, randomize_nan=True):
    if isnan(h):
        if not randomize_nan: return 0.0
        h = randhue()
    return cos(h * _π3rds)
@modulefunc
def f_h_hsin(h, randomize_nan=True):
    if isnan(h):
        if not randomize_nan: return 0.0
        h = randhue()
    return sin(h * _π3rds)
@modulefunc
def f_h_hcossin(h, randomize_nan=True):
    if isnan(h):
        if not randomize_nan: return 0.0, 0.0
        h = randhue()
    th = h * _π3rds
    return cos(th), sin(th)

@modulefunc
def f2_h_hdiffcos(h0, h1): return f_h_hcos(f2_h_huediff(h0, h1))
@modulefunc
def f2_h_hdiffsin(h0, h1): return f_h_hsin(f2_h_huediff(h0, h1))
@modulefunc
def f2_h_hdiffcossin(h0, h1): return f_h_hcossin(f2_h_huediff(h0, h1))


"//    Hue→Hue    FUNCTIONS    \\"

@modulefunc
def f_h_invert(h): return (h + 3.0) % 6.0

@modulefunc
def f_h_rotateG(h): return (h + 2.0) % 6.0
@modulefunc
def f_h_rotateB(h): return (h - 2.0) % 6.0

@modulefunc
def f_h_flipR(h): return (-h) % 6.0
@modulefunc
def f_h_flipG(h): return (4.0 - h) % 6.0
@modulefunc
def f_h_flipB(h): return (8.0 - h) % 6.0

@modulefunc
def f_h_squared(h): return (h * -2.0) % 6.0
@modulefunc
def f_h_sqrt(h):
    hh = (h * -2.0) % 6.0
    return (hh + residue6(h - hh) / 2.0) % 6.0

@modulefunc
def f2_h_huediff(h0, h1):
    "Shortest modular distance between two points (mod 6), signed."
    h0 %= 6.0
    h1 %= 6.0
    if h0 == h1 or isnan(h0) or isnan(h1): return 0.0
    hdiff = (h1 - h0) % 6.0
    if hdiff > 3: return hdiff - 6.0
    return hdiff

@modulefunc
def f2_h_midhue(h0, h1):
    if isnan(h0): return h1
    if isnan(h1): return h0
    hdiff = f2_h_huediff(h0, h1)
    if hdiff == 3: return nan
    return (h0 + hdiff / 2) % 6.0

@modulefunc
def f2_h_inverse_midhue_R(h2, h0, ratio=0.5):
    return f2_h_inverse_midhue(h2, h0, 1.0-ratio)
@modulefunc
def f2_h_inverse_midhue(h2, h1):
    if isnan(h2): return (h1 + 3.0) % 6.0
    if isnan(h1): return h2
    hdiff = f2_h_huediff(h1, h2)
    if hdiff == 3: return nan
    return (h1 + hdiff * 2) % 6.0
f2_h_inverse_midhue_L = modulefunc(
        f2_h_inverse_midhue, 
        "f2_h_inverse_midhue_L")
@modulefunc
def f2_h_reverse_inverse_midhue_R(h0, h2):
    return f2_h_inverse_midhue_R(h2, h0)
@modulefunc
def f2_h_reverse_inverse_midhue(h1, h2):
    return f2_h_inverse_midhue(h2, h1)
f2_h_reverse_inverse_midhue_L = modulefunc(
        f2_h_reverse_inverse_midhue, 
        "f2_h_reverse_inverse_midhue_L")

@modulefunc
def f2_h_flip(h, delta_hue): return (delta_hue * 2 - h) % 6.0
#(h + 2.0 * ((delta_hue - h) % 3.0))

@modulefunc
def f2_h_hue_multiply(h0, h1):
    return (-(h0 + h1)) % 6.0

@modulefunc
def f2_h_n_power(h, n):
    "Returns Hue-like 'h' raised to the real 'n'-th power."
    if isnan(h): return h
    nf, ni = modf(n)
    if n < 0:
        nf = -nf
    if not nf: return (h if (ni % 2) else -(h+h)) % 6.0
    if not (ni % 2): return f2_h_midhue(-(h+h), h, ratio=nf)
    return f2_h_midhue(h, -(h+h), ratio=nf)


@modulefunc
def f2_h_hue_logarithm(h, hb):
    "Returns float 'n', where, for Hue-likes 'h', 'hb':  hb**n == h.  Highly experimental."
    if adiff := f2_h_huediff(hb, hb*-2): return (f2_h_huediff(hb, h) / adiff)
    return 1.0



"//    RGB→RGB    FUNCTIONS    \\"

get_rgb = modulefunc(itemgetter(0, 1, 2), 'get_rgb')
get_gbr = modulefunc(itemgetter(1, 2, 0), 'get_gbr')
get_brg = modulefunc(itemgetter(2, 0, 1), 'get_brg')

get_rbg = modulefunc(itemgetter(0, 2, 1), 'get_rbg')
get_bgr = modulefunc(itemgetter(2, 1, 0), 'get_bgr')
get_grb = modulefunc(itemgetter(1, 0, 2), 'get_grb')

f_rgb_rotateG = modulefunc(get_brg, "f_rgb_rotateG")
f_rgb_rotateB = modulefunc(get_gbr, "f_rgb_rotateB")
f_rgb_flipR = modulefunc(get_rbg, "f_rgb_flipR")
f_rgb_flipG = modulefunc(get_bgr, "f_rgb_flipG")
f_rgb_flipB = modulefunc(get_grb, "f_rgb_flipB")


@modulefunc
def f_rgb_polar_truncate(rgb):
    r, g, b = rgb
    w = rgb_to_w(rgb)
    return r-w, g-w, b-w
@modulefunc
def f_rgb_cap_ceiling(rgb):
    r, g, b = rgb
    if VCAP := constants.VCAP:
        m = (VCAP - rgb_to_v(rgb))
        return r+m, g+m, b+m
    return inf*r, inf*g, inf*b
@modulefunc
def f_rgb_make_rationoid(rgb):
    r, g, b = rgb
    if cd := float_gcd_unsigned(float_gcd_unsigned(r, g), b):
        return r/cd, g/cd, b/cd
    return r, g, b


@modulefunc
def f_rgb_pos(rgb):
    r, g, b = rgb
    return +r, +g, +b
@modulefunc
def f_rgb_neg(rgb):
    r, g, b = rgb
    return -r, -g, -b
@modulefunc
def f_rgb_invert(rgb):
    r, g, b = rgb
    if VCAP := constants.VCAP:
        return (VCAP - r), (VCAP - g), (VCAP - b)
    return -r, -g, -b


@modulefunc
def f2_rgb_union(left, right):
    r0, g0, b0 = left
    r1, g1, b1 = right
    return (r0 if r0>=r1 else r1), \
               (g0 if g0>=g1 else g1), \
               (b0 if b0>=b1 else b1)
@modulefunc
def f2_rgb_intersection(left, right):
    r0, g0, b0 = left
    r1, g1, b1 = right
    return (r0 if r0<=r1 else r1), \
               (g0 if g0<=g1 else g1), \
               (b0 if b0<=b1 else b1)
@modulefunc
def f2_rgb_symmetric_difference(left, right):
    r0, g0, b0 = left
    r1, g1, b1 = right
    return (r0-r1) if r0 >= r1 else (r1-r0), \
             (g0-g1) if g0 >= g1 else (g1-g0), \
             (b0-b1) if b0 >= b1 else (b1-b0)

    
@modulefunc
def f2_rgb_add(left, right):
    r0, g0, b0 = left
    r1, g1, b1 = right
    return (r0 + r1), (g0 + g1), (b0 + b1)
@modulefunc
def f2_rgb_n_add(rgb, n):
    r0, g0, b0 = rgb
    return (r0 + n), (g0 + n), (b0 + n)

@modulefunc
def f2_rgb_sub(left, right):
    r0, g0, b0 = left
    r1, g1, b1 = right
    return (r0 - r1), (g0 - g1), (b0 - b1)
@modulefunc
def f2_rgb_n_sub(rgb, n):
    r0, g0, b0 = rgb
    return (r0 - n), (g0 - n), (b0 - n)

@modulefunc
def f2_rgb_n_mul(rgb, n):
    r0, g0, b0 = rgb
    return (r0 * n), (g0 * n), (b0 * n)
@modulefunc
def f2_rgb_n_truediv(rgb, n):
    r0, g0, b0 = rgb
    if not n: return copysign(inf, r0), copysign(inf, g0), copysign(inf, b0)
    return (r0 / n), (g0 / n), (b0 / n)
@modulefunc
def f2_rgb_n_reverse_truediv(rgb, n):
    r0, g0, b0 = rgb
    return ((n / r0) if r0 else copysign(inf, n)), \
                ((n / g0) if g0 else copysign(inf, n)), \
                ((n / b0) if b0 else copysign(inf, n))


@modulefunc
def f2_rgb_n_as_hue(rgb, hue=nan):
    s, v = rgb_to_sv(rgb)
    return hsv_to_rgb(hue, s, v)
@modulefunc
def f2_rgb_n_saturated(rgb, sat=1.0):
    h, v = rgb_to_hv(rgb)
    return hsv_to_rgb(h, sat, v)
@modulefunc
def f2_rgb_n_as_value(rgb, val=1.0):
    V = rgb_to_v(rgb)
    return f2_rgb_n_mul(rgb, (val / V)) if V else rgb

@modulefunc
def f2_rgb_n_hue_rotate(rgb, hue=nan):
    s, v = rgb_to_sv(rgb)
    return hsv_to_rgb(hue, s, v)
@modulefunc
def f2_rgb_n_saturate(rgb, coefficient=1.0):
    h, s, v = rgb_to_hsv(rgb)
    return hsv_to_rgb(h, s*coefficient, v)


@modulefunc
def f2_rgb_average(rgb0, rgb1):
    r0, g0, b0 = rgb0
    r1, g1, b1 = rgb1
    return (r0 + r1) / 2, (g0 + g1) / 2, (b0 + b1) / 2
@modulefunc
def f2_rgb_inverse_average(rgb2, rgb0):
    r2, g2, b2 = rgb2
    r0, g0, b0 = rgb0
    return (r2*2 - r0), (g2*2 - g0), (b2*2 - b0)
@modulefunc
def f2_rgb_midpoint(rgb0, rgb1):
    return tuple(map(midpoint, rgb0, rgb1))
@modulefunc
def f2_rgb_inverse_midpoint(rgb2, rgb1):
    return tuple(map(inverse_midpoint, rgb2, rgb1))


"//    HV→float    FUNCTIONS    \\"

@modulefunc
def f_hv_hcos(h, v, randomize_nan=True): return f_h_hcos(h, randomize_nan=randomize_nan) * v
@modulefunc
def f_hv_hsin(h, v, randomize_nan=True): return f_h_hsin(h, randomize_nan=randomize_nan) * v
@modulefunc
def f_hv_hcossin(h, v, randomize_nan=True):
    hx, hy = f_h_hcossin(h, randomize_nan=randomize_nan)
    return hx * v, hy * v


"//    HV→HV    FUNCTIONS    \\"

@modulefunc
def f_hv_squared(h, v): return f_h_squared(h), v**2
@modulefunc
def f_hv_sqrt(h, v): return f_h_sqrt(h), v**0.5

@modulefunc
def f2_hv_mul(h0, v0, h1, v1):
    if VCAP := constants.VCAP: return f2_h_hue_multiply(h0, h1), (v0 * (v1/VCAP))
    return f2_h_hue_multiply(h0, h1), (v0 * v1)
@modulefunc
def f2_hv_truediv(h0, v0, h1, v1):
    if VCAP := constants.VCAP: return f2_h_hue_multiply(h0, h1), _zinfdiv(v0, (v1/VCAP))
    return f2_h_hue_multiply(h0, h1), _zinfdiv(v0, v1)

@modulefunc
def f2_hv_n_pow(h, v, n): return f2_h_n_power(h, n), v**n



"//    HSV→HSV    FUNCTIONS    \\"

@modulefunc
def f2_hsv_average(hsv0, hsv1):
    h0, s0, v0 = hsv0
    h1, s1, v1 = hsv1
    rh0 = h0 * _π3rds
    rh1 = h1 * _π3rds
    return (h0 if (h0==h1 or isnan(h0) and isnan(h1)) \
                        else (atan2(sin(rh0) + sin(rh1), cos(rh0) + cos(rh1)) * 3.0 / pi), 
                (s0 + s1) / 2.0, 
                v0 if v0==v1 else ((v0 + v1) / 2.0))

@modulefunc
def f2_hsv_inverse_average(hsv0, hsv1):
    h0, s0, v0 = hsv0
    h1, s1, v1 = hsv1
    return hsv_to_rgb(h0 if (h0==h1 or isnan(h0) and isnan(h1)) else (h0 + (h0 - h1)), 
                                        s0 if s0==s1 else (2.0 * s0 - s1), 
                                        v0 if v0==v1 else (2.0 * v0 - v1))


"//    RGB→Hxx→RGB    FUNCTIONS    \\"


"//    EXPERIMENTAL    FUNCTIONS    \\"


"//    GLOBAL    STUFF    \\"

@modulefunc
def set_VCAP(new_vcap):
    """
        Assigns global constant VCAP to the value of ‘new_vcap’.
    """
    VCAP = constants.VCAP = new_vcap
    return VCAP


@modulefunc
def set_PRECISION(new_prec):
    """
        Assigns global constant PRECISION to the value of ‘new_prec’.
    """
    PRECISION = constants.PRECISION = new_prec
    return PRECISION


__vBlack = (0, 0, 0)
__vRed = (1.0, 0, 0)
__vOrange = (1.0, 0.5, 0.0)
__vYellow = (1.0, 1.0, 0)
__vLime = (0.5, 1.0, 0)
__vGreen = (0, 1.0, 0)
__vTeal = (0, 1.0, 0.5)
__vCyan = (0, 1.0, 1.0)
__vAqua = (0, 0.5, 1.0)
__vBlue = (0, 0, 1.0)
__vIndigo = (0.5, 0, 1.0)
__vMagenta = (1.0, 0, 1.0)
__vFuchsia = (1.0, 0, 0.5)

__vGray = (0.5, 0.5, 0.5)
__vWhite = (1, 1, 1)


tuple(map(modulefunc, [
    '__vBlack', '__vGray', '__vWhite', 
    '__vRed', '__vOrange', '__vYellow', '__vLime', '__vGreen', '__vTeal', 
    '__vCyan', '__vAqua', '__vBlue', '__vIndigo', '__vMagenta', '__vFuchsia'
    ]))




if __name__ == '__main__':
    
    
    print() / print()
    #import tkinter
