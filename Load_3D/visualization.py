from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

def create_canvas():
    canvas = FigureCanvas(Figure())
    ax = canvas.figure.add_subplot(111, projection='3d')
    return canvas, ax
