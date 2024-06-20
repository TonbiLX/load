from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def create_canvas():
    fig = Figure()
    ax = fig.add_subplot(111, projection='3d')
    canvas = FigureCanvas(fig)
    return canvas, ax

def draw_prism(ax, x, y, dx, dy, dz, color, label=None):
    """Draw a rectangular prism with a perspective effect."""
    vertices = np.array([
        [x, y, 0], [x + dx, y, 0], [x + dx, y + dy, 0], [x, y + dy, 0],
        [x, y, dz], [x + dx, y, dz], [x + dx, y + dy, dz], [x, y + dy, dz]
    ])

    faces = [
        [vertices[j] for j in [0, 1, 5, 4]],
        [vertices[j] for j in [7, 6, 2, 3]],
        [vertices[j] for j in [0, 3, 7, 4]],
        [vertices[j] for j in [1, 2, 6, 5]],
        [vertices[j] for j in [0, 1, 2, 3]],
        [vertices[j] for j in [4, 5, 6, 7]]
    ]

    poly3d = [np.array(face) for face in faces]
    collection = Poly3DCollection(poly3d, facecolors=color, edgecolors='black', linewidths=0.3, alpha=0.1)
    ax.add_collection3d(collection)

    if label:
        ax.text(x + dx / 2, y + dy / 2, dz / 2, label, ha='center', va='center', color='white', fontsize=4)
