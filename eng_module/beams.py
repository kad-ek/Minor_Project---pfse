from math import pi
from PyNite import FEModel3D
import csv
from PyNite.Visualization import render_model
from eng_module.utils import str_to_int, str_to_float, read_csv_file
from typing import Optional



### WORKBOOK06


def extract_arrays_all_combos(
    solved_beam_model: FEModel3D,
    result_type: str,
    direction: Optional[str],
    n_points: int = 200,
) -> dict:
    
    """
    Returns a dictionary keyed by load combo name that contains the resulting arrays of the 'solved_beam_model',
    for the given 'result_type' and 'direction' with 'n_points' as the number of values in the array.

    'solved_beam_model': A PyNite.FEModel3D object that contains one member and has been successfully analyzed
    'result_type': str, one of {'shear', 'moment', 'deflection', 'axial', 'torque'}
    'direction': str that corresponds to the 'result_type':
        'shear': {'Fy', 'Fz'}
        'moment': {'Mz', 'My'}
        'deflection': {'dx', 'dy', 'dz'}
    'n_points': the number of values in the resulting arrays

    The keys in the resulting dictionary represent the names of all of the load combos in the model. The
    values are (n_points, 2)-shaped arrays that contain an x-array (of beam locations) and a y-array (of results).
    """

    solved_beam_model.analyze()
    all_combos = {}
    member_name = list(solved_beam_model.Members.keys())[0]

    for combo_name in list(solved_beam_model.LoadCombos.keys())[1:]: #The first combination is the default 'Combo 1' so I exclude it:
        
        if result_type == 'shear':
            result = solved_beam_model.Members[member_name].shear_array(direction, n_points, combo_name)
            #print(result) You can see it returns list[list[float], list[float]] as mentioned above.
            result = all_combos[combo_name] = result
        elif result_type == 'moment':
            result = solved_beam_model.Members[member_name].moment_array(direction, n_points, combo_name)
            all_combos[combo_name] = result
        elif result_type == 'axial':
            result = solved_beam_model.Members[member_name].axial_array(n_points, combo_name)
            all_combos[combo_name] = result
        elif result_type == 'torque':
            result = solved_beam_model.Members[member_name].torque_array(n_points, combo_name)
            all_combos[combo_name] = result
        elif result_type == 'deflection':
            result = solved_beam_model.Members[member_name].deflection_array(direction, n_points, combo_name)
            all_combos[combo_name] = result

    return all_combos






#WORKBOOK04

def read_beam_file(filename: str) -> str:
    """
    Returns data contained in the file, 'filename' as a list of lists.
    It is assumed that the data in the file is "csv-ish", meaning with 
    comma-separated values.
    """
    return read_csv_file(filename)


def str_to_int(s: str) -> int|str:
    """
    Returns an integer. Converts 's' into an integer if possible. If not possible, keeps the string as it is.
    """
    try:
        s = int(s)
    except ValueError:
        s = s
    return s



def str_to_float(s: str) -> float|str:
    """
    Returns an float. Converts 's' into an float if possible. If not possible, keeps the string as it is.
    """
    try:
        s = float(s)
    except ValueError:
        s = s
    return s




def parse_supports(support_list: list[str]) -> dict[float, str]:

    """
    Returns a dictionary representing the data in 'supports' separated
    out into a dictionary with support locations as keys and support types
    as values. 

    Assumes 'support_list' is in a format that looks like this:
    ['support_loc:support_type', 'support_loc:support_type', etc...]
    e.g. ['1000:P', '3800:R', '6000:R']
    Where the valid support types are one of: P (pinned), F (fixed), or R (roller)

    # Example input
    ['1000:P', '3800:R', '4800:F', '8000:R']
    
    # Example output
    {1000: 'P', 3800: 'R', 4800: 'F', 8000: 'R'}
    
    """
    
    parsed = {}
    for support in support_list:
        support_loc, support_type = support.split(":")
        parsed.update({str_to_float(support_loc): support_type})
    return parsed


