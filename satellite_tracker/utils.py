import numpy as np

def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def smooth_path(points, window=3):
    if len(points) < window:
        return points
    return [
        tuple(np.mean(points[i:i+window], axis=0))
        for i in range(len(points) - window + 1)
    ]
