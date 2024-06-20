import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

def create_canvas():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_box_aspect([1, 1, 1])
    canvas = FigureCanvasQTAgg(fig)
    return canvas, ax

def draw_prism(ax, x, y, dx, dy, dz, color, label=None):
    """Draw a rectangular prism with given dimensions."""
    vertices = [
        [x, y, 0], [x + dx, y, 0], [x + dx, y + dy, 0], [x, y + dy, 0],
        [x, y, dz], [x + dx, y, dz], [x + dx, y + dy, dz], [x, y + dy, dz]
    ]
    vertices = np.array(vertices)

    faces = [
        [vertices[j] for j in [0, 1, 5, 4]],
        [vertices[j] for j in [7, 6, 2, 3]],
        [vertices[j] for j in [0, 3, 7, 4]],
        [vertices[j] for j in [1, 2, 6, 5]],
        [vertices[j] for j in [0, 1, 2, 3]],
        [vertices[j] for j in [4, 5, 6, 7]]
    ]
    poly3d = [[tuple(p) for p in face] for face in faces]
    ax.add_collection3d(Poly3DCollection(poly3d, facecolors=color, linewidths=0.4, edgecolors='black', alpha=0.1))
