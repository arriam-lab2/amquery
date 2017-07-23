import numpy as np
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python", __file__, "kbytes")
        exit
    else:
        size = sys.argv[1]
        print(np.around(float(size) / 1024, decimals=2))