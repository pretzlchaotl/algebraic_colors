
import sys
sys.path.append(__file__.rsplit('algebraic_colors', 1)[0])
from algebraic_colors.cf import color_functions as cf    
from algebraic_colors.cf.color_functions_strings import (
    hue_ch_encode, colorize_hue_ch, 
    )
from math import (
    nan, inf, isnan, isfinite, 
    modf, fmod, frexp, exp2, ldexp, 
    cos, sin, atan2, hypot, 
    copysign, 
    )
from cmath import rect, phase, exp, pi, tau
from more_itertools import is_sorted, consume
from operator import attrgetter


__all__ = []
def modulefunc(f, name: str=None):
    if not name and isinstance(f, str) and f:
        name = f
    __all__.append(name or f.__name__)
    return f

def modulefuncs(*names):
    consume(map(modulefunc, names))


_hue_cmp_error_text = "Ordering comparisons on hue objects is ternary; comparisons only work between a hue and a tuple of hues."
_subscript_digits = str.maketrans({'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'})


ch_hue_ref = {
    'w': nan, '∞': inf, '-∞': -inf, 
    'r': 0.0, 'y': 1.0, 'g': 2.0, 
    'c': 3.0, 'b': 4.0, 'm': 5.0, 
    'o': 0.5, 'l': 1.5, 't': 2.5, 
    'a': 3.5, 'i': 4.5, 'f': 5.5, 
}
hue_redindex_ch_ref = {
    nan: 'w', inf: '∞', -inf: '-∞', 
    0.0: 'r', 1.0: 'y', 2.0: 'g', 
    3.0: 'c', 4.0: 'b', 5.0: 'm', 
    0.5: 'o', 1.5: 'l', 2.5: 't', 
    3.5: 'a', 4.5: 'i', 5.5: 'f', 
    0.25: '(o|r)', 0.75: '(y|o)', 1.25: '(l|y)', 
    1.75: '(g|l)', 2.25: '(t|g)', 2.75: '(c|t)', 
    3.25: '(a|c)', 3.75: '(b|a)', 4.25: '(i|b)', 
    4.75: '(m|i)', 5.25: '(f|m)', 5.75: '(r|f)', 
    0.125: '(r|o|r)', 0.375: '(o|r|o)', 0.625: '(o|y|o)', 
    0.875: '(y|o|y)', 1.125: '(y|l|y)', 1.375: '(l|y|l)', 
    1.625: '(l|g|l)', 1.875: '(g|l|g)', 2.125: '(g|t|g)', 
    2.375: '(t|g|t)', 2.625: '(t|c|t)', 2.875: '(c|t|c)', 
    3.125: '(c|a|c)', 3.375: '(a|c|a)', 3.625: '(a|b|a)', 
    3.875: '(b|a|b)', 4.125: '(b|i|b)', 4.375: '(i|b|i)', 
    4.625: '(i|m|i)', 4.875: '(m|i|m)', 5.125: '(m|f|m)', 
    5.375: '(f|m|f)', 5.625: '(f|r|f)', 5.875: '(r|f|r)', 
    0.0625: '(r|o|r|r)', 0.1875: '(r|o|o|r)', 0.3125: '(o|r|r|o)', 0.4375: '(o|r|o|o)', 
    0.5625: '(o|y|o|o)', 0.6875: '(o|y|y|o)', 0.8125: '(y|o|o|y)', 0.9375: '(y|o|y|y)', 
    1.0625: '(y|l|y|y)', 1.1875: '(y|l|l|y)', 1.3125: '(l|y|y|l)', 1.4375: '(l|y|l|l)', 
    1.5625: '(l|g|l|l)', 1.6875: '(l|g|g|l)', 1.8125: '(g|l|l|g)', 1.9375: '(g|l|g|g)', 
    2.0625: '(g|t|g|g)', 2.1875: '(g|t|t|g)', 2.3125: '(t|g|g|t)', 2.4375: '(t|g|t|t)', 
    2.5625: '(t|c|t|t)', 2.6875: '(t|c|c|t)', 2.8125: '(c|t|t|c)', 2.9375: '(c|t|c|c)', 
    3.0625: '(c|a|c|c)', 3.1875: '(c|a|a|c)', 3.3125: '(a|c|c|a)', 3.4375: '(a|c|a|a)', 
    3.5625: '(a|b|a|a)', 3.6875: '(a|b|b|a)', 3.8125: '(b|a|a|b)', 3.9375: '(b|a|b|b)', 
    4.0625: '(b|i|b|b)', 4.1875: '(b|i|i|b)', 4.3125: '(i|b|b|i)', 4.4375: '(i|b|i|i)', 
    4.5625: '(i|m|i|i)', 4.6875: '(i|m|m|i)', 4.8125: '(m|i|i|m)', 4.9375: '(m|i|m|m)', 
    5.0625: '(m|f|m|m)', 5.1875: '(m|f|f|m)', 5.3125: '(f|m|m|f)', 5.4375: '(f|m|f|f)', 
    5.5625: '(f|r|f|f)', 5.6875: '(f|r|r|f)', 5.8125: '(r|f|f|r)', 5.9375: '(r|f|r|r)', 
    0.03125: '(r|o|r|r|r)', 0.09375: '(r|o|o|r|r)', 0.15625: '(o|r|r|o|r)', 0.21875: '(o|r|o|o|r)', 
    0.28125: '(r|o|r|r|o)', 0.34375: '(r|o|o|r|o)', 0.40625: '(o|r|r|o|o)', 0.46875: '(o|r|o|o|o)', 
    0.53125: '(o|y|o|o|o)', 0.59375: '(o|y|y|o|o)', 0.65625: '(y|o|o|y|o)', 0.71875: '(y|o|y|y|o)', 
    0.78125: '(o|y|o|o|y)', 0.84375: '(o|y|y|o|y)', 0.90625: '(y|o|o|y|y)', 0.96875: '(y|o|y|y|y)', 
    1.03125: '(y|l|y|y|y)', 1.09375: '(y|l|l|y|y)', 1.15625: '(l|y|y|l|y)', 1.21875: '(l|y|l|l|y)', 
    1.28125: '(y|l|y|y|l)', 1.34375: '(y|l|l|y|l)', 1.40625: '(l|y|y|l|l)', 1.46875: '(l|y|l|l|l)', 
    1.53125: '(l|g|l|l|l)', 1.59375: '(l|g|g|l|l)', 1.65625: '(g|l|l|g|l)', 1.71875: '(g|l|g|g|l)', 
    1.78125: '(l|g|l|l|g)', 1.84375: '(l|g|g|l|g)', 1.90625: '(g|l|l|g|g)', 1.96875: '(g|l|g|g|g)', 
    2.03125: '(g|t|g|g|g)', 2.09375: '(g|t|t|g|g)', 2.15625: '(t|g|g|t|g)', 2.21875: '(t|g|t|t|g)', 
    2.28125: '(g|t|g|g|t)', 2.34375: '(g|t|t|g|t)', 2.40625: '(t|g|g|t|t)', 2.46875: '(t|g|t|t|t)', 
    2.53125: '(t|c|t|t|t)', 2.59375: '(t|c|c|t|t)', 2.65625: '(c|t|t|c|t)', 2.71875: '(c|t|c|c|t)', 
    2.78125: '(t|c|t|t|c)', 2.84375: '(t|c|c|t|c)', 2.90625: '(c|t|t|c|c)', 2.96875: '(c|t|c|c|c)', 
    3.03125: '(c|a|c|c|c)', 3.09375: '(c|a|a|c|c)', 3.15625: '(a|c|c|a|c)', 3.21875: '(a|c|a|a|c)', 
    3.28125: '(c|a|c|c|a)', 3.34375: '(c|a|a|c|a)', 3.40625: '(a|c|c|a|a)', 3.46875: '(a|c|a|a|a)', 
    3.53125: '(a|b|a|a|a)', 3.59375: '(a|b|b|a|a)', 3.65625: '(b|a|a|b|a)', 3.71875: '(b|a|b|b|a)', 
    3.78125: '(a|b|a|a|b)', 3.84375: '(a|b|b|a|b)', 3.90625: '(b|a|a|b|b)', 3.96875: '(b|a|b|b|b)', 
    4.03125: '(b|i|b|b|b)', 4.09375: '(b|i|i|b|b)', 4.15625: '(i|b|b|i|b)', 4.21875: '(i|b|i|i|b)', 
    4.28125: '(b|i|b|b|i)', 4.34375: '(b|i|i|b|i)', 4.40625: '(i|b|b|i|i)', 4.46875: '(i|b|i|i|i)', 
    4.53125: '(i|m|i|i|i)', 4.59375: '(i|m|m|i|i)', 4.65625: '(m|i|i|m|i)', 4.71875: '(m|i|m|m|i)', 
    4.78125: '(i|m|i|i|m)', 4.84375: '(i|m|m|i|m)', 4.90625: '(m|i|i|m|m)', 4.96875: '(m|i|m|m|m)', 
    5.03125: '(m|f|m|m|m)', 5.09375: '(m|f|f|m|m)', 5.15625: '(f|m|m|f|m)', 5.21875: '(f|m|f|f|m)', 
    5.28125: '(m|f|m|m|f)', 5.34375: '(m|f|f|m|f)', 5.40625: '(f|m|m|f|f)', 5.46875: '(f|m|f|f|f)', 
    5.53125: '(f|r|f|f|f)', 5.59375: '(f|r|r|f|f)', 5.65625: '(r|f|f|r|f)', 5.71875: '(r|f|r|r|f)', 
    5.78125: '(f|r|f|f|r)', 5.84375: '(f|r|r|f|r)', 5.90625: '(r|f|f|r|r)', 5.96875: '(r|f|r|r|r)', 
}


