"""this module converts .tex to .pdf"""

import subprocess


def convert_pdf(path, debug_level=1, out_fn=print):
    cmd = 'pdflatex -aux-directory=aux_files {}-interaction nonstopmode "{}"'.format(
        "-quiet " if debug_level < 3 else "", path
    )

    proc = subprocess.Popen(cmd, cwd="files", stdout=subprocess.PIPE)
    comm = proc.communicate()
    if comm[1]:
        out_fn("ERROR: " + comm[1].decode("utf-8"))
    if comm[0]:
        out_fn("OUTPUT: " + comm[0].decode("utf-8"))
