import pyvips
import numpy as np

from ome_types.model import OME, Image, Pixels, Channel
from ome_types.model.simple_types import Color

from skimage import img_as_float, img_as_ubyte


DTYPE_TO_FORMAT = {
    'uint8': 'uchar',
    'int8': 'char',
    'uint16': 'ushort',
    'int16': 'short',
    'uint32': 'uint',
    'int32': 'int',
    'float32': 'float',
    'float64': 'double',
    'complex64': 'complex',
    'complex128': 'dpcomplex',
}

COLORS = (
    Color("white"), Color("red"), Color("lime"), Color("blue"), Color("magenta"), Color("cyan"), Color("yellow")
)

def generate_ome(c, w, h, names, dtype, colors=COLORS, pixel_physical_size=1.0):
    """
    Function generate ome xml meta information
    
    Parameters:
    - c (int): The number of channels
    - w (int): Image width
    - h (int): Image height
    - names (list): List of channel names
    - dtype (str): Images dtype
    - colors (list): List of ome_types.model.simple_types.Color colors
    - pixel_physical_size (float): Pixel size in um
    
    Returns:
    ome_types.model.OME: Composed ome xml for given parameters
    """
    ome_xml = OME()
    colors_2_use = [Color("white")]
    colors_2_use.extend([COLORS[1 + (i % (len(COLORS) - 1))] for i in range(c - 1)])
    # colors_2_use = [COLORS[0]] + 
    
    meta = Image(
        id="Image:0",
        name="resolution_1",
        pixels=Pixels(
            id="Pixels:0", type=str(dtype), dimension_order="XYZCT",
            size_c=c, size_x=w, size_y=h, size_z=1, size_t=1,
            big_endian=True, metadata_only=True,
            channels=[Channel(id=f"Channel:0:{i}", name=names[i], color=colors_2_use[i]) for i in range(c)],
            physical_size_x=pixel_physical_size,
            physical_size_y=pixel_physical_size
        )
    )
    
    ome_xml.images.append(meta)
    return(ome_xml)


def generate_pyvips_images(images, names, colors=COLORS, pixel_physical_size=1.0):
    """
    Generates pyvips images from stack of numpy arrays
    
    Parameters:
    - images (numpy array): stack of numpy images (colors, height, width)
    - names (list): list of channel names
    - colors (list): List of ome_types.model.simple_types.Color colors
    - pixel_physical_size (float): Pixel size in um
    
    Returns:
    pyvips.Image
    """
    c, h, w = images.shape
    ome_xml = generate_ome(c, w, h, names, str(images.dtype), colors, pixel_physical_size)
    # ome_xml = generate_ome(c, w, h, names, colors, str(images.dtype), pixel_physical_size=pixel_physical_size)
    
    res = np.transpose(images, axes=[1, 2, 0])
    res = pyvips.Image.new_from_memory(res.ravel(), w, h, c, DTYPE_TO_FORMAT[str(res.dtype)])
    res = pyvips.Image.arrayjoin(res.bandsplit(), across=1)
    
    res.set_type(pyvips.GValue.gint_type, "page-height", h)
    res.set_type(pyvips.GValue.gstr_type, "image-description", ome_xml.to_xml())
    
    return(res)


def compress_to_8bit(images, q=0.999):
    """
    Compress 16-bit images to 8-bit
    
    Parameters:
    - images (numpy ndarray): stack of numpy images (colors, height, width)
    - qval (float): probability for the quantile to compute
    
    Returns:
    numpy array of 8-bit images
    """
    res = []
    for img in images:
        qval = np.quantile(img, q)
        img[img >= qval] = qval
        
        img = np.array(img, dtype="float")
        img = (img - np.min(img)) / (qval - np.min(img))
        img = img_as_ubyte(img)
        res.append(img)
    return np.array(res)