modulefuncs('ch_hue_ref', 'hue_redindex_ch_ref')


"//    ____    UTILITY    FUNCTIONS    ____    \\"

@modulefunc
def hue_redindex_ch_encode(redindex: float, *, default_header=""):
    if ch := hue_redindex_ch_ref.get(redindex, None):
        return ch
    ch = hue_ch_encode(redindex)
    if ch == '?':
        ch = f"{default_header}({redindex})"
    return ch

cf_f2_h_midhue = cf.f2_h_midhue
class _decoderhue(float):
    def __or__(self, other): return _decoderhue(cf_f2_h_midhue(self, other))

@modulefunc
def hue_ch_decode(string: str):
    string = ' '.join(list(string)) # ★ Should wreck any function calls to ensure safe eval
    return eval(string, ch_hue_ref)


@modulefunc
def extract_dyadic_exponent(x: float, precision=24):
    """
    Returns the exponent of 2 which produces the denominator of ‘x’ when inverted:
        >>> n = extract_dyadic_exponent(7.375)
        -3
        >>> m = 7.375 * exp2(-n)
        59.0
        >>> exp2(-n)
        8.0
        >>> m / exp2(-n)
        7.375
    """
    xf, ix = modf(x)
    if xf == 0.0: return 0
    for i in range(-1, -precision, -1):
        if not fmod(xf, exp2(i)): return i
    return precision


@modulefunc
def residue6(θ):
    θ %= 6.0
    if θ > 3.0: return θ - 6.0
    return θ

residue6_alt = lambda x: ((x + 3) % 6) - 3


@modulefunc
def is_scalar(obj):
    return isinstance(obj, (int, float))

