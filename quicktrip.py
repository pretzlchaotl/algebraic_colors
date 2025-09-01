
import sys
sys.path.append(__file__.rsplit('algebraic_colors', 1)[0])
from algebraic_colors.cf import color_functions as cf
from algebraic_colors.rigorous.quickhue import \
    hue, hv_object, is_scalar, infzdiv
from math import gcd as _gcd, nan, copysign
from operator import attrgetter, itemgetter
from _collections import _tuplegetter
from functools import lru_cache

#from TandT.addedmanually.getem_ext import memprop


__all__ = []
def modulefunc(f, name: str=None):
    if not name and isinstance(f, str) and f:
        name = f
    __all__.append(name or f.__name__)
    return f

def modulefuncs(*names):
    tuple(map(modulefunc, names))


get_rgb = itemgetter(0, 1, 2)
get_brg = itemgetter(2, 0, 1)
get_gbr = itemgetter(1, 2, 0)
get_rbg = itemgetter(0, 2, 1)
get_bgr = itemgetter(2, 1, 0)
get_grb = itemgetter(1, 0, 2)


@modulefunc
def float_gcd(a, b):
    "Get the greatest common denominator of two floats."
    if a < 0:
        a = abs(a)
    if b < 0:
        b = abs(b)
    if a < b:
        a, b = b, a
    while b:
        b, a = (a % b), b
    return a

@modulefunc
def gcd(a, b):
    "Get the greatest common denominator of two floats or ints."
    try: return _gcd(a, b)
    except TypeError:
        return float_gcd(a, b)


_get_ends = itemgetter(0, -1)
def minmax(rgb): return _get_ends(sorted(rgb))

#@modulefunc
#def zdiv(a, b):
#    "Returns a/b if b != 0, returns 0 otherwise."
#    return b and (a / b)


@modulefunc
def midpoint(p, q, ratio=0.5):
    return p + (q - p) * ratio
@modulefunc
def inverse_midpoint(o, q, ratio=0.5):
    return q + (o - q) / ratio


@modulefunc
def rgb_to_h(rgb):
    "Get the redindex of a triple’s hue."
    w, V = minmax(rgb)
    return _rgbwV_to_h(*rgb, w, V)
@modulefunc
def rgb_to_hv(rgb):
    "Convert a triple into (H, V), where H is the redindex of its hue, and V is its max."
    w, V = minmax(rgb)
    return _rgbwV_to_h(*rgb, w, V), V

def _rgbwV_to_h(r, g, b, w, V):
    C = V - w
    if not C: return nan
    if V==r: return ((g - b) / C) % 6.0
    if V==g: return ((2.0*C + b - r) / C) % 6.0
    if V==b: return ((4.0*C + r - g) / C) % 6.0
    raise ValueError(f"{V} ∉ {(r, g, b)}")

rgb_to_hsv = cf.rgb_to_hsv


def rationalize(rgb0, rgb1):
    "Converts two rationoid triples’ rgb values into forms that can can co-operate."
    r0, g0, b0 = rgb0
    r1, g1, b1 = rgb1
    v0 = max(rgb0)
    v1 = max(rgb1)
    if (0 != v0 != v1 != 0): return (r0, g0, b0, r1, g1, b1)
    return (r0*v1, g0*v1, b0*v1, r1*v0, g1*v0, b1*v0)



def is_nullary(self):
    "A triple is nullary if all its values are zero."
    return not any(self)
def is_primary(self):
    "A triple is primary if its middle is equal to zero and its V is not."
    return self.count(0) == 2
def is_secondary(self):
    "A triple is secondary if its V is non-zero and equal to its middle."
    w, m, V = sorted(self)
    return (w == 0 != m == V)
def is_tertiary(self):
    "An Rarionoid is tertiary if its V is twice its middle and non-zero."
    w, m, V = sorted(self)
    return (w == 0 != m == V / 2)
def is_hexradic(self):
    "A triple is hexradic if it is primary or secondary."
    w, m, V = sorted(self)
    return (w == 0 == m != V) or (w == 0 != m == V)
def is_dodecaradic(self):
    "A triple is dodecradic if it is primary, secondary, or tertiary."
    w, m, V = sorted(self)
    return (w == 0 == m != V) or ((w == 0 != m) and not (V/2 != m != V))
    #or (w == 0 != m == V/2)
def is_whole(self):
    "A triple is whole if its maximum value is equal to one or zero."
    return not (1 != max(self) != 0)



