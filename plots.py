import eng_module.beams as beams
from typing import Optional
from PyNite import FEModel3D
from PyNite.Visualization import render_model
from math import pi
import eng_module.load_factors as lf
from plotly import graph_objects as go
import plotly.express as px
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, ScalarFormatter
import numpy as np
import matplotlib.pyplot as plt


def plot_results(
    beam_model: FEModel3D,
    result_type: str,
    direction: Optional[str] = None,
    units: Optional[str] = None,
    load_combo: Optional[str] = None,
    figsize=(8, 3),
    dpi=150,
    n_points=1000,
) -> Figure:

    """
    Returns a matplotlib figure of the analysis results in 'beam_model' according to the 'result_type' and 'direction'
    result_type: str, one of {"shear", "moment", "torque", "axial", "deflection"}
    direction: str, one of {"Fy", "Fx", "Fz"} (applicable to shear), {"Mx", "My", "Mz"} (applicable to moment), or
        {"dx", "dy", "dz"} (applicable to deflection)
    units: not implemented yet!!!
    load_combo: if not None, then the provided load combo will be plotted within the envelope, if present in the model.
    if none, the envelope results will be provided.
    """

    fig = Figure(figsize=figsize, dpi=dpi)
    ax = fig.gca()

    result_arrays = beams.extract_arrays_all_combos(
        beam_model,
        result_type,
        direction,
        n_points
    )
    
    x_locs = list(result_arrays.values())[0][0]

    if load_combo is None:
        max_result_env = beams.envelope_max(result_arrays)[1]   #ENVELOPE PART
        min_result_env = beams.envelope_min(result_arrays)[1]

        max_result_env_array = np.array(max_result_env)
        min_result_env_array = np.array(min_result_env)
        
        ax.plot(x_locs, [0] * len(x_locs), color = 'green')
        ax.plot(x_locs, max_result_env_array, color = 'blue')
        ax.plot(x_locs, min_result_env_array, color = 'red')

        ax.fill_between(x_locs, 0, max_result_env, where=(max_result_env_array >= 0), color='blue', alpha=0.3)
        ax.fill_between(x_locs, 0, min_result_env, where=(min_result_env_array < 0), color='red', alpha=0.3)

        if result_type == 'moment':
            ax.set_title("Moment Diagram", fontsize = 12)    
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Resulting Moment, N.mm', fontsize = 8)

        elif result_type == 'shear':
            ax.set_title("Shear Diagram", fontsize = 12)
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Shear Value, N', fontsize = 8)

        elif result_type == 'axial':
            ax.set_title("Axial Diagram", fontsize = 12)
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Axial Value, N', fontsize = 8)

        elif result_type == 'torque':
            ax.set_title("Torque Diagram", fontsize = 12)
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Torque Value, N.mm', fontsize = 8)

        elif result_type == 'deflection':
            ax.set_title("Deflection Diagram", fontsize = 12)
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Deflection, mm', fontsize = 8)
    
    
    else:
        # Extract the demanded load combo array.
        selected_results = result_arrays[load_combo]

        # Extract the results.
        results = selected_results[1]
        
        # Draw the plots.
        ax.plot(x_locs, [0] * len(x_locs), color = 'green')
        ax.plot(x_locs, results, color = 'orange')
        
        if result_type == 'moment':
            ax.fill_between(x_locs, 0, results, where=(results >= 0), color='blue', alpha=0.5)
            ax.fill_between(x_locs, 0, results, where=(results < 0), color='red', alpha=0.5)
            
            ax.set_title("Moment Diagram", fontsize = 12)
            
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Resulting Moment, N.mm', fontsize = 8)

        elif result_type == 'shear':
            ax.fill_between(x_locs, 0, results, where=(results >= 0), color='blue', alpha=0.5)
            ax.fill_between(x_locs, 0, results, where=(results < 0), color='red', alpha=0.5)
            
            ax.set_title("Shear Diagram", fontsize = 12)
            
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Shear Value, N', fontsize = 8)

        elif result_type == 'axial':
            ax.fill_between(x_locs, 0, results, where=(results >= 0), color='blue', alpha=0.5)
            ax.fill_between(x_locs, 0, results, where=(results < 0), color='red', alpha=0.5)
            
            ax.set_title("Axial Diagram", fontsize = 12)
            
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Axial Value, N', fontsize = 8)

        elif result_type == 'torque':
            ax.fill_between(x_locs, 0, results, where=(results >= 0), color='blue', alpha=0.5)
            ax.fill_between(x_locs, 0, results, where=(results < 0), color='red', alpha=0.5)
            
            ax.set_title("Torque Diagram", fontsize = 12)
            
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Torque Value, N.mm', fontsize = 8)

        elif result_type == 'deflection':
            ax.fill_between(x_locs, 0, results, where=(results >= 0), color='blue', alpha=0.5)
            ax.fill_between(x_locs, 0, results, where=(results < 0), color='red', alpha=0.5)
            
            ax.set_title("Deflection Diagram", fontsize = 12)
            
            ax.set_xlabel('Beam Length, mm', fontsize = 8)
            ax.set_ylabel('Deflection, mm', fontsize = 8)

            max_result = max(results)
            max_loc_idx = list(results).index(max_result)
            max_loc = x_locs[max_loc_idx]

            #text = f' The maximum deflection occurred at {max_loc} with the value of {max_result}.'


    ax.tick_params(axis = 'x', labelsize = 8, rotation = -90)
    ax.tick_params(axis = 'y', labelsize = 8)
    
    ax.get_xaxis().get_offset_text().set_size(8)
    
    ax.xaxis.set_major_locator(MaxNLocator(nbins=20))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=10))
    
    ax.grid(True, color = 'gray', linestyle = ':', linewidth=0.5, alpha=0.7)

       

    # display(fig)
    # print(text)

    return fig