@modulefunc
def infzdiv(a, b): return (a / b) if b else copysign(inf, a)
@modulefunc
def infzpow(a, b): return (a ** b) if (a or (b >= 0)) else copysign(inf, a)


'''
from collections import OrderedDict
class save_namespace(type):
    def __new__(subcls, name, bases, namespace):
        namespace = OrderedDict(namespace)
        new = super().__new__(subcls, name, bases, namespace)
        new.namespace = namespace
        return new
'''


_PREC = 11


@modulefunc
class hue:
    __slots__ = ('redindex',)
    redindex: float
    
    greenindex = property(lambda self: (self.redindex - 2.0) % 6.0)
    blueindex = property(lambda self: (self.redindex - 4.0) % 6.0)
    
    exponent = property(lambda self: extract_dyadic_exponent(self.redindex, self.precision))
    mantissa_red = property(lambda self: self.redindex / exp2(self.exponent))
    mantissa_green = property(lambda self: self.greenindex / exp2(self.exponent))
    mantissa_blue = property(lambda self: self.blueindex / exp2(self.exponent))
    
    precision = 24
    w = None
    
    @classmethod
    def from_string(cls, string: str): return cls(hue_ch_decode(string))
    @classmethod
    def from_rgb_object(cls, rgb: tuple): return cls(cf.rgb_to_h(rgb))
    @classmethod
    def from_greenindex(cls, greenindex: float): return cls(greenindex + 2.0)
    @classmethod
    def from_blueindex(cls, greenindex: float): return cls(blueindex + 4.0)
    
    def __new__(cls, redindex: float):
        if isinstance(redindex, hue): return redindex
        self = object.__new__(cls)
        self.redindex = float(redindex) % 6.0
        return self
    from_redindex = __new__
    #def __setattr__(self, name, value): raise AttributeError(f"attribute {name!r} of 'hue' objects is not writable")
    
    def __format__(self, format_spec=""):
#        print([format_spec])
        if style := '|' in format_spec:
            format_spec, style = format_spec.split('|')
#        print('    ', [format_spec, style])
        match (style):
            case 'c' | False:
                st = hue_redindex_ch_encode(self.redindex, default_header="hue")
            case 'C':
                st = hue_redindex_ch_encode(self.redindex, default_header="hue")
                if not st.startswith("hue"):
                    st = colorize_hue_ch(st)
            case ('') | (False):
                st = self.redindex
            case _:
                raise ValueError(f"Invalid format specifier: {format_spec}")