h_to_rgb = cf.h_to_rgb
hv_to_rgb = cf.hv_to_rgb
hsv_to_rgb = cf.hsv_to_rgb
modulefuncs("rgb_to_h", "rgb_to_hv", "hv_to_rgb", "h_to_rgb")


@modulefunc
class symmetricyclic_triple(tuple):
    
    cap: int = None
    
    r = _tuplegetter(0, "red")
    g = _tuplegetter(1, "green")
    b = _tuplegetter(2, "blue")
    
    @property
    def rgb(self): return self
    @property
    @lru_cache
    def hv(self): return hv_object.from_rgb_object(self)
    saturation = property(cf.rgb_to_s)
    
    @classmethod
    def from_iterable(cls, rgb): return cls(*rgb)
    @classmethod
    def from_hue_object(cls, h: hue): return cls(*h.as_rgb())
    @classmethod
    def from_hue_redindex(cls, h: hue): return cls(*h_to_rgb(h))
    @classmethod
    def from_hv_object(cls, hv: hv_object): return cls(*hv.as_rgb())
    @classmethod
    def from_H(cls, h): return cls(*h_to_rgb(h))
    @classmethod
    def from_HV(cls, h, v): return cls(*hv_to_rgb(h, v))
    @classmethod
    def from_HSV(cls, h, s, v): return cls(*hsv_to_rgb(h, s, v))
    @classmethod
    def _from_rgb_override(cls, r, g, b): return tuple.__new__(cls, (r, g, b))
    @classmethod
    def _from_iterable_override(cls, iterable):return cls._from_rgb_override(*iterable)
    
    def __new__(cls, r=0, g=0, b=0):
        return tuple.__new__(cls, (r, g, b))
    
    get_hue = (hue.from_rgb_object)
    get_hue_redindex = (rgb_to_h)
    get_V = (max)
    get_hv_object = (hv_object.from_rgb_object)
    get_HV = (rgb_to_hv)
    get_HSV = (rgb_to_hsv)
    get_Sv = cf.rgb_to_s
    
    def replace_HSV(self, h: hue=None, s: float=None, v: float=None):
        h0, s0, v0 = self.get_HSV()
        return self.from_HSV(h0 if h is None else h, \
                                            s0 if s is None else s, \
                                            v0 if v is None else v)
    def replace_H(self, h: hue):
        h0, s0, v0 = self.get_HSV()
        return self.from_HSV(h, s0, v0)
    def replace_S(self, s: float):
        h0, s0, v0 = self.get_HSV()
        return self.from_HSV(h0, s, v0)
    def replace_V(self, v: float):
        h0, s0, v0 = self.get_HSV()
        return self.from_HSV(h0, s0, v)
    
    def __hash__(self): return tuple.__hash__(self)
    
    def __format__(self, format_spec=""):
        r, g, b = self
        return f"({r:{format_spec}}, {g:{format_spec}}, {b:{format_spec}})"
    def __str__(self): return self.__format__(".8g")
    def __repr__(self): return f"triple{self:}"
    
    #        //        (Θ) → O        \\        #
    def __bool__(self): return any(self)
    is_nullary = is_nullary
    is_primary = is_primary
    is_secondary = is_secondary
    is_tertiary = is_tertiary
    is_hexradic = is_hexradic
    is_dodecaradic = is_dodecaradic
    is_whole = is_whole
    
    def rotate_green(self): return self._from_iterable_override(get_gbr(self))
    def rotate_blue(self): return self._from_iterable_override(get_brg(self))
    def flip_red(self): return self._from_iterable_override(get_rbg(self))
    def flip_green(self): return self._from_iterable_override(get_bgr(self))
    def flip_blue(self): return self._from_iterable_override(get_grb(self))

    def negative(self):
        r, g, b = self
        return type(self)(-r, -g, -b)
    def invert(self):
        r, g, b = self
        if cap := self.cap:
            return type(self)(cap-r, cap-g, cap-b)
        return type(self)(-r, -g, -b)
    def polar_truncate(self):
        if w := min(self):
            r, g, b = self
            return type(self)(r-w, g-w, b-w)
        return self
    def cap_ceiling(self):
        cap = self.cap
        if vn := cap and cap - max(self):
            r, g, b = self
            return type(self)(r+vn, g+vn, b+vn)
        return self
    
    __neg__ = negative
    __invert__ = invert = negative
    __floor__ = __trunc__ = polar_truncate
    __ceil__ = cap_ceiling
   
    hue_sign = get_hue
    __abs__ = absolute_value = get_V
    
    def midpigment(self, other):
        if not isinstance(other, triple): return NotImplemented
        return self._from_iterable_override(map(midpoint, self, other))
    def inverse_midpigment(self, other):
        if not isinstance(other, triple): return NotImplemented
        return self._from_iterable_override(map(inverse_midpoint, self, other))

