"""main module"""

# https://github.com/Ryz3D/generate_exam

"""
standard libraries:
    - sys
    - math
    - re
    - subprocess

known bugs:
    - updates total page count on second run
"""

"""
TODO:
    - windows executable (https://packaging.python.org/tutorials/packaging-projects/)
    - batch rename with format (drop .xml)
    - picture width tag
    - make compatible desmos/wolfram/mathlib backend
    - esolve factorial
    - return code errors
    - custom error types (varundefined, expnotsolved)
    - random mode (lower-upper per var)
        - warning when xml set value is outside of range
"""

import os, sys, py.exml, py.egen, py.econv, py.esolve

files_dir = "files/"
aux_dir = "aux_files/"

path_format = files_dir + "{}"
tex_format = files_dir + aux_dir + "{}.tex"
tex_sol_format = files_dir + aux_dir + "sol_{}.tex"
# pdflatex works in files dir -> relative to files/
tex_in_format = aux_dir + "{}.tex"
tex_sol_in_format = aux_dir + "sol_{}.tex"
pdf_format = files_dir + aux_dir + "{}.pdf"
pdf_sol_format = files_dir + aux_dir + "sol_{}.pdf"


def generate_exam(path, solution, debug_level=1, out_fn=print):
    if debug_level > 1:
        out_fn("INFO: generating file from {}".format(path))

    # step 1: parse xml
    data = py.exml.parse_file(path_format.format(path), debug_level)
    if debug_level > 2:
        out_fn("DEBUG: xml parsed")
        out_fn(data)

    # step 2: save as .tex in aux_files
    os.makedirs(files_dir + aux_dir, exist_ok=True)
    py.egen.save_tex(data, False, tex_format.format(path), debug_level, out_fn)
    if debug_level > 2:
        out_fn("DEBUG: tex generated")

    if solution:
        py.egen.save_tex(data, True, tex_sol_format.format(path), debug_level, out_fn)
        if debug_level > 2:
            out_fn("DEBUG: solution tex generated")

    # step 3: run pdflatex to convert to .pdf
    py.econv.convert_pdf(tex_in_format.format(path), debug_level, out_fn)
    if debug_level > 2:
        out_fn("DEBUG: pdf generated")

    if solution:
        py.econv.convert_pdf(tex_sol_in_format.format(path), debug_level, out_fn)
        if debug_level > 2:
            out_fn("DEBUG: solution pdf generated")

    if debug_level > 1:
        out_fn("INFO: completed {}".format(path))


def handle_file(path, solution, debug_level=1, out_fn=print):
    path = path.replace('"', "")

    try:
        with open(path_format.format(path)):
            pass
    except FileNotFoundError:
        out_fn("file not found: {}".format(path_format.format(path)))

    generate_exam(path, solution, debug_level, out_fn)


def move_file(fr, to):
    if os.path.isfile(to):
        os.unlink(to)
    os.rename(fr, to)


def handle_calc_in(i, v, nl="\n"):
    output = ""
    try:
        for exp in i.split(";"):
            exp = exp.strip()
            if exp == "":
                continue
            if "=" in exp:
                key = exp.split("=")[0].strip()
                val = exp.split("=")[1].strip()
                v[key] = py.esolve.eval(val, v)
                output += "{} = {}{}".format(key, v[key], nl)
            else:
                output += py.esolve.eval(exp, v) + nl
    except KeyError as e:
        output += e.args[0] + nl
    return output


def help(out_fn=print):
    out_fn(
        """generate_exam v0.1 usage:

python main.py (OPTIONS) [FILE]

OPTIONS:
    -h      --help      display the usage screen
    -a      --all       execute on all .xml files in "{files}" directory
    -s      --sol       generate exam pdf and solution pdf
    -c      --calc      start interactive expression solver
    -o DIR  --out DIR   specify output directory
    -l LVL  --log LVL   set log level (1: quiet ... 3: verbose)

FILE:
    required unless option -h -a or -c is used
    specify file by filename including .xml extension. place template in "{files}" directory next to this tool. execute from parent directory of "{files}".

WARNING:
    output will automatically be overwritten, make sure files are stored elsewhere

EXAMPLES:
    python main.py -l 3 "example.xml"
    python main.py -a -l 0 -s -o "out"
    python main.py -c
""".format_map(
            {
                "files": files_dir,
            }
        )
    )


def check_flag(out_fn, args, flag1, flag2, param=False):
    present = flag1 in args or flag2 in args
    if not present:
        return
    if param:
        if flag1 in args:
            i = args.index(flag1)
        elif flag2 in args:
            i = args.index(flag2)

        if i == len(args) - 1:
            out_fn("{} option expected parameter".format(args[i]))
        else:
            return args[i + 1]
    else:
        return True


def handle_cli(args=sys.argv, out_fn=print, in_fn=input):
    flag_h = check_flag(out_fn, args, "-h", "--help")
    flag_a = check_flag(out_fn, args, "-a", "--all")
    flag_s = check_flag(out_fn, args, "-s", "--sol")
    flag_c = check_flag(out_fn, args, "-c", "--calc")
    flag_o = check_flag(out_fn, args, "-o", "--out", True)
    flag_l = check_flag(out_fn, args, "-l", "--log", True)

    debug_level = 2
    if flag_l:
        debug_level = int(flag_l)

    if len(args) == 1 or flag_h:
        help(out_fn)
        return
    if flag_c:
        quitters = ["q", "quit", "exit", "quit()", "exit()"]
        out_fn(
            """to quit use Ctrl+C or "{}"
to clear screen and vars use "clear"
""".format(
                '", "'.join(quitters)
            )
        )
        v = {}
        while True:
            try:
                i = in_fn("> ")
            except KeyboardInterrupt:
                return
            if i in quitters:
                return
            elif i == "clear":
                v = {}
                if sys.platform == "win32":
                    os.system("cls")
                else:
                    os.system("clear")
            else:
                out_fn(handle_calc_in(i, v))

    queue = []
    if flag_a:
        for f in os.listdir(files_dir):
            if os.path.isfile(files_dir + f) and f.endswith(".xml"):
                queue.append(f)
    else:
        queue.append(args[-1])

    if debug_level > 1:
        out_fn(
            "INFO: files queued{}: {}".format(
                " (incl. solutions)" if flag_s else "", "; ".join(queue)
            )
        )

    for f in queue:
        handle_file(f, flag_s or False, debug_level, out_fn)

    if type(flag_o) == type(""):
        if not flag_o.endswith("/") and not flag_o.endswith("\\"):
            flag_o += "/"
        if not os.path.isdir(flag_o):
            os.mkdir(flag_o)
        for p in queue:
            move_file(pdf_format.format(p), "{}{}.pdf".format(flag_o, p))
            if flag_s:
                move_file(pdf_sol_format.format(p), "{}sol_{}.pdf".format(flag_o, p))


def main():
    handle_cli()


if __name__ == "__main__":
    main()
