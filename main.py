from traceback import print_exc

from code.shell import ACLShell


def loop(shell):
    try:
        shell.cmdloop()
    except Exception:
        print_exc()
        loop(shell)


if __name__ == '__main__':
    aclshell = ACLShell()
    loop(aclshell)
