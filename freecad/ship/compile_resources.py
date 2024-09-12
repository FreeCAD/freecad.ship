import os
import subprocess as sub


PYSIDE_VERSIONS = [6, 2]


def compile_resources(quiet=True):
    # try to create a resource file
    # assume either pyside2-rcc or pyside-rcc are available.
    # if both are available pyside2-rcc is used.
    rc_input = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources", "Ship.qrc"))
    rc_output = os.path.join(os.path.dirname(__file__), "Ship_rc.py")
    for version in PYSIDE_VERSIONS + ['']:
        try:
            exe = "pyside" + str(version) + "-rcc"
            proc = sub.Popen([exe, "-o", rc_output, rc_input],
                             stdout=sub.PIPE,
                             stderr=sub.PIPE,
                             universal_newlines=True)
            out, err = proc.communicate()
        except FileNotFoundError:
            continue
        if not quiet:
            print(out)
            print(err)
        break


if __name__ == '__main__':
    compile_resources(quiet=False)
