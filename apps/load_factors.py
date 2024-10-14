LOAD_COMB_EC = {
    "LC1": {"D_fact": 1.35},
    "LC2a": {"D_fact": 1.35, "Cs_fact": 1.5},
    "LC2b": {"D_fact": 1.35, "Cw_fact": 1.5},
    "LC3a": {"D_fact": 1.35, "Wp_fact": 1.5, "S_fact": 1.05},
    "LC3b": {"D_fact": 1.35, "Ws_fact": 1.5},
    "LC4a": {"D_fact": 1.35, "L_fact": 1.5, "S_fact": 1.05},
}


def ec_eurocode_combs():
    LOAD_COMB_EC2 = {
        "LC1": {"D":1.35},
        "LC2a": {"D":1.35,"Cs":1.5},
        "LC2b": {"D":1.35,"Cw":1.5},
        "LC3a": {"D":1.35,"Wp":1.5,"S":1.05},
        "LC3b": {"D":1.35,"Ws":1.5},
        "LC4a": {"D":1.35,"L":1.5,"S":1.05},
    }
    return LOAD_COMB_EC2

def factor_load(D: float=0, D_fact: float=0, 
                Cs: float=0, Cs_fact: float = 0, 
                Cw: float=0, Cw_fact: float= 0, 
                Wp: float=0, Wp_fact: float=0, 
                Ws:float=0, Ws_fact:float=0,
                L: float=0, L_fact:float=0, 
                S:float=0, S_fact:float = 0,
               ) -> float:
    """
    Returns the factored load with the given loads (D, Cs etc.) and load factors (D_fact, Cs_fact etc.)
    """
    factored_load = D*D_fact + Cs*Cs_fact + Cw*Cw_fact + Wp*Wp_fact + Ws*Ws_fact + L *L_fact + S*S_fact
    return factored_load



def max_factored_load(loads: dict, load_combs:dict) -> float:
    factored_loads={}
    for LC_name, comb_content in load_combs.items():
        #print(LC_name)
        #print(comb_content)
        factored_load = factor_load(**loads, **comb_content)
        factored_loads.update({LC_name: factored_load})
    #print(factored_loads)
    the_worst_case = max(factored_loads, key=lambda k:factored_loads[k])
    #print(the_worst_case)
    max_factored_load = max(factored_loads.values())
    #max_factored_load = factored_loads[the_worst_case]
    #print(max_factored_load)
    # print(f"The load combination which leads to the maximum factored load is {the_worst_case} and the maximum factored load is {max_factored_load}")
    # full_LC_name= load_combs[the_worst_case]
    # print(f"The related load combination is {the_worst_case}={full_LC_name}")
    return max_factored_load



def min_factored_load(loads: dict, load_combs:dict) -> float:
    factored_loads={}
    for LC_name, comb_content in load_combs.items():
        #print(LC_name)
        #print(comb_content)
        factored_load = factor_load(**loads, **comb_content)
        factored_loads.update({LC_name: factored_load})
    #print(factored_loads)
    the_best_case = min(factored_loads, key=lambda k:factored_loads[k])
    #print(the_worst_case)
    min_factored_load = min(factored_loads.values())
    #max_factored_load = factored_loads[the_worst_case]
    #print(max_factored_load)
    print(f"The load combination which leads to the minimum factored load is {the_best_case} and the minimum factored load is {min_factored_load}")
    full_LC_name= load_combs[the_best_case]
    print(f"The related load combination is {the_best_case}={full_LC_name}")



def envelope_max(results_arrays: dict) -> list[list[float], list[float]]:

    """
    Returns the maximum factored loads across all factored values exist in results_arrays.

    'result_arrays': a dict of factored result arrays for an action on a specific framing member,
        keyed by load combo name. The result array values are a Nx2 array where the x-coordinates
        are in index 0 and the y-coordinates are in index 1. It's obtained with extract_arrays_all_combos
        function.
    """
    all_results = []
    
    for results_array in results_arrays.values():
        all_results.append(results_array[1])
        x_loc = results_array[0]
    
    enveloped_result = []
    
    for idx, a in enumerate(x_loc):
        temporary_list = []
        for each_result in all_results:
            temporary_list.append(each_result[idx])
        enveloped_result.append(max(temporary_list))
    
    return [x_loc, enveloped_result]



def envelope_min(results_arrays: dict) -> list[list[float], list[float]]:
    
    """
    Returns the minimum factored loads across all factored values exist in results_arrays.

    'result_arrays': a dict of factored result arrays for an action on a specific framing member,
        keyed by load combo name. The result array values are a Nx2 array where the x-coordinates
        are in index 0 and the y-coordinates are in index 1. It's obtained with extract_arrays_all_combos
        function.
    """

    all_results = []
    
    for results_array in results_arrays.values():
        all_results.append(results_array[1])
        x_loc = results_array[0]
    
    enveloped_result = []
    
    for idx, a in enumerate(x_loc):
        temporary_list = []
        for each_result in all_results:
            temporary_list.append(each_result[idx])
        enveloped_result.append(min(temporary_list))
    
    return [x_loc, enveloped_result]