def parse_loads(loads_data: list[list])-> list[dict]:

    """
    Returns the loads in loads_data to a stctured list of dicts:

    # Example input (list[list[str|float])
    [
        ['POINT:Fy', -10000.0, 4800.0, 'case:Live'],
        ['DIST:Fy', 30.0, 30.0, 0.0, 4800.0, 'case:Dead']
    ]
    
    # Example output (list[dict])
    [
        {
            "Type": "Point", 
            "Direction": "Fy", 
            "Magnitude": -10000.0, 
            "Location": 4800.0, 
            "Case": "Live"
        },
        {
            "Type": "Dist", 
            "Direction": "Fy",
            "Start Magnitude": 30.0,
            "End Magnitude": 30.0,
            "Start Location": 0.0,
            "End Location": 4800.0,
            "Case": "Dead"
        }
    ]
    
    """
    
    parsed = []
    
    for load in loads_data:
        load_type, load_dir = load[0].split(":")
        load_case = load[-1].split(":")[1]
        if load_type == "POINT":
            magnitude = load[1]
            location = load[2]
    
            parsed.append(
                {
                    "Type": load_type.title(),
                    "Direction": load_dir.title(),
                    "Magnitude": magnitude,
                    "Location": location,
                    "Case": load_case
                }
            )
    
        elif load_type == "DIST":
            start_magnitude = load[1]
            end_magnitude = load[2]
            start_location = load[3]
            end_location = load[4]
    
            parsed.append(
                {
                    "Type": load_type.title(),
                    "Direction": load_dir,
                    "Start Magnitude": start_magnitude,
                    "End Magnitude": end_magnitude,
                    "Start Location": start_location,
                    "End Location": end_location,
                    "Case": load_case
                }
            )
            
    return parsed



def parse_beam_attributes(attribute_values: list[float]) -> dict[str, float]:
    
    """
    Returns a dictionary of beam attributes according to which attributes are present
    in 'beam_attributes' in the order according to the beam file format BEAM_FORMAT.md,
    Workbook_04 edition. The order of attributes are as follows: Length,E,Iz,[Iy,A,J,nu,rho]

    # Example input 1
    [20e3, 200e3, 6480e6, 390e6, 43900, 11900e3, 0.3]
    
    # Example input 2
    [4800, 24500, 1200000000, 10]
    
    # Example output 1
    {"L": 20e3, "E": 200e3, "Iz": 6480e6, "Iy": 390e6, "A": 43900, "J": 11900e3, "nu": 0.3, "rho": 1}
    
    # Example output 2
    {"L": 4800, "E": 24500, "Iz": 1200000000, "Iy": 10, "A": 1, "J": 1, "nu": 1, "rho": 1}

    """

    parsed = {}
           
    attribute_list = ["L", "E", "Iz", "Iy", "A", "J", "nu", "rho"]
    
    for idx, attributes in enumerate(attribute_list):
        try:
            parsed[attribute_list[idx]] = attribute_values[idx]
        except IndexError:
            parsed[attribute_list[idx]] = 1
    return parsed



def get_structured_beam_data(raw_data: list[list[str]]) -> dict:

    """
    The goal of this task is to create a dictionary with all of the beam data nicely parcelled out. In other words, the goal is to take the raw data, 
    which only has meaning because we happen to know the file format, and to put it in a structured form where it has explicit meaning. We will do this 
    by putting the data into a dictionary. Here is what the structured data would look like for the data in "beam_1.txt":

    In this modified function, we are using "parse" functions to make this function more robust.
    
    # Using the input generated from beams.read_beam_file('beam_1.txt')
    [['Balcony transfer'],
    ['4800', '24500', '1200000000', '1', '1'],
    ['1000:P', '3800:R'],
    ['POINT:Fy', '-10000', '4800', 'case:Live'],
    ['DIST:Fy', '30', '30', '0', '4800', 'case:Dead']]

    # Example output
    {'Name': 'Balcony transfer',
    'L': 4800.0,
    'E': 24500.0,
    'Iz': 1200000000.0,
    'Iy': 1.0,
    'A': 1.0,
    'J': 1.0,
    'nu': 1.0,
    'rho': 1.0,
    'Supports': {1000.0: 'P', 3800.0: 'R'},
    'Loads': [{'Type': 'Point',
    'Direction': 'Fy',
    'Magnitude': -10000.0,
    'Location': 4800.0,
    'Case': 'Live'},
    {'Type': 'Dist',
    'Direction': 'Fy',
    'Start Magnitude': 30.0,
    'End Magnitude': 30.0,
    'Start Location': 0.0,
    'End Location': 4800.0,
    'Case': 'Dead'}]}
    """
    
    beam_name= raw_data[0][0]
    numeric_beam_data = convert_to_numeric(raw_data[1:])
    beam_attributes = parse_beam_attributes(numeric_beam_data[0])
    support_attributes = parse_supports(numeric_beam_data[1])
    load_attributes = parse_loads(numeric_beam_data[2:])
    structured_data = {}
    structured_data['Name'] = beam_name
    structured_data = structured_data | beam_attributes
    structured_data['Supports'] = support_attributes
    structured_data['Loads'] = load_attributes
    
    return structured_data



