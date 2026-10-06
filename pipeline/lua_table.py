# -*- coding: utf-8 -*-
"""Minimal Lua table literal parser (subset used by gfwiki Module:Gun info/data*).

Handles: nil / true / false / numbers / "strings" / {key = value, [n] = value, positional}
Sufficient for the wiki data modules; not a general Lua parser.
"""
import re


class LuaTable(dict):
    """dict that also keeps positional (array) entries under integer keys."""


_TOK = re.compile(r'''
    \s*(?:
        (?P<num>-?\d+\.\d+(?:[eE][-+]?\d+)?)   |
        (?P<int>-?\d+)                           |
        (?P<str>"(?:\\.|[^"\\])*")               |
        (?P<name>[A-Za-z_][A-Za-z0-9_]*)         |
        (?P<op>\[|\]|\{|\}|,|=)
    )''', re.VERBOSE)


def _tokenize(src):
    pos, out = 0, []
    while pos < len(src):
        m = _TOK.match(src, pos)
        if not m:
            if src[pos:].strip() == '':
                break
            raise ValueError(f'tokenize error at {pos}: {src[pos:pos+40]!r}')
        pos = m.end()
        if m.lastgroup == 'num':
            out.append(('num', float(m.group('num'))))
        elif m.lastgroup == 'int':
            out.append(('num', int(m.group('int'))))
        elif m.lastgroup == 'str':
            s = m.group('str')[1:-1]
            s = s.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')
            out.append(('str', s))
        elif m.lastgroup == 'name':
            out.append(('name', m.group('name')))
        else:
            out.append(('op', m.group('op')))
    return out


def parse(src):
    """Parse `local data = {...}` module source; returns the table value."""
    start = src.index('{')
    val, pos = _parse_value(_tokenize(src[start:]), 0)
    return val


def _parse_value(toks, i):
    if i >= len(toks):
        raise ValueError('unexpected EOF')
    kind, v = toks[i]
    if kind == 'op' and v == '{':
        return _parse_table(toks, i + 1)
    if kind == 'num' or kind == 'str':
        return v, i + 1
    if kind == 'name':
        if v == 'true':
            return True, i + 1
        if v == 'false':
            return False, i + 1
        if v == 'nil':
            return None, i + 1
    raise ValueError(f'unexpected token {toks[i]} at {i}')


def _parse_table(toks, i):
    t = LuaTable()
    auto = 1
    while True:
        if i >= len(toks):
            raise ValueError('unexpected EOF in table')
        kind, v = toks[i]
        if kind == 'op' and v == '}':
            return t, i + 1
        if kind == 'op' and v == ',':
            i += 1
            continue
        # key?
        if kind == 'name' and i + 1 < len(toks) and toks[i + 1] == ('op', '='):
            key = v
            val, i = _parse_value(toks, i + 2)
            t[key] = val
        elif kind == 'op' and v == '[':
            # [n] = value
            n = toks[i + 1][1]
            val, i = _parse_value(toks, i + 4)  # skip ] =
            t[n] = val
        else:
            val, i = _parse_value(toks, i)
            t[auto] = val
            auto += 1
