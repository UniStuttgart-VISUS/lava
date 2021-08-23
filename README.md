# Lightweight annotated value arrays (lava) file format

A minimalistic file format for storing and transmitting data.
The format has two primary goals:
1) To be human-readable and expressive enough to allow parsing existing files without additional documentation.
2) To provide the option of storing binary data for efficient storage and I/O.

Lava files use JSON syntax.
Each lava file can contain data of multiple attributes and each attribute is associated with a one-dimensional array of values.
Value arrays are either stored directly within a lava file in ASCII-format or stored in seperate binary files (.bin) that are referenced from the lava file.
Each value array is annotated with semantic and structural information.

## Specification

Each .lava file contains two top-level arrays: `attributes` and `buffers`.

### `attributes`
Contains the semantic information of stored data attributes.
Each entry consists of the following key-value pairs:
* `name`: string-valued name of the data attribue
* `index`: index into `buffers`

### `buffers`
Contains the structural information of stored data and optionally the values themselves.
Each entry consists of the following key-value pairs:
* `type`: { binary, ascii }
* `elem_type`: { double, long, string }

For binary data:
* `data`: null
* `encoding`: {raw, lz4, ... }
* `uri`: file path to a .bin file relative to the .lava file

For ascii data:
* `data`: array of values of type `elem_type`
* `encoding`: null
* `uri`: null

## Example

Example files can be found in \examples.
A basic ascii .lava file for two attributes and three values per attribute (i.e. three data points) looks like this:
```
{
    "attributes": [
        {
            "name": "v0",
            "buffer": 0
        },
        {
            "name": "v1",
            "buffer": 1
        }
    ],
    "buffers": [
        {
            "type": "ascii",
            "elem_type": "double",
            "data": [0.1, 0.5, 1.2],
            "encoding": null,
            "uri": null
        },
        {
            "type": "ascii",
            "elem_type": "long",
            "data": [3, 5, 4],
            "encoding": null,
            "uri": null
        }
    ]
}
```


## Usage scenarios

### Short-term storage
...

### Long-term storage
...

### Realtime transmission
...