def get_node_locations(support_node_data: float, beam_length: list[float]) -> dict[str, float]:

    """
    Returns a dict representing the node names and node coordinates required for
    a beam with support locations at 'support_locations' and a beam of length of 
    'beam_length'.

    Each node name and node location is unique. Nodes are numbered sequentially from
    left to right starting at "N0". Even though this N0 is not in the support location
    (meaning the beam does not start with a support). Also the beam does not end with a
    support neither. It means if there is no support at the end of the beam, it will
    create a node at the end according to the length of the beam. But it will not 
    accidentally duplicate a node if there is already a support at the end of the beam.


    # Example input 1
    beam_length = 10000.0
    supports = [1000.0, 4000.0, 8000.0]
    
    # Example input 2
    beam_length = 210.0
    supports = [0.0, 210.0]
    
    # Example output 1
    {"N0": 0.0, "N1": 1000.0, "N2": 4000.0, "N3": 8000.0, "N4": 10000.0}
    
    # Example output 2
    {"N0": 0.0, "N1": 210.0}

    """

    nodes_to_create = support_node_data[:]  #[:] is to create a shallow copy so that they are not in the same memory.
    
    if 0.0 not in support_node_data:
        nodes_to_create.append(0.0)
    if beam_length not in support_node_data:
        nodes_to_create.append(beam_length)
    
    nodes = {}
    
    nodes_to_create.sort()
    
    for idx, loc in enumerate(nodes_to_create):
        node_name = f"N{idx}"
        nodes[node_name] = loc
    
    return nodes




def build_beam(beam_data: dict) -> FEModel3D:
    """
    Returns a beam finite element model for the data in 'beam_data' which is assumed to represent
    a simply supported beam with a cantilever at one end with a uniform distributed load applied
    in the direction of gravity.
    """

    support_loc = []

    for loc, sup_type in beam_data["Supports"].items():
        support_loc.append(loc)

    beam_data["Nodes"] = get_node_locations(support_loc, beam_data["L"])  #returns 'nodes'
    
    model = FEModel3D()
    
    node_acc={}
    
    for node_name, node_loc_X in beam_data["Nodes"].items():
        node_acc.update({"name": node_name, "X": node_loc_X, "Y" : 0, "Z" : 0})
        model.add_node(**node_acc)

        if node_loc_X in support_loc:
            if beam_data["Supports"][node_loc_X] == "P":
                
                model.def_support(node_name, True, True, True, True, True, False)

            elif beam_data["Supports"][node_loc_X] == "R":

                model.def_support(node_name, False, True, False, False, False, False)

            elif beam_data["Supports"][node_loc_X] == "F":

                model.def_support(node_name, True, True, True, True, True, True)

    #Shear modulus:
    G = calc_shear_modulus(beam_data["E"], beam_data["nu"])

    #Add material to the model:
    model.add_material("MaterialS355 (sallaaa)", beam_data["E"], G, beam_data["nu"], beam_data["rho"])

    
    #Add member (keep in mind that node_name is keeping the last node name):
    model.add_member(
        beam_data["Name"],
        "N0",
        node_name,
        "MaterialS355 (sallaaa)",
        Iy = beam_data["Iy"],
        Iz = beam_data["Iz"],
        J = beam_data["J"],
        A = beam_data["A"],
        )

    for load in beam_data["Loads"]:
        if load["Type"] == "Point":
            model.add_member_pt_load(
                beam_data["Name"],
                load["Direction"],
                load["Magnitude"],
                load["Location"],
                load["Case"],
            )
                
        elif load["Type"] == "Dist":
            model.add_member_dist_load(
                beam_data["Name"],
                load["Direction"],
                load["Start Magnitude"],
                load["End Magnitude"],
                load["Start Location"],
                load["End Location"],
                load["Case"],
            )
    
    model.analyze()
    #model.LoadCombos
    #Visualization.render_model(model, annotation_size=100, combo_name='Combo 1')
    #model.Members[beam_data["Name"]].plot_shear(Direction= "Fy", combo_name= "Combo 1", n_points=5000)
    #render_model(model, deformed_shape=True, combo_name="Combo 1", annotation_size=100)
    #model.Members[beam_data["Name"]].plot_deflection("dy", "Combo 1", 5000)
    return model




