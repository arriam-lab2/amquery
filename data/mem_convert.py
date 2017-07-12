if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python", __file__, "kbytes")
        exit
    else:
        size = sys.argv[1]
        print(float(size) / 1024)