triple = symmetricyclic_triple
modulefunc('triple')


#print(triple._namespace == triple.__dict__, '', sep='\n')    False
#print(set(triple._namespace) - set(triple.__dict__), '', sep='\n')    {'__qualname__'}
#print(set(triple.__dict__) - set(triple._namespace), '', sep='\n')    {'__doc__', '_namespace', '__dict__'}


@modulefunc
class rationoid(triple):
    
    def __new__(cls, r=0, g=0, b=0):
        w = min(r, g, b)
        if (w < 0):
            r -= w
            g -= w
            b -= w
        if cd := gcd(gcd(r, g), b):
            return triple.__new__(cls, int(r/cd), int(g/cd), int(b/cd))
        return triple.__new__(cls, r, g, b)
    
    def __hash__(self): return tuple.__hash__(self)
    
    def __str__(self): return self.__format__("d")
    def __repr__(self): return f"rationoid{self:}"
    
    #        //        (Tq) → Tq        \\        #
    def invert(self):
        r, g, b = self
        return rationoid(-r, -g, -b)
    
    __invert__ = __neg__ = invert
    
    #        //        (Tq, Tq) → B        \\        #
    def __eq__(self, other):
        if not isinstance(other, rationoid): return False
        return super().__eq__(other)
    def __ne__(self, other):
        if not isinstance(other, rationoid): return True
        return super().__ne__(other)
    
    #        //        (Tq, Tq) → Tq        \\        #
    def triple_add(self, other):
        if not isinstance(other, rationoid): return NotImplemented
        r0, g0, b0, r1, g1, b1 = rationalize(self, other)
        return rationoid(r0 + r1, g0 + g1, b0 + b1)
    def triple_subtract(self, other):
        if not isinstance(other, rationoid): return NotImplemented
        r0, g0, b0, r1, g1, b1 = rationalize(self, other)
        return rationoid(r0 - r1, g0 - g1, b0 - b1)
    
    def triple_union(self, other):
        if not isinstance(other, rationoid): return NotImplemented
        r0, g0, b0, r1, g1, b1 = rationalize(self, other)
        return rationoid((r0 if r0 >= r1 else r1), 
                                            (g0 if g0 >= g1 else g1), 
                                            (b0 if b0 >= b1 else b1))
    def triple_intersection(self, other):
        if not isinstance(other, rationoid): return NotImplemented
        r0, g0, b0, r1, g1, b1 = rationalize(self, other)
        return rationoid((r0 if r0 <= r1 else r1), 
                                            (g0 if g0 <= g1 else g1), 
                                            (b0 if b0 <= b1 else b1))
    def triple_symmetric_difference(self, other):
        if not isinstance(other, rationoid): return NotImplemented
        r0, g0, b0, r1, g1, b1 = rationalize(self, other)
        return rationoid(abs(r0 - r1), abs(g0 - g1), abs(b0 - b1))
    
    __add__ = triple_add
    __sub__ = triple_subtract
    __ror__ = __or__= triple_union
    __rand__ = __and__ = triple_intersection
    __rxor__ = __xor__ = triple_symmetric_difference
    
    
    def hv_multiply(self, other):
        if not isinstance(other, rationoid): return NotImplemented
        return self.from_hv_object(self.hv * other.hv)
    def hv_divide(self, other):
        if not isinstance(other, rationoid): return NotImplemented
        return self.from_hv_object(self.hv / other.hv)
    
    def multiply(self, other):
        if isinstance(other, rationoid): return self.hv_multiply(other)
        if is_scalar(other): return self.from_hv_object(self.hv.scalar_multiply(other))
        return NotImplemented
    def divide(self, other):
        if isinstance(other, rationoid): return self.hv_divide(other)
        if is_scalar(other): return self.from_hv_object(self.hv.scalar_divide(other))
        return NotImplemented
    
    def reverse_scalar_divide(self, other):
        if is_scalar(other): return self.from_hv_object(self.hv.reverse_scalar_divide(other))
        return NotImplemented
    
    def scalar_power(self, other):
        if is_scalar(other): return self.from_hv_object(self.hv.scalar_power(other))
        return NotImplemented
    
    #            #            #            #            #
    __mul__ = multiply
    __truediv__ = divide
    __rmul__ = __mul__
    __rtruediv__ = reverse_scalar_divide
    
    __pow__ = scalar_power
