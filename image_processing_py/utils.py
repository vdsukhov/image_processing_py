import re
import rasterio.features
import numpy as np
import geopandas as gpd

from rasterio.transform import Affine
from typing import Union
from skimage.draw import polygon


def convert_win_path_to_linux(path):
    """
    Function converts the windows path to wsl linux path
    
    Parameters:
        - path (str): window path (should be a raw string)
    
    Returns:
        (str): converted path for wsl system
    """
    
    prefix = re.match("^\w", path)[0].lower()
    prefix = f"/mnt/{prefix}"
    suffix = re.sub(r"^\w:", "", path)
    suffix = re.sub(r"\\+", "/", suffix)

    return f"{prefix}{suffix}"


# next function taken from here:
# https://gist.github.com/petebankhead/77782fd6d684e18efb2447980fdfbb90
def labels_to_features(lab: np.ndarray, object_type='annotation', connectivity: int=4, 
                      transform: Affine=None, mask=None, downsample: float=1.0, include_labels=False,
                      classification=None):
    """
    Create a GeoJSON FeatureCollection from a labeled image
    Function originally taken from here: https://gist.github.com/petebankhead/77782fd6d684e18efb2447980fdfbb90
    
    Parameters:
        - lab: labeled image
        - object_type (str): property object type
        - connectivity (int): Use 4 or 8 pixel connectivity for grouping pixels into features
        - transform (Affine): Affine transformation optional
        - mask (bool): bool mask 
        - downsample (float): scale factor to scale coordinates
        - include_labels (bool): should labeles be included
        - classification (str): properties classification type?
    
    Returns:
        (list): list with features in form of dictionaries
    """
    features = []
    
    # Ensure types are valid
    if lab.dtype == bool:
        mask = lab
        lab = lab.astype(np.uint8)
    else:
        mask = lab > 0
    
    # Create transform from downsample if needed
    if transform is None:
        transform = Affine.scale(downsample)
    
    # Trace geometries
    for s in rasterio.features.shapes(lab, mask=mask, 
                                      connectivity=connectivity, transform=transform):

        # Create properties
        props = dict(object_type=object_type)
        if include_labels:
            props['measurements'] = [{'name': 'Label', 'value': s[1]}]
            
        # Just to show how a classification can be added
        if classification is not None:
            props['classification'] = classification
        
        # Wrap in a dict to effectively create a GeoJSON Feature
        po = dict(type="Feature", geometry=s[0], properties=props)

        features.append(po)
    
    return features


def geojson_to_tiff(gdf: gpd.GeoDataFrame, shape: Union[tuple, list, np.ndarray], dtype: np.dtype = np.int32) -> np.ndarray:
    """
    Converts a GeoDataFrame containing polygons into a labeled image (numpy array).

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame containing polygons to convert into image labels.
        shape (Union[tuple, list, np.ndarray]): Shape of the output image as (height, width).
        dtype (np.dtype): Data type for the output image labels.

    Returns:
        np.ndarray: Labeled image where each polygon in gdf is represented by a unique label.

    Raises:
        AssertionError: If any geometry in gdf is not a Polygon.

    Notes:
        - Currently, only polygons are supported as geometries for converting into images.
    """
    labels = np.zeros(shape, dtype=dtype)
    
    assert np.all([elem.geom_type == "Polygon" for elem in gdf['geometry']]), \
        "Currently, only polygons are supported as geometries for converting into images."
    
    for i, geom in enumerate(gdf['geometry']):
        coords = np.array(geom.exterior.coords[:-1])
        pxx, pyy = polygon(coords[:, 1], coords[:, 0], labels.shape)
        labels[pxx, pyy] = i + 1
    
    return labels
    
    