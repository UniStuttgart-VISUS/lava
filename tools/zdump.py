import argparse
import zlib

parser = argparse.ArgumentParser(usage="%(prog)s <FILE>", description="dump a zlib-compressed string column to stdout")
parser.add_argument('files', nargs="*")
args = parser.parse_args()

if not args.files:
    print("need at least one input file")
    exit(1)
for file in args.files:
    with open(file, 'rb') as infile:
        comp = infile.read()
        uncomp = zlib.decompress(comp)
        print(uncomp.decode('utf-8'))