
import sys
from itertools import filterfalse, permutations, chain
from more_itertools import all_equal
from numbers import Complex
from math import nan

sys.path.append(__file__.rsplit("/", 1)[0])
from color_functions import *
from color_functions import __all__ as colfs__all, modulefunc
from color_functions_strings__data import *


__all__ = []


def modulefunc(f, name: str=None):
    if not name and isinstance(f, str) and f:
        name = f
    __all__.append(name or f.__name__)
    return f


modulefunc('hues_to_chars_map')
modulefunc('chars_to_hues_map')
modulefunc('hues_to_chars_map_lowrank')
modulefunc('chars_to_hues_map_lowrank')


float_ndigits = sys.float_info.dig


"//    CHAR    REPRESENTATIONS    \\"

'''
@modulefunc
def _hue_rank(h, rounding: int=None, recursionlimit=60):
    if isnan(h): return 0
    h = rounded(h % 6, ndigits=rounding)
    iterations = range(recursionlimit) if recursionlimit else count()
    for i in iterations:
        if not (h % i): return i
    return inf
'''

@modulefunc
def _hue_ch(h):
    if isnan(h): return "w"
    ND = constants.prec
    h = rounded(h % 6, ND if ND>=3 else 3)
    if not (h%0.5): return _wholecolors_12_chars[int(h*2)]
    return "?"


@modulefunc
def _midhue_ch(h0, h1, cache=True):
    if isnan(h0) or isnan(h1): return "w"
    h0 %= 6
    h1 %= 6
    key = rounds(h0, h1)
    if ch := cache and _midhue_ch._mem.get(key, None): return ch
    mid = modmid(h0, h1, 6)
    ch = _hue_ch(mid)
    if ch != "?":
        if cache:
            _midhue_ch._mem[key] = ch
        return ch
    ch0 = _hue_ch(h0)
    ch1 = _hue_ch(h1)
    if ch0 != "?" != ch1:
        ch0 = ch0.strip('()')
        ch1 = ch1.strip('()')
        ch = f"({ch0}|{ch1})"
        if cache:
            _midhue_ch._mem[key] = ch
        return ch
    return "?"
_midhue_ch._mem = {}


class _MidhueProxy:
    "A workaround type which makes dealing with hue_ch strings easier by utilizing the python interpreter rather than crafting regular expressions or whatever."
    __slots__ = ("_h", "_st")
    
    _instances = {}
    
    @classmethod
    def getnew(cls, hue: float, defaultsym: str):
        "Creates a new instance and returns it, caching it in cls._instances on the way."
        ND = constants.prec
        h = rounded(float(hue) % 6, ND if ND>=3 else 3)
        prox = cls._instances.get(h, None)
        if prox is not None: return prox
        return cls(hue, defaultsym)
    
    def __init__(self, hue: float, sym: str):
        ND = constants.prec
        if sym is None:
            sym = _hue_ch(hue)
        self._h = rounded(float(hue) % 6, ND if ND>=3 else 3)
        self._st = str(sym)
        _MidhueProxy._instances[self._h] = self
    
    def __str__(self): return self._st
    __repr__ = __str__
    
    def __or__(self, other):
        if isinstance(other, Complex):
            oh = rounded(other, maximum(constants.prec, 3))
            os = oh
        elif isinstance(other, _MidhueProxy):
            oh = other._h
            os = other._st
        else: return NotImplemented
        sh = self._h
        sym = _midhue_ch(sh, oh)
        if sym == "?":
            sym = f"({self._st}|{os})"
        return _MidhueProxy.getnew(modmid(self._h, oh, m=6), sym)
    


#chars_to_hues_map_lowrank = {}
_basic_midhueproxies = \
    {ch: _MidhueProxy(i/2.0, ch) for i, ch in enumerate(_wholecolors_12_chars)} \
    | {'k': nan, 'w': nan}