def load_beam_model(filename: str, load_combos: Optional[dict] = None) -> FEModel3D: 
    """
    Returns an FEModel3D beam model representing the beam described in 'filename'
    """
    beam_data_raw = read_beam_file(filename)
    #beam_data_sep = separate_data(beam_data_raw)
    beam_data_structured = get_structured_beam_data(beam_data_raw)
    beam_model = build_beam(beam_data_structured)
    if load_combos is not None:
        for combo_name, combo_factors in load_combos.items():
            beam_model.add_load_combo(combo_name, combo_factors)
    return beam_model



#WORKBOOK 03



def separate_data(data: list[str]) -> list[list[str]]:
    
    """
    It receives one parameter representing the file data, a list[str], and it returns a list[list[str]]. The functions purpose is to split up each individual line of data in the input so the output now looks like this (using the data in "beam_1.txt" as an example):

    # Input
    ['Roof beam',
    '4800, 19200, 1000000000',
    '0, 3000',
    '-100, 500, 4800',
    '-200, 3600, 4800']

    # Output
    [['Roof beam'],
    ['4800', '19200', '1000000000'],
    ['0', '3000'],
    ['-100', '500', '4800'],
    ['-200', '3600', '4800']]

    """
    
    line_data=[]
    for each_line in data:
        each_line = each_line.split(", ")
        line_data.append(each_line)
    return line_data



def convert_to_numeric(data: list[list[str]]) -> list[list[float]]:
    
    """
    
    takes a list[list[str]] and returns a list[list[float]] using the "transforming" recipe.
    
    # Input
    [
    ['4800', '19200', '1000000000'],
    ['0', '3000'],
    ['-100', '500', '4800'],
    ['-200', '3600', '4800']
    ]

    # Output
    [
    [4800.0, 19200.0, 1000000000.0],
    [0.0, 3000.0],
    [-100.0, 500.0, 4800.0],
    [-200.0, 3600.0, 4800.0]
    ]
    
    """
    
    line_data=[]
    for each_list in data:
        new_list = []
        for the_string in each_list:
            float_version = str_to_float(the_string)
            new_list.append(float_version)
        line_data.append(new_list)
    return line_data



# def get_structured_beam_data(raw_data: list[list[str]]) -> dict:            #NEW VERSION ON WB04

#     """
#     The goal of this task is to create a dictionary with all of the beam data nicely parcelled out. In other words, the goal is to take the raw data, which only has meaning because we happen to know the file format, and to put it in a structured form where it has explicit meaning. We will do this by putting the data into a dictionary. Here is what the structured data would look like for the data in "beam_1.txt":
    
#     # Input
#     [['Roof beam'],
#      ['4800', '19200', '1000000000'],
#      ['0', '3000'],
#      ['-100', '500', '4800'],
#      ['-200', '3600', '4800']]
    
#      # Output
#     {'Name': 'Roof beam',
#      'L': 4800.0,
#      'E': 19200.0,
#      'Iz': 1000000.0,
#      'Supports': [0.0, 3000.0],
#      'Loads': [[-100.0, 500.0, 4800.0], [-200.0, 3600.0, 4800.0]]}
#     """
    
#     beam_name= raw_data[0][0]
#     numeric_beam_data = convert_to_numeric(raw_data[1:])
#     L, E, Iz = numeric_beam_data[0]
#     Supports = numeric_beam_data[1]
#     Loads = numeric_beam_data[2:]
#     structured_data = {}
#     structured_data['Name'] = beam_name
#     structured_data['L'] = L
#     structured_data['E'] = E
#     structured_data['Iz'] = Iz
#     structured_data['Supports'] = Supports
#     structured_data['Loads'] = Loads
#     return structured_data



