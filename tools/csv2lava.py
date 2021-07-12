import argparse
import os
import zlib
import pandas as pd

from dataclasses import (dataclass, field)
from dataclasses_json import dataclass_json
from numpy import float32, float64, int32, int64
from typing import List

the_ext = ".lava"

@dataclass_json
@dataclass
class DataBuffer:
    type: str
    elem_type: str = None
    data: List = None #field(default_factory=list)
    encoding: str = "raw"
    uri: str = ""

@dataclass_json
@dataclass
class Attribute:
    id: str
    buffer: int


@dataclass_json
@dataclass
class LavaData:
    attributes: List[Attribute] = field(default_factory=list)
    buffers: List[DataBuffer] = field(default_factory=list)

parser = argparse.ArgumentParser(usage="%(prog)s <FILE>", description="convert a .csv file to binary blobs with index")
parser.add_argument('files', nargs="*")
parser.add_argument('--force-float', help="Write floats instead of doubles. You can add column names to specify, otherwise all are converted.", action='store', nargs="*")
parser.add_argument('--force-int', help="Write ints instead of longs. You can add column names to specify, otherwise all are converted.", action='store', nargs="*")
parser.add_argument('--force-uncompressed', help="Do not compress string columns. You can add column names to specify, otherwise all are converted.", action='store', nargs="*")
args = parser.parse_args()

def force_float(colname: str) -> bool:
    if type(args.force_float) == list:
        if len(args.force_float) == 0:
            # everything to floats!
            return True
        else:
            return colname in args.force_float
    else:
        return False

def force_int(colname: str) -> bool:
    if type(args.force_int) == list:
        if len(args.force_int) == 0:
            # everything to ints!
            return True
        else:
            return colname in args.force_int
    else:
        return False

def force_uncompressed(colname: str) -> bool:
    if type(args.force_uncompressed) == list:
        if len(args.force_uncompressed) == 0:
            # everything to uncompressed!
            return True
        else:
            return colname in args.force_uncompressed
    else:
        return False

if not args.files:
    print("need at least one input file")
    exit(1)
for file in args.files:
    dataname, file_extension = os.path.splitext(os.path.basename(file))
    dir = os.path.dirname(file)
    data = pd.read_csv(f'{dir}{os.sep}{dataname}.csv')
    print(f'converting {file} to {dir}{os.sep}{dataname}{the_ext} (and blobs)')

    outdata = LavaData()

    print(f'\tfound {data.columns.size} columns in data')
    for col in data:
        c = data[col]
        
        if c.dtype == int64 or c.dtype == float64:
            b = DataBuffer(type = "binary")
            npthing = c.to_numpy()
            if c.dtype == int64:
                if (force_int(c.name)):
                    b.elem_type = "int"
                    npthing = npthing.astype(int32)
                else:
                    b.elem_type = "long"
            elif c.dtype == float64:
                if (force_float(c.name)):
                    b.elem_type = "float"
                    npthing = npthing.astype(float32)
                else:
                    b.elem_type = "double"
            
            if c.dtype == npthing.dtype:
                print(f'\tcolumn {c.name}: {c.dtype}')
            else:
                print(f'\tcolumn {c.name}: {c.dtype}, written as {npthing.dtype}')
                
            b.uri = f'{dataname}_{c.name}.bin'
            outdata.buffers.append(b)
            print(f'\t\twriting blob {b.uri}')
            npthing.tofile(f'{dir}{os.sep}{b.uri}')
        else:
            b = DataBuffer(type = "text")
            b.elem_type = "string"
            outblob: str = c.to_csv(None, index=False, header=False, line_terminator="\n")
            if (force_uncompressed(c.name)):
                print(f'\tcolumn {c.name}: {c.dtype}, written as string')
                b.uri = f'{dataname}_{c.name}.txt'
                print(f'\t\twriting blob {b.uri}')
                with open(f'{dir}{os.sep}{b.uri}', 'wb') as obf:
                    obf.write(outblob.encode('utf-8'))

            else:
                print(f'\tcolumn {c.name}: {c.dtype}, written as compressed string')
                b.encoding = "zlib"
                b.uri = f'{dataname}_{c.name}.ztxt'
                print(f'\t\twriting blob {b.uri}')
                cmpblob = zlib.compress(outblob.encode('utf-8'))
                with open(f'{dir}{os.sep}{b.uri}', 'wb') as obf:
                    obf.write(cmpblob)

            outdata.buffers.append(b)



        dc = Attribute(id = c.name, buffer = len(outdata.buffers) - 1)
        outdata.attributes.append(dc)


    with open(f'{dir}{os.sep}{dataname}{the_ext}', "w") as tf:
        tf.write(outdata.to_json(indent=True))