@modulefunc
def hue_ch_decode(string: str):
    #if not {'(', ')', '|', 'r','g','b','c','m','y','o','l','t','a','i','f'}.issuperset(string):
    #    raise ValueError("Invalid symbols in input string.")
    h = chars_to_hues_map_lowrank.get(string, None) \
            or chars_to_hues_map.get(string, None)
    if h is not None: return h
    try:
        prox = eval(string, _basic_midhueproxies)
    except Exception as exc:
        print(f"hue_ch_decode({string!r})  →  ")
        raise
    return prox._h

'''

_uniqperms = lambda itr, lnth: filterfalse(all_equal, permutations(itr, lnth))
_huechar_join = lambda tup: '|'.join(tup).join("()")
all_huechars_len2 = list(map(_huechar_join, _uniqperms(_wholecolors_12_chars, 2)))
all_huechars_len3 = list(map(_huechar_join, _uniqperms(_wholecolors_12_chars, 3)))
all_huechars_len4 = list(map(_huechar_join, _uniqperms(_wholecolors_12_chars, 4)))


def _ch_spread(st):
    st = list(filter(str.isalpha, st))
    if len(st) == 1: return 0
    λ = lambda c: (nan if c in"wk" else _wholecolors_12_chars.index(c))
    ids = list(map(λ, st))
    diffs = [abs(moddiff(ids[i], ids[i+1], m=12)) for i in range(len(ids) - 1)]
    return maximum(diffs) / len(diffs)
_sorky = _ch_spread
all_huechars_len2 = sorted(all_huechars_len2, key=_sorky)
all_huechars_len3 = sorted(all_huechars_len3, key=_sorky)
all_huechars_len4 = sorted(all_huechars_len4, key=_sorky)

#print(f"{all_huechars_len2 = }")
#print(f"\n{list(map(_ch_spread, all_huechars_len2)) = }")

del _sorky, _ch_spread

all_huechars_order = [all_huechars_len2, all_huechars_len3, all_huechars_len4]

chars_to_hues_map = {"w": nan}
hues_to_chars_map = {nan: "w"}

_maps_addcharhue_getindex = \
    lambda k: (nan if k in "wk" else _wholecolors_12_chars.index(k))
def _maps_addcharhue(c, h):
    if c not in chars_to_hues_map:
        chars_to_hues_map[c] = h
    if h not in hues_to_chars_map:
        hues_to_chars_map[h] = c
    return h

[_maps_addcharhue(ch, _wholecolors_12_chars.index(ch) * 0.5) for ch in "oltaifcmyrgb"]
[_maps_addcharhue(ch, hue_ch_decode(ch)) \
    for ch in chain.from_iterable(all_huechars_order)]
[_midhue_ch._mem.__setitem__(\
            (hue_ch_decode(ch0), hue_ch_decode(ch1)), f"({ch0}|{ch1})") \
    for ch0, ch1 in _uniqperms(_wholecolors_12_chars, 2)]


all_charhues_order = [[_maps_addcharhue(ch, hue_ch_decode(ch)) \
                                            for ch in allchrs] \
                                                for allchrs in all_huechars_order]
modulefunc('all_huechars_order')
modulefunc('all_charhues_order')

hues_to_chars_map_lowrank = {k: hues_to_chars_map[k] for k in (i*0.5 for i in range(12))}
chars_to_hues_map_lowrank = {v: k for k,v in hues_to_chars_map_lowrank.items()}
'''



@modulefunc
def hue_ch_encode(hue: float, *, _recur=20):
    if isnan(hue): return "w"
    hue = constants.prec_round_atleast_nd(hue % 6, 6)
    ch = hues_to_chars_map_lowrank.get(hue, None) \
        or hues_to_chars_map.get(hue, None)
    if ch is not None: return ch
