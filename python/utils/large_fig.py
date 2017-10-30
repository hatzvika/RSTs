import matplotlib.pyplot as plt


def large_fig(total_lat, total_lon):
    aspect_ratio = total_lon / total_lat
    if aspect_ratio <= (16 / 9):
        size_y = 12
        size_x = size_y * aspect_ratio
    else:
        size_x = 20
        size_y = size_x / aspect_ratio

    return plt.figure(num=None, figsize=(size_x, size_y), dpi=80, facecolor='w', edgecolor='k')