#    
#    __lshift__ = reverse_hv_diff
#    __rshift__ = hv_diff
    
    def midpigment(self, other, ratio=0.5):
        if not isinstance(other, rationoid): return NotImplemented
        r0, g0, b0, r1, g1, b1 = rationalize(self, other)
        return rationoid(r0 + (r1 - r0) * ratio, g0 + (g1 - g0) * ratio, b0 + (b1 - b0) * ratio)
    def inverse_midpigment(self, other, ratio=0.5):
        if not isinstance(other, rationoid): return NotImplemented
        r0, g0, b0, r1, g1, b1 = rationalize(self, other)
        return rationoid(r1 + (r0 - r1) / ratio, g1 + (g0 - g1) / ratio, b1 + (b0 - b1) / ratio)
    



@modulefunc
class tripole(triple):
    
    cap = None
    
    def __new__(cls, r=0, g=0, b=0):
        if w := min(r, g, b):
            return triple.__new__(cls, r-w, g-w, b-w)
        return triple.__new__(cls, r, g, b)
    
    def __hash__(self): return tuple.__hash__(self)
    
    def __str__(self): return self.__format__(".8g")
    def __repr__(self): return f"tripole{self:}"
    
    #        //        (Th) → Th        \\        #
    def invert(self):
        r, g, b = self
        return tripole(-r, -g, -b)
    def polar_truncate(self):
        return self
    def cap_ceiling(self):
        cap = self.cap
        if vn := cap and cap - max(self):
            r, g, b = self
            return tripole(r and r+vn, g and g+vn, b and b+vn)
        return self
    
    __invert__ = invert
    __neg__ = negative = invert
    __floor__ = __trunc__ = polar_truncate
    __ceil__ = cap_ceiling
    
    #        //        (Th, Th) → B        \\        #
    def __eq__(self, other):
        if not isinstance(other, triple_nonrat): return False
        return super().__eq__(other)
    def __ne__(self, other):
        if not isinstance(other, triple_nonrat): return True
        return super().__ne__(other)
    
    #        //        (Th, Th) → Th        \\        #
    def triple_add(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripole(r0 + r1, g0 + g1, b0 + b1)
    def triple_subtract(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripole(r0 - r1, g0 - g1, b0 - b1)
    
    def triple_union(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripole((r0 if r0 >= r1 else r1), 
                                            (g0 if g0 >= g1 else g1), 
                                            (b0 if b0 >= b1 else b1))
    def triple_intersection(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripole((r0 if r0 <= r1 else r1), 
                                            (g0 if g0 <= g1 else g1), 
                                            (b0 if b0 <= b1 else b1))
    def triple_symmetric_difference(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripole(abs(r0 - r1), abs(g0 - g1), abs(b0 - b1))
    
    #        //        (Th, ℝ) → Th        \\        #
    def scalar_multiply(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        return tripole(r0 * other, g0 * other, b0 * other)
    def scalar_divide(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        if not other: return self
        return tripole(r0 / other, g0 / other, b0 / other)
    def reverse_scalar_divide(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        return tripole(zdiv(other, r0), zdiv(other, g0), zdiv(other, b0))
    
    __add__ = triple_add
    __sub__ = triple_subtract
    __ror__ = __or__= triple_union
    __rand__ = __and__ = triple_intersection
    __rxor__ = __xor__ = triple_symmetric_difference
    
    def hv_multiply(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        return self.from_hv_object(self.hv * other.hv)
    def hv_divide(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        return self.from_hv_object(self.hv / other.hv)
    
    def multiply(self, other):
        if isinstance(other, triple_nonrat): return self.hv_multiply(other)
        if is_scalar(other): return self.scalar_multiply(other)
        return NotImplemented
    def divide(self, other):
        if isinstance(other, triple_nonrat): return self.hv_divide(other)
        if is_scalar(other): return self.scalar_multiply(other)
        return NotImplemented
    
    def scalar_power(self, other):
        if is_scalar(other): return self.from_hv_object(self.hv.scalar_power(other))
        return NotImplemented
    
    #            #            #            #            #
    __mul__ = multiply
    __truediv__ = divide
    __rmul__ = __mul__
    __rtruediv__ = reverse_scalar_divide
    
    __pow__ = scalar_power
    
    #__lshift__ = reverse_hv_diff
    #__rshift__ = hv_diff
    '''
    __rmul__ = __mul__ = scalar_multiply
    __truediv__ = scalar_divide
    __rtruediv__ = reverse_scalar_divide
    '''
    
    def midpigment(self, other, ratio=0.5):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripole(r0 + (r1 - r0) * ratio, g0 + (g1 - g0) * ratio, b0 + (b1 - b0) * ratio)
    def inverse_midpigment(self, other, ratio=0.5):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripole(r1 + (r0 - r1) / ratio, g1 + (g0 - g1) / ratio, b1 + (b0 - b1) / ratio)



@modulefunc
class tripcoloroid(triple):
    "This class is specifically meant for subclassing and free-form arithmetic operations.  It has no normalization implementation, so be warned that it might break when not handled carefully."
    
    cap = None
    
    def __new__(cls, r=0, g=0, b=0):
        return triple.__new__(cls, r, g, b)
    
    def __hash__(self): return tuple.__hash__(self)
    
    def __str__(self): return self.__format__(".8g")
    def __repr__(self): return f"tripcoloroid{self:}"
    
    #        //        (Th) → Th        \\        #
    def negative(self):
        r, g, b = self
        return tripcoloroid(-r, -g, -b)
    def invert(self):
        r, g, b = self
        if cap := self.cap:
            return tripcoloroid(copysign(cap, r)-r, copysign(cap, g)-g, copysign(cap, b)-b)
        return tripcoloroid(-r, -g, -b)
    
    def polar_truncate(self):
        if w := abs(min(self, key=abs)):
            r, g, b = self
            return tripcoloroid(r-copysign(w, r), g-copysign(w, g), b-copysign(w, b))
        return self
    def cap_ceiling(self):
        cap = self.cap
        if vn := cap and cap - abs(max(self, key=abs)):
            r, g, b = self
            return tripcoloroid(r+copysign(vn, r), g+copysign(vn, g), b+copysign(vn, b))
        return self
    
    __neg__ = negative
    __invert__ = invert
    __floor__ = __trunc__ = polar_truncate
    __ceil__ = cap_ceiling
    
    #        //        (Th, Th) → B        \\        #
    def __eq__(self, other):
        if not isinstance(other, triple_nonrat): return False
        return super().__eq__(other)
    def __ne__(self, other):
        if not isinstance(other, triple_nonrat): return True
        return super().__ne__(other)
    
    #        //        (Th, Th) → Th        \\        #
    def triple_add(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcoloroid(r0 + r1, g0 + g1, b0 + b1)
    def triple_subtract(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcoloroid(r0 - r1, g0 - g1, b0 - b1)
    
    def triple_union(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcoloroid(max(r0, r1, key=abs), 
                                            max(g0, g1, key=abs), 
                                            max(b0, b1, key=abs))
    def triple_intersection(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcoloroid(min(r0, r1, key=abs), 
                                            min(g0, g1, key=abs), 
                                            min(b0, b1, key=abs))
    def triple_symmetric_difference(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        return (self | other) - (self & other)
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcoloroid(abs(r0 - r1), abs(g0 - g1), abs(b0 - b1))
    
    #        //        (Th, ℝ) → Th        \\        #
    def scalar_multiply(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        return tripcoloroid(r0 * other, g0 * other, b0 * other)
    def scalar_divide(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        if not other: return self
        return tripcoloroid(r0 / other, g0 / other, b0 / other)
    def reverse_scalar_divide(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        return tripcoloroid(zdiv(other, r0), zdiv(other, g0), zdiv(other, b0))
    
    __add__ = triple_add
    __sub__ = triple_subtract
    __ror__ = __or__= triple_union
    __rand__ = __and__ = triple_intersection
    __rxor__ = __xor__ = triple_symmetric_difference
    
    
    def hv_multiply(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        hv0 = self.hv
        hv1 = other.hv
        if cap := self.cap:
            return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v * (hv1.v / self.cap))
#            (self.hv * (other.hv / self.cap))
        return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v * hv1.v)
        #from_hv_object(self.hv.replace(self.hv.h * other.hv.h, self.hv.v * other.hv.v))
    def hv_divide(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        hv0 = self.hv
        hv1 = other.hv
        if cap := self.cap:
            return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v / (hv1.v / self.cap))
        return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v / hv1.v)
    
    def multiply(self, other):
        if isinstance(other, triple_nonrat): return self.hv_multiply(other)
        if is_scalar(other): return self.scalar_multiply(other)
        return NotImplemented
    def divide(self, other):
        if isinstance(other, triple_nonrat): return self.hv_divide(other)
        if is_scalar(other): return self.scalar_multiply(other)
        return NotImplemented
    
    def scalar_power(self, other):
        if is_scalar(other): return self.from_hv_object(self.hv.scalar_power(other))
        return NotImplemented
    
    #            #            #            #            #
    __mul__ = multiply
    __truediv__ = divide
    __rmul__ = __mul__
    __rtruediv__ = reverse_scalar_divide
    
    __pow__ = scalar_power
    
    #__lshift__ = reverse_hv_diff
    #__rshift__ = hv_diff
    '''
    __rmul__ = __mul__ = scalar_multiply
    __truediv__ = scalar_divide
    __rtruediv__ = reverse_scalar_divide
    '''
    
    def midpigment(self, other, ratio=0.5):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcoloroid(r0 + (r1 - r0) * ratio, g0 + (g1 - g0) * ratio, b0 + (b1 - b0) * ratio)
    def inverse_midpigment(self, other, ratio=0.5):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcoloroid(r1 + (r0 - r1) / ratio, g1 + (g0 - g1) / ratio, b1 + (b0 - b1) / ratio)



@modulefunc
class tripcolor(triple):
    
    cap = 255
    
    def __new__(cls, r=0, g=0, b=0):
        w = min(r, g, b)
        if w < 0:
            r -= w
            g -= w
            b -= w
        cap = cls.cap
        if V := cap and max(r, g, b):
            if V > cap:
                vx = cap / V
                return triple.__new__(cls, r*vx, g*vx, b*vx)
        return triple.__new__(cls, r, g, b)
    
    def __hash__(self): return tuple.__hash__(self)
    
    def __str__(self): return self.__format__(".8g")
    def __repr__(self): return f"tripcolor{self:}"
    
    #        //        (Th) → Th        \\        #
    def negative(self):
        r, g, b = self
        return tripcolor(-r, -g, -b)
    def invert(self):
        r, g, b = self
        if cap := self.cap:
            return tripcolor(cap-r, cap-g, cap-b)
        return tripcolor(-r, -g, -b)
    
    def polar_truncate(self):
        if w := min(self):
            r, g, b = self
            return self._from_rgb_override(r-w, g-w, b-w)
        return self
    def cap_ceiling(self):
        cap = self.cap
        if vn := cap and cap - max(self):
            r, g, b = self
            return self._from_rgb_override(r+vn, g+vn, b+vn)
        return self
    
    __neg__ = negative
    __invert__ = invert
    __floor__ = __trunc__ = polar_truncate
    __ceil__ = cap_ceiling
    
    #        //        (Th, Th) → B        \\        #
    def __eq__(self, other):
        if not isinstance(other, triple_nonrat): return False
        return super().__eq__(other)
    def __ne__(self, other):
        if not isinstance(other, triple_nonrat): return True
        return super().__ne__(other)
    
    #        //        (Th, Th) → Th        \\        #
    def triple_add(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcolor(r0 + r1, g0 + g1, b0 + b1)
    def triple_subtract(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcolor(r0 - r1, g0 - g1, b0 - b1)
    
    def triple_union(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcolor((r0 if r0 >= r1 else r1), 
                                            (g0 if g0 >= g1 else g1), 
                                            (b0 if b0 >= b1 else b1))
    def triple_intersection(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcolor((r0 if r0 <= r1 else r1), 
                                            (g0 if g0 <= g1 else g1), 
                                            (b0 if b0 <= b1 else b1))
    def triple_symmetric_difference(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcolor(abs(r0 - r1), abs(g0 - g1), abs(b0 - b1))
    
    #        //        (Th, ℝ) → Th        \\        #
    def scalar_multiply(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        return tripcolor(r0 * other, g0 * other, b0 * other)
    def scalar_divide(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        if not other: return self
        return tripcolor(r0 / other, g0 / other, b0 / other)
    def reverse_scalar_divide(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        return tripcolor(zdiv(other, r0), zdiv(other, g0), zdiv(other, b0))
    
    __add__ = triple_add
    __sub__ = triple_subtract
    __ror__ = __or__= triple_union
    __rand__ = __and__ = triple_intersection
    __rxor__ = __xor__ = triple_symmetric_difference
    
    def hv_multiply(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        hv0 = self.hv
        hv1 = other.hv
        if cap := self.cap:
            return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v * (hv1.v / self.cap))
#            (self.hv * (other.hv / self.cap))
        return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v * hv1.v)
        #from_hv_object(self.hv.replace(self.hv.h * other.hv.h, self.hv.v * other.hv.v))
    def hv_divide(self, other):
        if not isinstance(other, triple_nonrat): return NotImplemented
        hv0 = self.hv
        hv1 = other.hv
        if cap := self.cap:
            return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v / (hv1.v / self.cap))
        return self.from_HV(-(hv0.h.redindex + hv1.h.redindex), hv0.v / hv1.v)
    
    def multiply(self, other):
        if isinstance(other, triple_nonrat): return self.hv_multiply(other)
        if is_scalar(other): return self.scalar_multiply(other)
        return NotImplemented
    def divide(self, other):
        if isinstance(other, triple_nonrat): return self.hv_divide(other)
        if is_scalar(other): return self.scalar_multiply(other)
        return NotImplemented
    
    def scalar_power(self, other):
        if is_scalar(other): return self.from_hv_object(self.hv.scalar_power(other))
        return NotImplemented
    
    #            #            #            #            #
    __mul__ = multiply
    __truediv__ = divide
    __rmul__ = __mul__
    __rtruediv__ = reverse_scalar_divide
    
    __pow__ = scalar_power
    
    #__lshift__ = reverse_hv_diff
    #__rshift__ = hv_diff
    '''
    __rmul__ = __mul__ = scalar_multiply
    __truediv__ = scalar_divide
    __rtruediv__ = reverse_scalar_divide
    '''
    
    def midpigment(self, other, ratio=0.5):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcolor(r0 + (r1 - r0) * ratio, g0 + (g1 - g0) * ratio, b0 + (b1 - b0) * ratio)
    def inverse_midpigment(self, other, ratio=0.5):
        if not isinstance(other, triple_nonrat): return NotImplemented
        r0, g0, b0 = self
        r1, g1, b1 = other
        return tripcolor(r1 + (r0 - r1) / ratio, g1 + (g0 - g1) / ratio, b1 + (b0 - b1) / ratio)

triple_nonrat = (tripole, tripcoloroid, tripcolor)



@modulefunc
class hv_tripole(hv_object):
    __slots__ = ("rgb",)
    rgb: tripole
    
    r = property(attrgetter("rgb.r"))
    g = property(attrgetter("rgb.g"))
    b = property(attrgetter("rgb.b"))
    
    @classmethod
    def from_rgb(cls, r=0, g=0, b=0):
        rgb = tripole(r, g, b)
        self = object.__new__(cls)
        hv = hv_object(*rgb.get_HV())
        self.h = hv.h
        self.v = hv.v
        self.rgb = rgb
        return self
    @classmethod
    def from_hv(cls, h: hue=hue.w, v: float=0.0):
        return cls.from_hv_object(hv_object(h, v))
    @classmethod
    def from_rgb_object(cls, rgb):
        return cls.from_rgb(*rgb)
    @classmethod
    def from_hv_object(cls, hv: hv_object=hv_object.w1):
        self = object.__new__(cls)
        self.h = hv.h
        self.v = hv.v
        self.rgb = tripole.from_hv_object(self)
        return self
    
#    def __new__(cls, h: hue=hue.w, v: float=1.0):
    def __new__(cls, *args):
        argslen = len(args)
        if argslen == 1:
            args, = args
            argslen = len(args)
        if not argslen: return cls.from_hv(hue.w, 0.0)
        if argslen == 3: return cls.from_rgb(*args)
        if argslen == 2: return cls.from_hv(*args)
        raise ValueError(f"invalid number of inputs: {argslen};    {args}")
    
    def replace(self, h=None, v=None):
        return hv_tripole.from_hv(self.h if h is None else h, 
                                                   self.v if v is None else v)
    
    def __str__(self): return f"[{self.h:|c}, {self.v}]"
    def __repr__(self): return f"hv_tripole({self.h}, {self.v})"
    
    def __iter__(self): yield from self.rgb
    def __getitem__(self, key): return self.rgb[key]
    
    #        //        (Th, Th) → Th        \\        #
    def triple_add(self, other):
        if not isinstance(other, triple_nonrat_plus): return NotImplemented
        r0, g0, b0 = self.rgb
        r1, g1, b1 = other.rgb
        return self.from_rgb(r0 + r1, g0 + g1, b0 + b1)
    def triple_subtract(self, other):
        if not isinstance(other, triple_nonrat_plus): return NotImplemented
        r0, g0, b0 = self.rgb
        r1, g1, b1 = other.rgb
        return self.from_rgb(r0 - r1, g0 - g1, b0 - b1)
    def reverse_triple_subtract(self, other):
        if not isinstance(other, triple_nonrat_plus): return NotImplemented
        r0, g0, b0 = other.rgb
        r1, g1, b1 = self.rgb
        return self.from_rgb(r0 - r1, g0 - g1, b0 - b1)
    
    def triple_union(self, other):
        if not isinstance(other, triple_nonrat_plus): return NotImplemented
        r0, g0, b0 = other.rgb
        r1, g1, b1 = self.rgb
        return self.from_rgb((r0 if r0 >= r1 else r1), 
                                            (g0 if g0 >= g1 else g1), 
                                            (b0 if b0 >= b1 else b1))
    def triple_intersection(self, other):
        if not isinstance(other, triple_nonrat_plus): return NotImplemented
        r0, g0, b0 = other.rgb
        r1, g1, b1 = self.rgb
        return self.from_rgb((r0 if r0 <= r1 else r1), 
                                            (g0 if g0 <= g1 else g1), 
                                            (b0 if b0 <= b1 else b1))
    def triple_symmetric_difference(self, other):
        if not isinstance(other, triple_nonrat_plus): return NotImplemented
        r0, g0, b0 = other.rgb
        r1, g1, b1 = self.rgb
        return self.from_rgb(abs(r0 - r1), abs(g0 - g1), abs(b0 - b1))

    
    #        //        (Th, ℝ) → Th        \\        #
    def scalar_multiply(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        return self.from_rgb_object(r0 * other, g0 * other, b0 * other)
    def scalar_divide(self, other):
        if not is_scalar(other): return NotImplemented
        r0, g0, b0 = self
        if not other: return self
        return self.from_rgb_object(r0 / other, g0 / other, b0 / other)
    def reverse_scalar_divide(self, other):
        if not is_scalar(other): return NotImplementednted
        r0, g0, b0 = self
        return self.from_rgb_object(zdiv(other, r0), zdiv(other, g0), zdiv(other, b0))
    
    __add__ = triple_add
    __sub__ = triple_subtract
    __ror__ = __or__= triple_union
    __rand__ = __and__ = triple_intersection
    __rxor__ = __xor__ = triple_symmetric_difference
    
    def hv_multiply(self, other):
        return self.from_hv_object(super().multiply(other))
    def hv_divide(self, other):
        return self.from_hv_object(super().divide(other))
    
    def multiply(self, other):
        if isinstance(other, hv_object): return self.replace(self.h * other.h, self.v * other.v)
        if isinstance(other, hue): return self.replace(self.h * other, self.v)
        return self.scalar_multiply(other)
    def divide(self, other):
        if isinstance(other, hv_object): return self.replace(self.h * other.h, infzdiv(self.v, other.v))
        if isinstance(other, hue): return self.replace(self.h * other, self.v)
        return self.scalar_divide(other)
    
    def scalar_power(self, other):
        if is_scalar(other): return self.from_hv_object(super().scalar_power(other))
        return NotImplemented
    
    #            #            #            #            #
    __mul__ = multiply
    __truediv__ = divide
    __rmul__ = __mul__
    __rtruediv__ = reverse_scalar_divide
    
    __pow__ = scalar_power
    
    #__lshift__ = reverse_hv_diff
    #__rshift__ = hv_diff
    '''
    __rmul__ = __mul__ = scalar_multiply
    __truediv__ = scalar_divide
    __rtruediv__ = reverse_scalar_divide
    '''
    

triple_nonrat_plus = (*triple_nonrat, hv_tripole)



if __name__ == '__main__':
    
    from algebraic_colors.rigorous.quickhue import get_hue_wheel, get_hv_wheel
    
    hv_wheel = get_hv_wheel(12, v=2, include_nullhue=False)
    tripole_wheel = tuple(map(tripole.from_hv_object, hv_wheel))
    
    for r in range(4):
        for g in range(4):
            for b in range(4):
                trip = tripole(r, g, b)
                print(f"T{r, g, b} = {trip};    {r+g+b = }  →  {sum(trip)}")
    
    j = 7
    hv1 = hv_wheel[j]
    trip1 = tripole_wheel[j]
    for hv0, trip0 in zip(hv_wheel, tripole_wheel):
        trip2 = trip0 + trip1
        print((trip0 | trip1).get_HV(), trip2.get_HV())
        continue
        hv2 = hv0 * hv1
        print((hv0, hv1, [hv2]), hv2/hv0==hv1, hv2/hv1==hv0)
    
    
    print() / print()
    #import tkinter