#        print('        ', [st])
        if format_spec: return f"{st:{format_spec}}"
        return str(st)
    def __repr__(self): return f"hue({self.redindex})"
    def __str__(self): return self.__format__("|c")
    #hue_ch_encode(self.redindex)
    
    def __hash__(self): return hash((hue, self.redindex))
    
    #        //        (Θ) → O        \\        #
    def __bool__(self): return (self.redindex == self.redindex)
   
    def complex_from_redindex(self): return exp(self.redindex * pi / 3.0)
    def complex_from_greenindex(self): return exp(self.greenindex * pi / 3.0)
    def complex_from_blueindex(self): return exp(self.blueindex * pi / 3.0)
    
    def as_rgb(self): return cf.h_to_rgb(self.redindex)
    
   #    ranking_Θ_B    #
    def is_nullary(self): return isnan(self.redindex)
    def is_primary(self): return not (self.redindex % 2)
    def is_secondary(self): return (self.redindex % 2) == 1.0
    def is_tertiary(self): return (self.redindex % 1.0) == 0.5
    def is_hexradic(self): return self.redindex.is_integer()
    def is_dodecaradic(self): return not (self.redindex % 0.5)
    #    ranking_Θ_O    #
    def rank(self):
        if isnan(self.redindex): return 0
        if self.redindex.is_integer(): return (self.redindex % 2) + 1.0
        if n := extract_dyadic_exponent(self.redindex): return 2 - n
        return is_odd(self.redindex // exp2(n)) + 1
    def rank_symbol(self):
        nkst = str(self.rank()).translate(_subscript_digits)
        return f"Θ{nkst}"
    
    #        //        (Θ) → Θ        \\        #
    def invert(self): return hue(self.redindex + 3.0)
    def rotate_green(self): return hue(self.redindex + 2.0)
    def rotate_blue(self): return hue(self.redindex + 4.0)
    def flip_red(self): return hue(6.0 - self.redindex)
    def flip_green(self): return hue(4.0 - self.redindex)
    def flip_blue(self): return hue(2.0 - self.redindex)
    
    def squared(self): return hue(self.redindex * -2)
    def sqrt(self):
        h = self.redindex
        return hue(h*-2 + residue6(h*3) / 2)
    
    #    rounding_ΘS_Θ    #
    #def dyadic_round(self, nbits=0): return hue(_______)
    #def __round__(self, n): return hue(_______)
    
    #    / //        (Θ, O) → B        \\    \\    #
    def __eq__(self, other):
        if isinstance(other, hue):
            p = self.redindex
            q = other.redindex
            if (p != p): return (q != q)
            return (p == q)
        if isinstance(other, complex):
            return (abs(other) == 1.0) and ((phase(other) * 3.0 / pi) % 2.0) == (self.redindex % 2.0)
        return False
    def __ne__(self, other):
        if isinstance(other, hue):
            p = self.redindex
            q = other.redindex
            if (p != p): return (q == q)
            return (p != q)
        if isinstance(other, complex):
            return (abs(other) != 1.0) or ((phase(other) * 3.0 / pi) % 2.0) != (self.redindex % 2.0)
        return True
    
    def __ge__(self, other):
        if not isinstance(other, tuple): raise TypeError(_hue_cmp_error_text)
        return is_sorted(other, key=self.huediff_asymmetric, reverse=False)
    def __le__(self, other):
        if not isinstance(other, tuple): raise TypeError(_hue_cmp_error_text)
        return is_sorted(other, key=self.huediff_asymmetric, reverse=True)
    def __gt__(self, other):
        if not isinstance(other, tuple): raise TypeError(_hue_cmp_error_text)
        return is_sorted(other, key=self.huediff_asymmetric, reverse=False, strict=True)
    def __lt__(self, other):
        if not isinstance(other, tuple): raise TypeError(_hue_cmp_error_text)
        return is_sorted(other, key=self.huediff_asymmetric, reverse=True, strict=True)
    
    #    / //        (Θ, Θ) → ℝ        \\    \\    #
    def huediff(self, other):
        "p >> q  :=  (p→q)  :=  p.huediff(q)"
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        q = other.redindex
        #if isnan(p) or isnan(q): return 0.0
        #(['88800', '0.479', '0.000', '0.722', '0.000'], 'rigorous/quickhue.py', '263(huediff)'), 
        if not (p == p != q == q): return 0.0
        #(['88900', '0.411', '0.000', '0.570', '0.000'], 'rigorous/quickhue.py', '263(huediff)'), 
        diff = (q - p) % 6.0
        if diff > 3.0: return diff - 6.0
        #(['88600', '0.368', '0.000', '0.416', '0.000'], 'rigorous/quickhue.py', '266(huediff)'),  (instead of residue6)
        #(['89000', '0.343', '0.000', '0.390', '0.000'], 'rigorous/quickhue.py', '266(huediff)'), (using floats)
        return diff
        #return residue6(q - p)
    def reverse_huediff(self, other):
        "p << q  :=  (p←q)  :=  q.huediff(p)"
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        q = other.redindex
        if not (p == p != q == q): return 0.0
        diff = (p - q) % 6.0
        if diff > 3.0: return diff - 6.0
        return diff
    
    def huediff_asymmetric(self, other):
        "|)p→q|)  :=  p.huediff_asymmetric(q)"
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        q = other.redindex
        if not (p == p != q == q): return 0.0
        return (q - p) % 6.0
    def huediff_complement(self, other):
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        q = other.redindex
        if not (p == p != q == q): return 6.0
        return 6.0 - ((q - p) % 6.0)
    
    def hue_log(self, other):
        if not isinstance(other, hue): return NotImplemented
        q = other.redindex
        if (q != q): return nan
        qq = (-q-q) % 6.0
        ddd = (qq-q) % 6.0
        if ddd > 3.0:
            ddd -= 6.0
        if ddd != 0.0:
            p = self.redindex
            if (p != p): return nan
            bb = (p - q) % 6.0
            if bb > 3.0:
                bb -= 6.0
            return (bb / ddd) + 1.0    # (Q→P)/(Q→Q²) + 1.0
        return 1.0
        #(['30000', '0.176', '0.000', '0.191', '0.000'], 'rigorous/quickhue.py', '305(hue_log)'), 
#        if adiff := other.huediff(other.squared()):    # (Q→Q²) ? [↓] : 1.0
#            return ((other.huediff(self) / adiff) + 1.0)    # (Q→P)/(Q→Q²) + 1.0
#        return 1.0
        #(['30000', '0.240', '0.000', '0.771', '0.000'], 'rigorous/quickhue.py', '302(hue_log)'), 
    def reverse_hue_log(self, other):
        "For wrapping hue_log(base=self)"
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        if (p != p): return nan
        pp = (-p-p) % 6.0
        ddd = (pp-p) % 6.0
        if ddd > 3.0:
            ddd -= 6.0
        if ddd != 0.0:
            q = other.redindex
            if (q != q): return nan
            bb = (q - p) % 6.0
            if bb > 3.0:
                bb -= 6.0
            return (bb / ddd) + 1.0    # (Q→P)/(Q→Q²) + 1.0
        return 1.0
#        if adiff := self.huediff(self.squared()):    # (Q→Q²) ? [↓] : 1.0
#            return ((self.huediff(other) / adiff) + 1.0)    # (Q→P)/(Q→Q²) + 1.0
#        return 1.0
    
    #    / //        (Θ, Θ) → Θ        \\    \\    #
    def midhue(self, other):
        "(p | q)  :=  p.midhue(q)"
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        if (p != p): return other
        q = other.redindex
        if not (q == q != p): return self
        dd = (q - p) % 6.0
        if (dd == 3.0): return hue(nan)
        if (dd > 3.0):
            dd -= 6.0
        #dd = residue6(q - p)
        #if (dd == 3.0): return hue.w
        return hue(p + dd / 2)
    def inverse_midhue(self, other):
        "(p / q)  :=  ( | p / q)  :=  p.inverse_midhue(q)"
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        q = other.redindex
        if (p != p): return hue(q + 3.0)
        if not (q == q != p): return self
        dd = (p - q) % 6.0
        if (dd == 3.0): return hue(nan)
        if (dd > 3.0):
            dd -= 6.0
        #dd = residue6(p - q)
        #if (dd == 3.0): return hue.w
        return hue(q + dd * 2)
    def reverse_inverse_midhue(self, other):
        "(p // q)  :=  (p / q | )  :=  p.reverse_inverse_midhue(q)"
        if not isinstance(other, hue): return NotImplemented
        q = other.redindex
        p = self.redindex
        if (q != q): return hue(p + 3.0)
        if not (p == p != q): return other
        dd = (p - q) % 6.0
        if (dd == 3.0): return hue.w
        if dd > 3.0:
            dd -= 6.0
        return hue(p - dd * 2)
    
    def hue_flip(self, other):
        "p % q  :=  p.hue_flip(q)"
        if not isinstance(other, hue): return NotImplemented
        return hue(other.redindex * 2 - self.redindex)
    def hue_multiply(self, other):
        "p * q  :=  p.hue_multiply(q)"
        if not isinstance(other, hue): return NotImplemented
        p = self.redindex
        q = other.redindex
        if (p != p or q != q): return hue(nan)
        return hue(-(p + q))
    
    #    / //        (Θ, ℝ) → Θ        \\    \\    #
    def rotate(self, delta):
        "p + n  :=  p.rotate(n)"
        if isinstance(delta, hue): return NotImplemented
        return hue(self.redindex + delta)
    def inverse_rotate(self, delta):
        "p - n  :=  p.inverse_rotate(n)"
        if isinstance(delta, hue): return NotImplemented
        return hue(self.redindex - delta)
    def hue_power(self, n):
        "p**n  :=  p.hue_power(n)"
        if isinstance(n, hue): return NotImplemented
        h = self.redindex
        if (h != h): return self
        nf, ni = modf(n)
        if n < 0:
            nf = -nf
        oddn = bool(ni % 2);
        hhh = (h * (-3 if oddn else 3)) % 6.0
        if hhh > 3.0:
            hhh -= 6.0
        return hue((h if oddn else h*-2) + hhh*nf)
        '''
        if (ni % 2):
            hhh = (h*-3)%6.0
            if hhh > 3.0:
                hhh -= 6.0
            return hue(h + hhh*nf)
        hhh = (3*h) % 6.0
        if hhh > 3.0:
            hhh -= 6.0
        return hue(h*-2 + hhh*nf)'''
        #(['30000', '0.283', '0.000', '0.487', '0.000'], 'rigorous/quickhue.py', '392(hue_power)'), 
        #if (ni % 2): return hue(h + residue6(h*-3)*nf)
        #return hue(h*-2 + residue6(h*3)*nf)
        #(['30000', '0.301', '0.000', '0.546', '0.000'], 'rigorous/quickhue.py', '392(hue_power)'), 
    def hue_reverse_root(self, n): return self.hue_power((1/n) if n!=0 else inf)
    
    #            #            #            #            #
    __invert__ = invert
    
    __rshift__ = huediff
    __lshift__ = reverse_huediff
    
    __or__ = midhue
    __truediv__ = inverse_midhue
    __floordiv__ = reverse_inverse_midhue
    __mod__ = hue_flip
    __mul__ = hue_multiply
    
    __add__ = rotate
    __sub__ = inverse_rotate
    __pow__ = hue_power


arithmetic_methods_hue = {
        "type_conversions_Θ_x": [
                'as_rgb', 
                'redindex', 'greenindex', 'blueindex', 
                'complex_from_redindex', 'complex_from_greenindex', 'complex_from_blueindex', ], 
        "unary_Θ_B": ['__bool__', 
                'is_nullary', 'is_primary', 'is_secondary', 'is_tertiary', 
                'is_hexradic', 'is_dodecaradic', ], 
        "ranking_Θ_O": ['rank', 'rank_symbol', ], 
        "unary_Θ_Θ": [
                'invert', 
                'rotate_green', 'rotate_blue', 
                'flip_red', 'flip_green', 'flip_blue', 
                'squared', 'sqrt'], 
        "binary_ΘΘ_Θ": [
                'hue_multiply', 
                'midhue', 'inverse_midhue', 'reverse_inverse_midhue', 'hue_flip'], 
        "binary_ΘΘ_S": [
                'huediff', 'reverse_huediff', 'huediff_asymmetric', 'huediff_complement', 
                'hue_log', 'reverse_hue_log'], 
        "binary_ΘS_Θ": [
                'rotate', 'inverse_rotate', 
                'hue_power', 'hue_reverse_root', ], 
        "binary_ΘS_S": [], 
        "binary_comparison_ΘΘ_B": ['__eq__', '__ne__'], 
        "ternary_comparison_Θ(ΘΘ)_B": ['__ge__', '__le__', '__gt__', '__lt__'], 
    }


ch_hue_ref = {k: _decoderhue(v) for k, v in ch_hue_ref.items()}

hue.w = hue.from_string('w')



@modulefunc
class hv_object:
    __slots__ = ('h', 'v')
    h: hue
    v: float
    H = property(attrgetter('h'))
    V = property(attrgetter('v'))
    
    precision = classmethod(property(lambda cls: hue.precision))
    w1 = None
    
    @classmethod
    def from_rgb_object(cls, rgb: tuple): return cls(*cf.rgb_to_hv(rgb))
    
    def __new__(cls, h: hue=hue.w, v: float=1.0, *, _override=False):
        #if not _override:
        if isinstance(h, hv_object): return h
        h = hue(h)
        v = float(v)
        if not (h and v and v==v): return hv_object.w1
        elif v < 0:
            h = ~h
            v = -v
        self = object.__new__(cls)
        self.h = h
        self.v = v
        return self
    #def __setattr__(self, name, value): raise AttributeError(f"attribute {name!r} of 'hue' objects is not writable")
    
    def replace(self, h=None, v=None):
        return hv_object(self.h if h is None else h, 
                                    self.v if v is None else v)
    
    def __format__(self, format_spec=""):
        if style := '|' in format_spec:
            format_spec, style = format_spec.split('|')
        match (style):
            case 'c':
                stH = hue_redindex_ch_encode(self.h.redindex, default_header="hv")
                stV = format(self.v, format_spec)
            case 'C':
                stH = hue_redindex_ch_encode(self.h.redindex, default_header="hv")
                if not st.startswith("hv"):
                    stH = colorize_hue_ch(stH)
                stV = format(self.v, format_spec)
            case 'cx':
                stH = hue_redindex_ch_encode(self.h.redindex, default_header="hv")
                stV = self.v.hex()
            case 'Cx':
                stH = frexp_hue_ch_encode(self.h.redindex, default_header="hv")
                if not st.startswith("hv"):
                    stH = colorize_hue_ch(stH)
                stV = self.v.hex()
            case ('') | (False):
                stH = self.h
                stV = self.v
            case _:
                raise ValueError(f"Invalid format specifier: {format_spec}")
        return f"[{stH:{format_spec}}, {stV:{format_spec}}]"
    def __str__(self): return f"[{self.h:|c}, {self.v}]"
    def __repr__(self): return f"hv_object({self.h}, {self.v})"
    
    def __hash__(self): return hash((hv_object, self.h.redindex, self.v))
    
    #        //        (Θ) → O        \        #
    def __bool__(self): return bool(self.v)
   
    def complex_from_redindex(self): return exp(self.h.redindex * pi / 3.0) * self.v
    def complex_from_greenindex(self): return exp(self.h.greenindex * pi / 3.0) * self.v
    def complex_from_blueindex(self): return exp(self.h.blueindex * pi / 3.0) * self.v
    
    def as_rgb(self): return cf.hv_to_rgb(self.h.redindex, self.v)
    
    #    ranking_Θ_B    #
    is_nullary = property(attrgetter("h.is_nullary"))
    is_primary = property(attrgetter("h.is_primary"))
    is_secondary = property(attrgetter("h.is_secodary"))
    is_tertiary = property(attrgetter("h.is_tertiary"))
    is_hexradic = property(attrgetter("h.is_hexradic"))
    is_dodecaradic = property(attrgetter("h.is_dodecaradic"))
    def is_whole(self):
        "An HV object is whole if its scalar is equal to one or zero."
        return not (1 != self.v != 0)
    
    #        //        (Θ) → Θ        \        #
    def flip_red(self): return self.replace(self.h.flip_red())
    def flip_green(self): return self.replace(self.h.flip_green())
    def flip_blue(self): return self.replace(self.h.flip_blue())
    def rotate_green(self): return self.replace(self.h.rotate_green())
    def rotate_blue(self): return self.replace(self.h.rotate_blue())
    def invert(self): return self.replace(self.h.invert())
    
    hue_sign = attrgetter('h')
    absolute_value = attrgetter('v')
    
    def squared(self): return hv_object(self.h.squared(), self.v**2)
    def sqrt(self): return hv_object(self.h.sqrt(), self.v**0.5)
    
    #    rounding_ΘS_Θ    #
    #def dyadic_round(self, nbits=0): return hue(_______)
    #def __round__(self, n): return hue(_______)
    
    #    / //        (Θ, O) → B        \    \    #
    def __eq__(self, other):
        if isinstance(other, hue): return (self.v == bool(other)) and (self.h == other)
        if isinstance(other, hv_object): return (self.h == other.h) and (self.v == other.v)
        if isinstance(other, complex):
            return (abs(other) == self.v) and ((phase(other) * 3.0 / pi) % 2.0) == (self.h.redindex % 2.0)
        return False
    def __ne__(self, other):
        if isinstance(other, hue): return (self.v != bool(other)) or (self.h != other)
        if isinstance(other, hv_object): return (self.h != other.h) or (self.v != other.v)
        if isinstance(other, complex):
            return (abs(other) != self.v) or ((phase(other) * 3.0 / pi) % 2.0) != (self.h.redindex % 2.0)
        return True
    
    #    / //        (Θν, Θν) → Θν        \    \    #
    def midpoint(self, other):
        "For HV objects p and q, (p|q) := HV((p.H | q.H), (p.V + q.V)/2)."
        if not isinstance(other, hv_object): return NotImplemented
        return self.replace(self.h.midhue(other.h), (self.v + other.v) / 2)
    def inverse_midpoint(self, other):
        "For HV objects p and q, (|p/q) := HV((| p.H / q.H), 2*p.V - q.V)."
        if not isinstance(other, hv_object): return NotImplemented
        return self.replace(self.h.inverse_midhue(other.h), 2 * self.v - other.v)
    def reverse_inverse_midpoint(self, other):
        "For HV objects p and q, (p/q|) := HV((p.H / q.H |), -p.V + 2*q.V)."
        if not isinstance(other, hv_object): return NotImplemented
        return self.replace(self.h.reverse_inverse_midhue(other.h), 2 * other.v - self.v)
    def multiply(self, other):
        "For HV objects p and q, p*q := HV(p.H*q.H, p.V*q.V)"
        if isinstance(other, hv_object): return self.replace(self.h * other.h, self.v * other.v)
        if isinstance(other, hue): return self.replace(self.h * other, self.v)
        return self.scalar_multiply(other)
    def divide(self, other):
        "For HV objects p and q, p/q := HV(p.H*q.H, p.V/q.V). \n"\
        "Division by zero returns infinity."
        if isinstance(other, hv_object): return self.replace(self.h * other.h, infzdiv(self.v, other.v))
        if isinstance(other, hue): return self.replace(self.h * other, self.v)
        return self.scalar_divide(other)
    def reverse_divide(self, other):
        "For HV objects p and q, p/q := HV(p.H*q.H, p.V/q.V). \n"\
        "Division by zero returns infinity."
        if isinstance(other, hue): return self.replace(other * self.h, self.v)
        if isinstance(other, hv_object): return other.new(other.h * self.h, infzdiv(other.v, self.v))
        return self.reverse_scalar_divide(other)
    
    #    / //        (Θν, Θ) → Θν        \    \    #
    def hue_flip(self, other):
        "For HV object p and Hue q, p.hue_flip(q) := HV(p.H.hue_flip(q), p.V)."
        if isinstance(other, hue): return self.replace(self.h.hue_flip(other))
        return NotImplemented
    
    #    / //        (Θν, ℝ) → Θν        \    \    #
    def hue_rotate(self, delta):
        "For HV object p and scalar n, p.hue_rotate(n) := HV(p.H+n, p.V)."
        if is_scalar(delta): return self.replace(self.h.rotate(delta))
        return NotImplemented
    def hue_inverse_rotate(self, delta):
        "For HV object p and scalar n, p.hue_inverse_rotate(n) := HV(p.H-n, p.V)."
        if is_scalar(delta): return self.replace(self.h.inverse_rotate(delta))
        return NotImplemented
    
    def scalar_add(self, other):
        "For HV object p and scalar n, p+n := HV(p.H, p.V+n)."
        if is_scalar(other): return self.replace(v=self.v + other)
        return NotImplemented
    def scalar_subtract(self, other):
        "For HV object p and scalar n, p-n := HV(p.H, p.V-n)."
        if is_scalar(other): return self.replace(v=self.v - other)
        return NotImplemented
    def reverse_scalar_subtract(self, other):
        "For HV object p and scalar n, n-p := HV(p.H, -p.V+n)."
        if is_scalar(other): return self.replace(v=other - self.v)
        return NotImplemented
    
    def scalar_multiply(self, other):
        "For HV object p and scalar n, p*n := HV(p.H, p.V*n)."
        if is_scalar(other): return self.replace(v=self.v * other)
        return NotImplemented
    def scalar_divide(self, other):
        "For HV object p and scalar n, p/n := HV(p.H, p.V/n). \n"\
        "Division by zero returns infinity."
        if is_scalar(other): return self.replace(v=infzdiv(self.v, other))
        return NotImplemented
    def reverse_scalar_divide(self, other):
        "★MAY NEED TO INVERT p.H OR SOMETHING★\n"\
        "For HV object p and scalar n, n/p := HV(p.H, n/p.V). \n"\
        "Division by zero returns infinity."
        if is_scalar(other): return self.replace(v=infzdiv(other, self.v))
        return NotImplemented
    
    def scalar_power(self, other: float):
        "For HV object p and scalar n, p**n := HV(p.H**n, p.V**n). \n"\
        "Raising zero to a negative exponent returns infinity.  Raising zero to zero returns nan."
        if is_scalar(other): return self.replace(self.h.hue_power(other), infzpow(self.v, other))
        return NotImplemented
    def scalar_reverse_root(self, other):
        "Returns self.scalar_power(1/n) if n!=0 else self.scalar_power(inf)."
        if not is_scalar(other): return NotImplemented
        n = (1 / other) if other else inf
        return self.replace(self.h.hue_power(n), infzpow(self.v, n))
    
    #    / //        (Θν, Θν) → ℝ²        \    \    #
    def hv_diff(self, other):
        "For HV objects p and q, p.HV_diff(q) returns tuple (m, n) such that HV(p.H + m, p.V + n) == q. "
        if isinstance(other, hv_object): return self.h.hue_diff(other.h), (other.v - self.v)
        return NotImplemented
    def reverse_hv_diff(self, other):
        "For HV objects p and q, p.reverse_HV_diff(q) returns tuple (m, n) such that HV(q.H + m, q.V + n) == p. "
        if isinstance(other, hv_object): return self.h.reverse_hue_diff(other.h), (self.v - other.v)
        return NotImplemented
    
    #    / //        (Θν, ℝ²) → Θν        \    \    #
    def hv_rotate(self, delta_hue=0, delta_val=0):
        "For HV object p and scalar 2-tuple mn, p+mn := HV(p.H+m, p.V+n)."
        return self.replace(self.h.rotate(delta_hue), self.v + delta_val)
    def hv_inverse_rotate(self, delta_hue=0, delta_val=0):
        "For HV object p and scalar 2-tuple mn, p-mn := HV(p.H+-m, p.V-n)."
        return self.replace(self.h.inverse_rotate(delta_hue), self.v - delta_val)
    
    #        //        (Θ) → Θ        \    (cont.)    #
    def __floor__(self): return self.replace(v=self.v.__floor__())
    def __ceil__(self): return self.replace(v=self.v.__ceil__())
    def __trunc__(self): return self.replace(v=self.v.__trunc__())
    def __round__(self, ndigits=0):
        return self.replace(v=self.v.__round__(ndigits=ndigits))
    
    #            #            #            #            #
    __abs__ = absolute_value
    __invert__ = invert
    __neg__ = invert
    __pos__ = lambda self: self
    
    __add__ = scalar_add
    __sub__ = scalar_subtract
    __radd__ = __add__
    __rsub__ = reverse_scalar_subtract
    
    __mul__ = multiply
    __truediv__ = divide
    __rmul__ = __mul__
    __rtruediv__ = reverse_scalar_divide
    
    __pow__ = scalar_power
    
    __lshift__ = reverse_hv_diff
    __rshift__ = hv_diff


hv_object.w1 = object.__new__(hv_object)
hv_object.w1.h = hue.w
hv_object.w1.v = 0.0



arithmetic_methods_hv = {
        "type_conversions_Θν_x": [
                'as_rgb', 
                'complex_from_redindex', 'complex_from_greenindex', 'complex_from_blueindex', ], 
        "unary_Θν_B": ['__bool__', 
                'is_nullary', 'is_primary', 'is_secondary', 'is_tertiary', 
                'is_hexradic', 'is_dodecaradic', 'is_whole', ], 
        "unary_Θν_O": [
                'hue_sign', 'absolute_value', ], 
        "unary_Θν_Θν": [
                'invert', 
                'rotate_green', 'rotate_blue', 
                'flip_red', 'flip_green', 'flip_blue', 
                'squared', 'sqrt', ], 
        "binary_ΘνΘν_Θν": [
                'multiply', 'divide', 'reverse_divide', 
                'midpoint', 'inverse_midpoint', 'reverse_inverse_midpoint', 'hue_flip'], 
        "binary_ΘνΘν_S": [
                'huediff', 'reverse_huediff', 'huediff_asymmetric', 'huediff_complement', 
                'hue_log', 'reverse_hue_log'], 
        "binary_ΘνS_Θν": [
                'scalar_add', 'scalar_subtract', 'reverse_scalar_subtract', 
                    'scalar_multiply', 'scalar_divide', 'reverse_scalar_divide', 
                    'scalar_power', 'scalar_reverse_root', 
                'hue_rotate', 'hue_inverse_rotate', 
                    'hue_power', 'hue_reverse_root', ], 
        "binary_ΘνΘν_(SS)": [
                'hv_diff', 'reverse_hv_diff', ], 
        "binary_Θν(SS)_Θν": [
                'hv_rotate', 'hv_inverse_rotate',], 
        "binary_ΘνS_S": [], 
        "binary_comparison_ΘνΘν_B": ['__eq__', '__ne__'], 
    }



@modulefunc
def get_hue_wheel(length=12, include_nullhue=False):
    incr = 6.0 / length
    huewheel = list(map(hue, map(incr.__mul__, range(length))))
    if include_nullhue:
        huewheel.append(hue.w)
    return huewheel


@modulefunc
def get_hv_wheel(length=12, v=1, include_nullhue=False):
    incr = 6.0 / length
    hvwheel = tuple(hv_object(h, v) for h in map(incr.__mul__, range(length)))
    if include_nullhue:
        hvwheel += (hv_object.w1,)
    return hvwheel

@modulefunc
def get_hv_onion(h_lengths=12, v_range=(1, 2), include_nullhue=False):
    if include_nullhue:
        yield (hv_object.w1,)
    v_range = tuple(v_range)
    if isinstance(h_lengths, int):
        yield from (get_hv_wheel(h_lengths, v) for v in v_range)
    else:
        for length, v in zip(h_lengths, v_range):
            incr = 6.0 / length
            yield tuple(hv_object(h, v) for h in map(incr.__mul__, range(length)))


#"//    ADDITIONAL    FUNCS    \\"#
@modulefunc
def midhue_weighted(hp: hue, hq: hue, ratio=0.5):
    "(p | q)  :=  p.midhue(q)"
    if not isinstance(hq, hue): return NotImplemented
    p = hp.redindex
    if (p != p): return hq
    q = hq.redindex
    if not (q == q != p): return hp
    dd = (q - p) % 6.0
    if (dd == 3.0): return hue(nan)
    if (dd > 3.0):
        dd -= 6.0
    return hue(p + dd * ratio)

@modulefunc
def inverse_midhue_weighted(hp: hue, hq: hue, ratio=0.5):
    "(p / q)  :=  ( | p / q)  :=  p.inverse_midhue(q)"
    if not isinstance(hq, hue): return NotImplemented
    p = hp.redindex
    q = hq.redindex
    if (p != p): return hue(q + 3.0)
    if not (q == q != p): return hp
    dd = (p - q) % 6.0
    if (dd == 3.0): return hue(nan)
    if (dd > 3.0):
        dd -= 6.0
    return hue(q + dd / ratio)



#"//    TRIGONOMETRY    \\"

_cos = cos
_sin = sin
_atan2 = atan2
@modulefunc
def cos(th): return 0 if (th != th) else _cos(th)
@modulefunc
def sin(th): return 0 if (th != th) else _sin(th)
@modulefunc
def cossin(th, rh): return (0, 0) if (th != th) else (_cos(th) * rh, _sin(th) * rh)

@modulefunc
def atan2(y, x): return nan if (y == 0 == x) else _atan2(y, x)

@modulefunc
def radians_from_redindex(h: hue): return h.redindex * pi / 3.0
@modulefunc
def radians_from_greenindex(h: hue): return h.greenindex * pi / 3.0
@modulefunc
def radians_from_blueindex(h: hue): return h.blueindex * pi / 3.0

@modulefunc
def radians_from_pigmentindex(pigmentindex: float): return pigmentindex * pi / 3.0
@modulefunc
def radians_to_pigmentindex(pigmentindex: float): return pigmentindex * 3.0 / pi

@modulefunc
def hcosine(pigmentindex: float): return cos(pigmentindex * pi / 3.0)
@modulefunc
def hsine(pigmentindex: float): return cos(pigmentindex * pi / 3.0)
@modulefunc
def hcosinesine(pigmentindex: float): return cossin(pigmentindex * pi / 3.0)

@modulefunc
def hvcosine(pigmentindex: float, magnitude: float): return cos(pigmentindex * pi / 3.0) * magnitude
@modulefunc
def hvsine(pigmentindex: float, magnitude: float): return cos(pigmentindex * pi / 3.0) * magnitude
@modulefunc
def hvcosinesine(pigmentindex: float, magnitude: float):
    return polar_to_cart(pigmentindex * pi / 3.0, magnitude)

@modulefunc
def hdiffcos(h0: hue, h1: hue): return hcosine(h1 - h0)
@modulefunc
def hdiffsin(h0: hue, h1: hue): return hsine(h1 - h0)
@modulefunc
def hdiffcossin(h0: hue, h1: hue): return hcosinesine(h1 - h0)

@modulefunc
def xy_to_hv(x, y, *, pigmentindex=0):
    if not pigmentindex: return hv_object(atan2(y, x) * 3.0 / pi, hypot(x, y))
    return hv_object(atan2(y, x) * 3.0 / pi - (pigmentindex * 2.0), hypot(x, y))
@modulefunc
def hv_to_xy(hv: hv_object, *, pigmentindex=0):
    p = hv.h.redindex
    if pigmentindex:
        p += pigmentindex * 2.0
    return hvcosinesine(p, hv.v)





if __name__ == '__main__':
    
    x = hue(3)
    print(x ** 0.5)
    
    a, b = hue.w, hue.from_string('f')
    print(f"{a = }    {b = }\n{a | b = }")
    
    print() / print()
    #import tkinter
    
