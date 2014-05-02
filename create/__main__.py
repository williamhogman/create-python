def main():
    from create.server import ScriptServer
    from create.code import CodeManager

    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, ScriptServer(CodeManager("www")))

main()