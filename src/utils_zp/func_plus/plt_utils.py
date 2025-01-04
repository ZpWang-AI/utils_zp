from ..core import *


def plot_curve(
    *xys, title:str=None, savefig_path:str=None,
    x_name:str=None, y_name:str=None,
    x_range:Tuple[float, float]=None, y_range:Tuple[float, float]=None,
    close:bool=False,
):
    # from matplotlib import pyplot as plt
    plt.plot(*xys,)
    plt.title(title)
    if x_name is not None:
        plt.xlabel(x_name)
    if y_name is not None:
        plt.ylabel(y_name)
    if x_range is not None:
        plt.xlim(x_range)
    if y_range is not None:
        plt.ylim(y_range)
    if savefig_path is not None:
        plt.savefig(savefig_path)
    if close:
        plt.close()
        
        
def mark_extremum(
    x, y, 
    mark_max=False, mark_min=False, 
    format_y_func=None,
):
    from matplotlib import pyplot as plt
    if format_y_func is None:
        format_y_func = lambda y:y
    if mark_max:
        mid = np.argmax(y)
        plt.text(x[mid], y[mid], str(format_y_func(y[mid])))
    if mark_min:
        mid = np.argmin(y)
        plt.text(x[mid], y[mid], str(format_y_func(y[mid])))
        

def plot_hist(data, bins, fig_path):
    from matplotlib import pyplot as plt
    pd.Series(data).hist(bins=bins)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig(fig_path)
    plt.close()
    

def visualize_1d_matrix(matrix, fig_path):
    from matplotlib import pyplot as plt
    x, y = list(range(len(matrix))), sorted(matrix)
    plt.scatter(x, y,)
    mark_extremum(x,y,True,True)
    
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.savefig(fig_path)