# def get_node_locations(support_node_data: dict[str, float]):     #NEW VERSION ON WB04

#     """
#     It will return a dict[str, float] meaning a dictionary with string keys and float values. The string keys will be the node names for our beam model 
#     (something like "N0" or "N1") and the values will be the position of the node on the x-axis (e.g. 0.0 or 122.5).
#     # Input
#     supports = [0.0, 3000.0, 4800.0]

#     # Output
#     {"N0": 0.0, "N1": 3000.0, "N2": 4800.0}
    
#     """
    
#     nodes={}
#     for idx, loc in enumerate(support_node_data):
#         node_name = f"N{idx}"
#         #nodes[node_name] = loc
#         nodes.update({node_name: loc})
#     return nodes




# def build_beam(beam_data: dict, A: float=1, J: float = 1, nu: float = 1, rho:float =1) -> FEModel3D:          #NEW VERSION ON WB04
#     """
#     Returns a beam finite element model for the data in 'beam_data' which is assumed to represent
#     a simply supported beam with a cantilever at one end with a uniform distributed load applied
#     in the direction of gravity.
#     """
    
#     beam_data['Nodes'] = get_node_locations(beam_data["Supports"])
    
#     model = FEModel3D()
    
#     node_acc={}
#     for node_name, support_loc in beam_data["Nodes"].items():
#         node_acc.update({"name": node_name, "X": support_loc, "Y": 0, "Z": 0})
#         model.add_node(**node_acc)
#         #All supports are rollers:
#         model.def_support(node_name, False, True, False, False, False, False)
#     #First support is pinned:
#     model.def_support("N0", True, True, True, True, True, False)

#     #Shear modulus:
#     G = calc_shear_modulus(beam_data["E"], nu)

#     #Add material to the model:
#     model.add_material("Beam material", beam_data["E"], G, nu, rho)

#     #Add member (keep in mind that node_name is keeping the last node name):
#     model.add_member(
#         beam_data["Name"],
#         "N0",
#         node_name,
#         "Beam material",
#         Iy = 1,
#         Iz = beam_data["Iz"],
#         J=J,
#         A = A,
#     )

#     for magnitude, load_start, load_end in beam_data["Loads"]:
#         model.add_member_dist_load(
#             beam_data["Name"],
#             "Fy",
#             magnitude,
#             magnitude,
#             load_start,
#             load_end,
#         )

#     model.analyze()

#     #model.Members[beam_data["Name"]].plot_shear(Direction= "Fy", combo_name= "Combo 1")
#     #model.Members[beam_data["Name"]].min_deflection("dy", "Combo 1")
#     #model.plot_deflection("dy", "Combo 1", 100)
#     return model



# def load_beam_model(filename: str) -> FEModel3D:            #NEWER VERSION ON WORKBOOK04. (separate_data had to removed, don't know why)
#     """
#     Returns an FEModel3D beam model representing the beam described in 'filename'
#     """
#     beam_data_raw = read_beam_file(filename)
#     beam_data_sep = separate_data(beam_data_raw)
#     beam_data_structured = get_structured_beam_data(beam_data_sep)
#     beam_model = build_beam(beam_data_structured)
#     return beam_model









#WORKBOOK 02






# def read_beam_file(filename: str) -> list:    #WB03 version
#     """
#     returns a long string of text representing the text data in the file.
#     """
#     file_data = []
#     with open(filename, "r") as file:
#         for line in file.readlines():
#             line = line.strip("\n")
#             file_data.append(line)
#     return file_data


def separate_lines(filename) -> list[str]:
    """
    return a list[str] where each item in the list will represent one line in the original file data.
     
    for example:
    def test_separate_lines():
    example_1_data = "cat, bat, hat\\ntroll, scroll, mole"
    assert separate_lines(example_1_data) == ["cat, bat, hat", "troll, scroll, mole"]
    # etc.
    
    
    """
    separated_filename = filename.split("\n")
    return separated_filename


def extract_data(data: str, index: int) -> list[str]:
    """
    The function returns the data list item corresponding to the index separated out as their own list items
    """
    return data[index].split(", ")



def get_spans(beam_length: float, cant_sup_loc: float) -> tuple[float,float]:
    """
    b is the distance between the first support to the cant. support.
    a is the distance from the cant. support to the end of the beam.
    """
    b = cant_sup_loc
    a = beam_length - b
    return b, a



