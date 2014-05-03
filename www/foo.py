
def main():
    name = "anon"
    if "__web__" in globals():
        name = request.args.get("name") or name

    print "Hello there {}".format(name)

if __name__ == '__main__':
    main()
