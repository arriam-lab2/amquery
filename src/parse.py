
def parse_otu_table(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

        otus = lines[0].strip().split('\t')
        print(otus)

        for line, otu in zip(lines[1:], otus):
            data = line.replace(otu + '\t', '')
            print(otu, ": ", data)

            #otus = lines[0].strip().split('\t')

if __name__ == "__main__":
    parse_otu_table("data/unweighted_unifrac_otu_table.txt")