#def build_beam(beam_data: list[str]) -> FEModel3D:                                                 #WB02 version
    """
    Returns a beam finite element model for the data in 'beam_data' which is assumed to represent
    a simply supported beam with a cantilever at one end with a uniform distributed load applied
    in the direction of gravity.
    """
    LEI = extract_data(beam_data, 0)
    L = str_to_float(LEI[0])
    E = str_to_float(LEI[1])
    I = str_to_float(LEI[2])
    supports_1_and_2 = extract_data(beam_data, 1)
    span_list = get_spans(L,str_to_float(supports_1_and_2[1]))
    
    b = span_list[0]
    a= span_list[1]
    w = str_to_float(extract_data(beam_data, 2)[0])
    
    model = fe_model_ss_cant(w,b,a,E,I)
    
    model.analyze()
    #model.Members["M0"].plot_shear(Direction= "Fy", combo_name= "Combo 1", n_points=100)
    #model.Members['M0'].max_deflection("dy","Combo 1")
    return model

    


# def load_beam_model(filename: str) -> FEModel3D:                                #WB02 version
#     """
#     Takes the beam file filename as input and will return to you an FEModel3D ready for analysis!
#     """
#     beam_file = read_beam_file(filename)
#     separated_data = separate_lines(beam_file) #now the separate lines removed and it became 1 line, with different items.
#     model_1 = build_beam(separated_data)
#     model_1.analyze()
#     #r1_combos = model_1.Nodes['N1'].RxnFY
#     #r2_combos = model_1.Nodes['N0'].RxnFY
#     #print(r1_combos, r2_combos)
#     return model_1

















































#WORKBOOK 1

# def str_to_int(s: str) -> int:
#     """
#     Returns an integer. Converts 's' into an integer if possible.
#     """
#     return int(s)



# def str_to_float(s: str) -> int:
#     """
#     Returns an float. Converts 's' into an float if possible.
#     """
#     return float(s)



def calc_shear_modulus(E: float, nu: float) -> float:
    
    """
    Returns the shear modulus.
    """
    
    shear_modulus = E/(2*(1+nu))
    return shear_modulus



def euler_buckling_load(l:float, E:float, I:float, k:float) -> float:
    """
    Returns the Euler buckling load for the parameters provided.
    """
    P_cr = pi**2 * E * I / (k * l)**2
    return P_cr



def beam_reactions_ss_cant(w: float, b:float, a:float) -> tuple[float,float]:
    
    """
    Returns 2 floats representing the reaction forces r1 and r2.
    
                w
    ||||||||||||||||||||||||||||||    
    ------------------------------
    ^                  ^
    R2                 R1
    ---------b---------|----a-----
    """ 

    r1 = -(w * (a+b)**2 / (2*b))
    r2 = -(w / (2*b) * (b**2 - a**2))
    return r1, r2



def fe_model_ss_cant(
    w:float,
    b: float,
    a:float,
    E:float = 1.0,
    I: float = 1.0,
    A: float = 1.0,
    J: float = 1.0,
    nu: float = 1.0,
    rho: float = 1.0,
) -> FEModel3D:
    
    """
    Returns 2 floats representing the reaction forces r1 and r2, this time with FEA method.
    
                w
    ||||||||||||||||||||||||||||||    
    ------------------------------
    ^                  ^
    R2                 R1
    ---------b---------|----a-----

    J: Polar moment of inertia
    nu: Poison's ratio
    rho: Density
    """
    model=FEModel3D()
    model.add_node("N0", 0, 0, 0)
    model.add_node("N1", b, 0, 0)
    model.add_node("N2", b+a, 0, 0)

    model.def_support("N0", True, True, True, True, True, False)
    model.def_support("N1", False, True, False, False, False, False)

    G = calc_shear_modulus(E, nu)
    
    model.add_material("default", E=E, G=G, nu=nu, rho=rho)

    model.add_member("M0", "N0", "N2", "default", Iy=I, Iz=I, J=J, A=A)
    
    model.add_member_dist_load("M0","Fy", w1=w, w2=w, x1=0, x2=b+a)

    model.add_load_combo("Combo 1", {"Case 1": 1.0})
    
    return model