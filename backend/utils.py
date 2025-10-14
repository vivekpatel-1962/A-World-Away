import cv2
import numpy as np
from scipy import signal
from typing import Optional

N_FLUX_DEFAULT = 3196

def image_to_flux(img_bgr: np.ndarray, target_steps: int = N_FLUX_DEFAULT) -> np.ndarray:
    """
    Convert a light curve image (BGR) into a 1D normalized flux array.
    
    Args:
        img_bgr: Input BGR image (numpy array)
        target_steps: Desired length of output array
        
    Returns:
        np.ndarray: Normalized flux values in range [0, 1]
    """
    if img_bgr is None or not isinstance(img_bgr, np.ndarray):
        raise ValueError("Input must be a valid BGR numpy image")
    
    if img_bgr.ndim != 3 or img_bgr.shape[2] != 3:
        raise ValueError("Expected a BGR image with 3 channels")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Auto-detect and handle inverted images (dark curve on light background)
    if np.mean(gray) > 127:  # If image is mostly white
        gray = 255 - gray
    
    # Adaptive thresholding works better for varying backgrounds
    binary = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 2
    )
    
    # Find the curve by taking the topmost point in each column
    h, w = binary.shape
    flux = []
    
    for x in range(w):
        column = binary[:, x]
        y_positions = np.where(column > 0)[0]
        if len(y_positions) > 0:
            # Take the topmost point in each column
            y = np.min(y_positions)
            flux.append(float(y))
        else:
            flux.append(np.nan)
    
    flux = np.array(flux, dtype=np.float32)
    
    # Handle any NaN values by linear interpolation
    if np.isnan(flux).any():
        x = np.arange(len(flux))
        mask = ~np.isnan(flux)
        if mask.sum() > 0:  # If we have at least one valid point
            flux = np.interp(x, x[mask], flux[mask])
        else:
            flux = np.zeros_like(flux)
    
    # Apply smoothing to reduce noise
    if len(flux) > 10:  # Only if we have enough points
        flux = signal.savgol_filter(flux, window_length=min(51, len(flux)//4*2+1), polyorder=2)
    
    # Normalize to [0, 1] (inverted since y=0 is top of image)
    flux = 1.0 - (flux / h)
    
    # Ensure values are within [0, 1] after processing
    flux = np.clip(flux, 0.0, 1.0)
    
    # Resample to target length if needed
    if target_steps and len(flux) != target_steps:
        x_old = np.linspace(0, 1, len(flux))
        x_new = np.linspace(0, 1, target_steps)
        flux = np.interp(x_new, x_old, flux)
    
    return flux.astype(np.float32)