#    if _recur <= 0: return "?"
#    _recur -= 1
#    irat = 2
#    if not constants.prec_round_atleast_nd(hue % (1/3), 6):
#        irat = 3
#    rat = 1 / irat
#    inv_mid_L = inv_mid_R = nearest = round((hue*2) / 12) / 2
#    ndist = f_h_huediff(hue, nearest)
#    if ndist > 0:    #   inv_mid  < hue < nearest
#        inv_mid_L = (inv_mid_R + ndist / 2) % 6.0
#    else: #if ndist < 0:    #   nearest  < hue < inv_mid
#        inv_mid_R = (inv_mid_L + ndist / 2) % 6.0
#    chL = hue_ch_encode(inv_mid_L, _recur=_recur)
#    chR = hue_ch_encode(inv_mid_R, _recur=_recur)
#    #print(f"    {_recur}    (inv_mid_L  |  inv_mid_R)  =  {inv_mid_L:.5f}  |  {inv_mid_R:.5f}")
#    #print(f"    {_recur}    (chL  |  chR)  =   ({chL}  |  {chR})")
#    if chL != "?" != chR: return f"({chL.strip('()')}|{chR.strip('()')})"
    return "?"


#ls = [('k', '⚫'), ('w', '⚪'), ('r', '♈'), ('o', '♊'), ('y', '♌'), ('l', '♍'), ('g', '♎'), ('t', '♏'), ('c', '⛎'), ('a', '⃣'), ('b', '♐'), ('i', '♑'), ('m', '♒'), ('f', '♓')]\

_charstocolorsyms = {107: 9899, 119: 9898, 114: 9800, 111: 9802, 121: 9804, 108: 9805, 103: 9806, 116: 9807, 99: 9934, 97: 8419, 98: 9808, 105: 9809, 109: 9810, 102: 9811}
_colorsymstochars = {9899: 107, 9898: 119, 9800: 114, 9802: 111, 9804: 121, 9805: 108, 9806: 103, 9807: 116, 9934: 99, 8419: 97, 9808: 98, 9809: 105, 9810: 109, 9811: 102}
@modulefunc
def colorize_hue_ch(string: str):
    string = string.lower()
    if "nan" in string:
        string = string.replace("nan", '⚪')
    return string.translate(_charstocolorsyms)
@modulefunc
def decolorize_hue_ch(string: str): return string.translate(_colorsymstochars)


#    ⚫⚪    ♈♊♌♍♎♏⛎⃣♐♑♒♓


if __name__ == "__main__":
    
    
    #import tkinte
    set_PRECISION(999)
    
    
    _x = 12
    hues = list(map((1/_x).__mul__, range(6 * _x)))
    
    #print(hues)
    
    for hue in hues:
        print()
        print(f"{hue = :.5f}")
        ch0 = colorize_hue_ch(hue_ch_encode(hue, _recur=0))
        #print(f"{hue = :.5f}    {ch0}")
#        for h1 in hues:
#            ch1 = colorize_hue_ch(hue_ch_encode(h1, _recur=0))
#            print(f"    {h1 = :.5f}    {ch1}")
#            h2 = f_h_midhue(hue, h1)
#            ch2 = colorize_hue_ch(hue_ch_encode(h2, _recur=0)) if h2 in hues else f"({ch0}|{ch1})"
#            print(f"        {f_h_midhue(hue, h1) = :.5f}    {ch2}")
#        
        #print(f"            {f_h_huediff(hue, 1/6) = :.5f}\n"\
#                  f"            {f_h_inverse_midhue_L(hue, 1/6) = :.5f}\n"\
#                  f"            {f_h_inverse_midhue_R(hue, 1/6) = :.5f}")
        print(f"{hue = :.5f}    {colorize_hue_ch(hue_ch_encode(hue, _recur=64))}")
    

#try:
#    with open(__file__.removesuffix(".py")+"__data.py", 'x') as wf:
#        print(f"\n{hues_to_chars_map = }\n\n{hues_to_chars_map_lowrank = }\n\n\n{chars_to_hues_map = }\n\n{chars_to_hues_map_lowrank = }\n", file=wf)
#except FileExistsError:
#    

