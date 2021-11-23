"""this module solves simple mathematical expressions"""

import math, decimal

pretty_digits = 6  # i.e. 1.23456
scientific_upper = 3  # min. 1e+4
scientific_lower = -3  # max. 9.99e-4
round_margin = 0.00001  # 0.001%
max_steps = 20
ops = ["+", "*", "^", "-", "/"]
dctx = decimal.Context(prec=20)


def prettyfloat(f, try_str=False):
    if f < 0:
        return "-" + prettyfloat(-f)
    ex = math.floor(math.log10(f))
    # scientific notation (big)
    if ex > scientific_upper:
        return prettyfloat(f / math.pow(10, ex)) + "e+" + str(ex)
    # scientific notation (small)
    if ex < scientific_lower:
        return prettyfloat(f / math.pow(10, ex)) + "e" + str(ex)
    # round numbers
    if f == 0:
        return "0"
    if abs(round(f) - f) / f < round_margin:
        if try_str:
            return str(round(f))
        return prettyfloat(round(f), True)
    # round based on digits
    signif_digits = -ex + pretty_digits - 1
    signif_digits = max(signif_digits, 0)
    signif_str = ("{:." + str(signif_digits) + "f}").format(f)
    if "." in signif_str:
        return signif_str.rstrip("0")
    else:
        return signif_str


# full precision and no scientific notation
def ftos(f):
    return format(dctx.create_decimal(repr(f)), "f")


def eval_num(num, vars):
    if num == "":
        raise KeyError("ERROR: esolve: missing number")
    try:
        return float(num)
    except ValueError:
        if num in vars:
            return float(vars[num])
        elif str(num)[0] == "-" and num[1:] in vars:
            return -float(vars[num[1:]])
        else:
            raise KeyError("ERROR: esolve: var {} not defined".format(num))


def eval_rec(exp, vars):
    exp = exp.replace(" ", "")

    # solve paranthesis first
    p_level = 0
    p_i = 0
    new_exp = ""
    for i in range(len(exp)):
        if exp[i] == "(":
            p_level += 1
            if p_level == 1:
                new_exp += exp[p_i:i]
                p_i = i + 1
        if exp[i] == ")":
            p_level -= 1
            if p_level == 0:
                new_exp += eval_rec(exp[p_i:i], vars)
                p_i = i + 1
    new_exp += exp[p_i:]
    exp = new_exp

    # blocks can be expressions or numbers, operators are operators
    blocks = []
    operators = []
    next_start = 0
    mark_negative = False
    for chr_i in range(len(exp)):
        chr = exp[chr_i]
        if chr in ops:
            new_block = exp[next_start:chr_i].strip()
            if len(new_block) > 0:
                blocks.append(new_block)
            # checks if operator or not
            mark_negative = False
            if chr == "-":
                if chr_i == 0:
                    mark_negative = True
                elif exp[chr_i - 1] in ops:
                    mark_negative = True
            if not mark_negative:
                next_start = chr_i + 1
                # 0: level, 1: operator
                operators.append([ops.index(chr) % 3, chr])
    blocks.append(exp[next_start:])

    # reduce blocks by operator priority
    for _ in range(max_steps):
        if len(operators) <= 1:
            break
        p_max = 0
        for o in operators:
            p_max = max(p_max, o[0])
        o_i = 0
        while o_i < len(operators):
            o = operators[o_i]
            if o[0] == p_max:
                blocks.insert(
                    o_i + 2, eval_rec(blocks[o_i] + o[1] + blocks[o_i + 1], vars)
                )
                del blocks[o_i : o_i + 2]
                del operators[o_i]
            o_i += 1

    if len(operators) == 1:
        b0 = eval_num(blocks[0], vars)
        b1 = eval_num(blocks[1], vars)
        if operators[0][1] == "+":
            return ftos(b0 + b1)
        if operators[0][1] == "-":
            return ftos(b0 - b1)
        if operators[0][1] == "*":
            return ftos(b0 * b1)
        if operators[0][1] == "/":
            return ftos(b0 / b1)
        if operators[0][1] == "^":
            return ftos(math.pow(b0, b1))
    elif len(operators) == 0:
        return ftos(eval_num(blocks[0], vars))

    return "NaN"


def eval(s, vars, debug_level=1, out_fn=print):
    res = eval_rec(s, vars)
    if debug_level > 2:
        out_fn("DEBUG: " + s + "=" + str(res))
    try:
        return prettyfloat(float(res))
    except ValueError:
        return res
