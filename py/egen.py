"""this module converts parsed .xml to .tex"""

import math, py.exml, py.esolve

lt_packages = ["wrapfig", "graphicx", "textgreek", "amsmath", "caption", "geometry", "fancyhdr", "lastpage"]
lt_linebreak = "\\\\"
lt_smallspace = "\\hfill \\break"
lt_bigspace = "\\vspace{15mm}"


def calc_vars(text):
    vars = {"pi": math.pi, "e": math.e}
    equations = map(lambda t: t.strip(), text.split(";"))
    equations = filter(None, equations)
    for e in equations:
        vars[e.split("=")[0].strip()] = py.esolve.eval(e.split("=")[1].strip(), vars)
    return vars


def resolve_vars(fields, vars):
    result = ""
    if type(fields) == type([]):
        for f in fields:
            if type(f) == type(""):
                result += f
            elif len(f) == 2:
                if f[1] in vars:
                    result += " " + py.esolve.prettyfloat(float(vars[f[1]]))
                else:
                    raise KeyError("ERROR: egen: var not found: {}".format(f[1]))
    else:
        return fields
    return result


def resolve_text(field, vars, ignore_nl=False):
    if type(field) == type([]):
        if field[0] == "p":
            return resolve_vars(field[1], vars) + (
                lt_linebreak if not ignore_nl else ""
            )
        elif field[0] == "picture":
            caption = ""
            try:
                caption = py.exml.get_field(field[1], "caption")
            except KeyError:
                pass
            return """\\begin{{wrapfigure}}{{r}}{{0.3\\textwidth}}
\\centering
\\includegraphics[width=.95\linewidth]{{{src}}}
\\caption*{{{caption}}}
\\end{{wrapfigure}}
""".format_map(
                {
                    "src": py.exml.get_field(field[1], "src"),
                    "caption": caption,
                }
            )
        else:
            return ""
    else:
        return field


def resolve_all(field, vars, ignore_nl=False, sep=""):
    return sep.join(map(lambda f: resolve_text(f, vars, ignore_nl), field))


def generate_tex(data, solution=False, debug_level=1, out_fn=print):
    ex = py.exml.get_field(py.exml.get_field(data, "xml"), "excercise")
    vars = calc_vars(py.exml.get_field(ex, "variables"))
    intro = resolve_all(py.exml.get_field(ex, "intro"), vars)

    tex_data = {
        "lt_packages": "\n".join(
            map(lambda p: "\\usepackage{{{}}}".format(p), lt_packages)
        ),
        "title": py.exml.get_field(ex, "title"),
        "variables": str(vars),
        "intro": intro,
        "points_sum": 0,
        "questions": "",
    }

    q_ids = []
    questions = py.exml.get_fields(ex, "question")
    for ques_i in range(len(questions)):
        ques = questions[ques_i]
        q_id = py.exml.get_field(ques, "id")
        q_ids.append(q_id)
        dependency_fields = py.exml.get_fields(ques, "depends")
        dependencies = []
        for dep in dependency_fields:
            if type(dep) == type([]):
                dependencies.extend(dep)
            else:
                dependencies.append(dep)
        for dep_i in range(len(dependencies)):
            try:
                dependencies[dep_i] = q_ids.index(dependencies[dep_i])
            except KeyError:
                raise KeyError(
                    "ERROR: egen: could not find dependency '{}'".format(dependencies[dep_i])
                )
        dep_str = ""
        if len(dependencies) > 0:
            dep_str = """Benötigt Aufgabenteil{} {}{}""".format(
                "e" if len(dependencies) > 1 else "",
                ", ".join(map(lambda x: chr(ord("a") + x) + ")", dependencies)),
                lt_linebreak + lt_smallspace,
            )

        sol_lines = 1
        try:
            solution_field = py.exml.get_field(ques, "solution")
            sol_lines = len(solution_field)
        except KeyError:
            pass
        
        q_points = int(py.exml.get_field(ques, "points"))
        tex_data["points_sum"] += q_points
        tex_data[
            "questions"
        ] += """\subsection*{{{letter}) {task} ({points}P)}}

{solution}
""".format_map(
            {
                "letter": chr(ord("a") + ques_i),
                "id": q_id,
                "points": q_points,
                "task": resolve_all(py.exml.get_field(ques, "task"), vars, True),
                "solution": lt_bigspace * sol_lines
                if not solution
                else (
                    dep_str + resolve_all(solution_field, vars, False, lt_smallspace)
                ),
            }
        )

    if debug_level > 2:
        out_fn("DEBUG: generated {} questions{}, completing .tex".format(len(questions), " and solutions" if solution else ""))

    return """\\documentclass{{article}}
{lt_packages}
\\geometry{{
    a4paper,
    total={{170mm,257mm}},
    left=20mm,
    top=20mm,
}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[RE,LO]{{Name:}}
\\fancyfoot[RE,LO]{{Gesamtpunktzahl: {points_sum}P}}
\\fancyfoot[LE,RO]{{Seite \\thepage/\\pageref{{LastPage}}}}

\\graphicspath{{ {{./pictures/}} }}

\\begin{{document}}

\\part*{{{title}}}

{intro}
{questions}

\\end{{document}}
""".format_map(
        tex_data
    )


def save_tex(data, solution, path, debug_level=1, out_fn=print):
    tex = generate_tex(data, solution, debug_level, out_fn)
    if debug_level > 2:
        if solution:
            out_fn("DEBUG: saving solution file at '{}'".format(path))
        else:
            out_fn("DEBUG: saving file at '{}'".format(path))
    with open(path, "wt", encoding="utf-8") as f:
        f.write(tex)
    return tex
