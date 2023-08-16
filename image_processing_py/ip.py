import numpy as np
import mahotas as mh
import tqdm

def edof(imgs):
    """
    Performs extended depth of focus (edof)
    
    Parameters:
        - imgs (numpy ndarray): z-stack of images
        
    Returns:
        (numpy ndarray): Image with performed edof
    """
    focus = np.array([mh.sobel(t, just_filter=True) for t in imgs])
    best = np.argmax(focus, 0)
    
    flat_stack = imgs.reshape((imgs.shape[0], -1))
    flat_stack = flat_stack.transpose()
    edof_img = flat_stack[np.arange(len(flat_stack)), best.ravel()]
    edof_img = edof_img.reshape(imgs.shape[1:])
    
    return edof_img