# Image Processing Scripts with Python

Welcome to the Image Processing Python Package repository! This package provides a collection of methods and utilities for various image processing tasks in Python.

## Installation

To install this package, ensure you have Python `>=3.10` installed. You can install the package using `pip`:

```bash
pip install git+https://github.com/vdsukhov/image_processing_py
```

## Functionality

- `image_processing_py.ometif.generate_ome` - This function generates OME metadata for creating OME-TIFF images, primarily utilizing the `ome_types` package.
- `image_processing_py.ometif.generate_pyvips_images` - This function converts a stack of NumPy arrays into pyvips images, which can be saved as pyramidal OME-TIFF files. For example, you can achieve this with the following command: `imgs.tiffsave(out_path, compression='lzw', Q=75, tile_width=2048, tile_height=2048, pyramid=True, subifd=True, bigtiff=True)`. Note that these arguments are provided as an example.
- `image_processing_py.utils.labels_to_features` - This function converts a labeled image into a GeoJSON FeatureCollection, making it compatible with QuPath.
- `image_processing_py.utils.geojson_to_tiff` - This function takes a GeoJSON file containing segmented cells and converts it into a labeled image.

