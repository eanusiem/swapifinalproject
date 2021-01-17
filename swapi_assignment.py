import json
import requests 
   
ENDPOINT = 'https://swapi.co/api'

PEOPLE_KEYS = ('url', 'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year',
    'gender', 'homeworld', 'species' 
)

PLANET_KEYS = ('url', 'name', 'rotation_period', 'orbital_period', 'diameter', 'climate', 'gravity', 
    'terrain', 'surface_water', 'population'
)

PLANETHOTH_KEYS = ('url', 'name', 'system_position', 'natural_satellites', 'rotation_period', 'orbital_period',
    'diameter', 'climate', 'gravity', 'terrain', 'surface_water', 'population', 'indigenous_life_forms'
)

STARSHIP_KEYS = ('url', 'starship_class', 'name', 'model', 'manufacturer', 'length', 'width', 'max_atmosphering_speed',
    'hyperdrive_rating', 'MGLT', 'crew', 'passengers', 'cargo_capacity', 'consumables', 'armament'
)

SPECIES_KEYS = ('url', 'name', 'classification', 'designation', 'average_height', 'skin_colors', 'hair_colors', 
    'eye_colors', 'average_lifespan', 'language'
)

VEHICLE_KEYS = ('url', 'vehicle_class', 'name', 'model', 'manufacturer', 'length', 'max_atmosphering_speed',
    'crew', 'passengers', 'cargo_capacity', 'consumables', 'armament'
)
 
def read_json(filepath = 'swapi_planets-v1p0.json'):  

    """"
    Given a valid filepath, reads a JSON document and returns a dictionary.

    Parameters:
        filepath (str): path to file.

    Returns:
        dict: decoded JSON document expressed as a dictionary.
    """

    with open(filepath, 'r', encoding='utf-8') as file_object:
        data = json.load(file_object)

    return data  
 
def get_swapi_resource(url, params=None): 
    
    """
    Issues an HTTP GET request to return a representation of a resource. If no category is
    provided, the root resource will be returned. If a match is achieved the JSON object 
    that is returned will include a list property named 'results' that contains the
    resource(s) matched by the search query.

    Parameters:
        url (str): a url that specifies the resource.
        params (dict): optional dictionary of querystring arguments.

    Returns:
        dict: decoded JSON document expressed as dictionary.
    """

    if params:
        response = requests.get(url, params=params).json()
    else:
        response = requests.get(url).json()

    return response

def combine_data(default_data, override_data): 

    """ 
    Creates a shallow copy of the default dictionary and then updates the new
    copy with override data. Override values will replace default values when if
    the keys match.

    Parameters:
        default_data (dict): entity data that provides the default representation of the object.
        override_data (dict): entity data intended to override matching default values.
 
    Returns: 
        dict: updated dictionary that contains override values.
    """  
  
    combine_data = default_data.copy()  
    combine_data.update(override_data) 
    return combine_data 

def filter_data(data, filter_keys): 

    """
    Returns a new dictionary based containing a filtered subset of key-value pairs
    sourced from a dictionary provided by the caller.

    Parameters:
        data (dict): source entity.
        filter_keys (tuple): sequence of keys used to select a subset of key-value pairs.

    Returns:
        dict: a new entity containing a subset of the source entity's key-value pairs.
    """

    record = {}
    for key in filter_keys:
        if key in data.keys():
            record[key] = data[key]
    return record 

def is_unknown(value):

    """
    This function applies a case-insensitive truth value test for string values that equal unknown or n/a. 
    
    Parameters: 
    (str): single parameter value. 
    
    Returns: 
    True if a match is obtained.
    """ 

    value = value.lower().strip() 

    if value == "unknown":
        return True
    elif value == "n/a": 
        return True 
    else: 
        return False

def convert_string_to_float(value):

    """
    This function attempts to convert a string to a floating point value. 

    Parameters: 
    (str): single parameter value.

    Returns: 
    True for boolean values, faux string boolean values, "NaN, and exponential notation.
    """

    try:
        return float(value)
    except ValueError:
        return value
 
def convert_string_to_int(value):

    """
    This function attempts to convert a string to an int. 

    Parameters: 
    (str): single parameter value.

    Returns: 
    True for boolean values, faux string boolean values, NaN, and exponential notation.
    """

    try:
        return int(value)
    except ValueError:
        return value

def convert_string_to_list(value, delimiter=','): 
    
    """"
    This function converts a string of delimited text values to a list. 

    Parameters: 
    (str): single parameter value.
 
    Returns:  
    Resulting list to the caller. 
    """ 

    new_list = [] 
    for people in value.split(delimiter):
        new_list.append(people)
    
    return new_list
  
def clean_data(entity):
 
    """
    This function converts dictionary string values to more appropriate types.
    The function evaluates each key-value pair encountered with if-elif-else conditional statements, 
    membership operators, and calls to other functions that perform the actual type conversions to accomplish this task. 

    Parameters:  
    entity(dict): source entity.

    Returns: 
    dict: 'cleaned' values to the caller. 
    """

    float_props = ('gravity', 'length', 'hyperdrive_rating')
    int_props = ('rotation_period', 'orbital_period', 'diameter', 'surface_water', 'population',
             'height', 'mass', 'average_height', 'average_lifespan', 'max_atmosphering_speed',
             'MGLT', 'crew', 'passengers', 'cargo_capacity')
    list_props = ('hair_color', 'skin_color', 'climate', 'terrain', 'hair_colors', 'skin_colors', 'eye_colors')

    cleaned_dictionary = {}

    for key,value in entity.items():
        if type(value) == str and is_unknown(value):
            cleaned_dictionary[key] = None 
        elif key in float_props: 
            if key == 'gravity':
                value = value.replace('standard','').strip()
            cleaned_dictionary[key] = convert_string_to_float(value)
        elif key in int_props:
            cleaned_dictionary[key] = convert_string_to_int(value)
        elif key in list_props:
            value = value.strip() 
            cleaned_dictionary[key] = convert_string_to_list(value, delimiter=', ')
        elif key == 'homeworld': 
                homeworld = get_swapi_resource(value)
                new_homeworld = filter_data(homeworld, PLANET_KEYS)
                cleaned_dictionary[key] = clean_data(new_homeworld)
        elif key == 'species': 
                species = get_swapi_resource(value[0])
                new_species = filter_data(species, SPECIES_KEYS)
                cleaned_dictionary[key] = [clean_data(new_species)]
        else:
            cleaned_dictionary[key] = value
 
    return cleaned_dictionary


def assign_crew(starship, crew):
    
    """
    This function assigns crew members to a starship.

    Parameters: 
    starship (dict): source entity.
    crew (dict): source entity. 

    Returns: 
    updated starship with one or more new crew member key-value pairs added to the caller.
    """

    for key,value in crew.items(): 
        starship[key] = value

    return starship

def write_json(filepath, data): 

    """
    Given a valid filepath, write data to a JSON file.

    Parameters:
        filepath (str): the path to the file.
        data (dict): the data to be encoded as JSON and written to the file.

    Returns:
        None 
    """

    with open(filepath, 'w', encoding='utf-8') as file_obj:
        json.dump(data, file_obj, ensure_ascii=False, indent=2)

def main():
 
    """
    Entry point. This program will interact with local file assets and the Star Wars
    API to create two data files required by Rebel Alliance Intelligence.

    - A JSON file comprising a list of likely uninhabited planets where a new rebel base could be
      situated if Imperial forces discover the location of Echo Base.

    - A JSON file of Echo Base information including an evacuation plan of base personnel
      along with passenger assignments for Princess Leia, the communications droid C-3PO aboard
      the transport Bright Hope escorted by two X-wing starfighters piloted by Luke Skywalker
      (with astromech droid R2-D2) and Wedge Antilles (with astromech droid R5-D4).
  
    Parameters: 
        None    

    Returns:   
        None    
    """    
    uninhabited_planets = []
    planets_data = read_json('swapi_planets-v1p0.json')
    for planet in planets_data:
        if is_unknown(planet['population']):
            ideal_planet = filter_data(planet, PLANET_KEYS)
            ideal_planet = clean_data(ideal_planet)
            uninhabited_planets.append(ideal_planet)
    write_json('swapi_planets_uninhabited-v1p1.json', uninhabited_planets)
    
    echo_base = read_json('swapi_echo_base-v1p0.json')
    swapi_hoth = get_swapi_resource('https://swapi.co/api/planets/4/')
    echo_base_hoth = echo_base['location']['planet']
    hoth = combine_data(echo_base_hoth, swapi_hoth)
    hoth = filter_data(hoth, PLANETHOTH_KEYS)
    hoth = clean_data(hoth) 
    echo_base['location']['planet'] = hoth
    
    echo_base_commander = echo_base['garrison']['commander']
    echo_base_commander = clean_data(echo_base_commander)
    echo_base['garrison']['commander'] = echo_base_commander

    echo_base_smuggler = echo_base['visiting_starships']['freighters'][1]['pilot']
    echo_base_smuggler = clean_data(echo_base_smuggler)
    echo_base['visiting_starships']['freighters'][1]['pilot'] = echo_base_smuggler

    swapi_vehicles_url = f"{ENDPOINT}/vehicles/"
    swapi_snowspeeder = get_swapi_resource(swapi_vehicles_url, {'search': 'snowspeeder'})['results'][0]
    echo_base_snowspeeder = echo_base['vehicle_assets']['snowspeeders'][0]['type']
    snowspeeder = combine_data(echo_base_snowspeeder, swapi_snowspeeder)
    snowspeeder = filter_data(snowspeeder, VEHICLE_KEYS)
    snowspeeder = clean_data(snowspeeder)
    echo_base['vehicle_assets']['snowspeeders'][0]['type'] = snowspeeder

    swapi_starships_url = f"{ENDPOINT}/starships/"
    swapi_t65 = get_swapi_resource(swapi_starships_url, {'search': 't-65 x-wing'})['results'][0]
    echo_base_t65 = echo_base['starship_assets']['starfighters'][0]['type']
    tf_65 = combine_data(echo_base_t65, swapi_t65)
    tf_65 = filter_data(tf_65, STARSHIP_KEYS)
    tf_65 = clean_data(tf_65)
    echo_base['starship_assets']['starfighters'][0]['type'] = tf_65

    swapi_gr75 = get_swapi_resource(swapi_starships_url, {'search': 'gr-75 medium transport'})['results'][0]
    echo_base_gr75 = echo_base['starship_assets']['transports'][0]['type']
    medium_gr75 = combine_data(echo_base_gr75, swapi_gr75)
    medium_gr75 = filter_data(medium_gr75, STARSHIP_KEYS)
    medium_gr75 = clean_data(medium_gr75)
    echo_base['starship_assets']['transports'][0]['type'] = medium_gr75

    swapi_millennium_falcon = get_swapi_resource(swapi_starships_url, {'search': 'millennium falcon'})['results'][0]
    echo_base_millennium_falcon = echo_base['visiting_starships']['freighters'][0]
    m_falcon = combine_data(echo_base_millennium_falcon, swapi_millennium_falcon)
    m_falcon = filter_data(m_falcon, STARSHIP_KEYS)
    m_falcon = clean_data(m_falcon)

    swapi_people_url = f"{ENDPOINT}/people/"
    han = get_swapi_resource(swapi_people_url, {'search': 'han solo'})['results'][0]
    han = filter_data(han, PEOPLE_KEYS)
    han = clean_data(han)
    chewie = get_swapi_resource(swapi_people_url, {'search': 'chewbacca'})['results'][0]
    chewie = filter_data(chewie, PEOPLE_KEYS)
    chewie = clean_data(chewie)
    m_falcon = assign_crew(m_falcon, {'pilot': han, 'copilot': chewie})
    echo_base['visiting_starships']['freighters'][0] = m_falcon


    evacuation_plan = echo_base['evacuation_plan']
    max_base_personnel = 0
    millennium_personel = echo_base['garrison']['personnel']
    for value in millennium_personel.values():
        max_base_personnel += value
    evacuation_plan['max_base_personnel'] = max_base_personnel
    max_available_transports = echo_base['starship_assets']['transports'][0]['num_available']
    evacuation_plan['max_available_transports'] = max_available_transports
    passenger_overload_multiplier = evacuation_plan['passenger_overload_multiplier']
    standard_passenger_carrying_capacity = echo_base['starship_assets']['transports'][0]['type']['passengers']
    evacuation_plan['max_passenger_overload_capacity'] = max_available_transports * passenger_overload_multiplier * standard_passenger_carrying_capacity

    evac_transport = medium_gr75.copy()
    evac_transport['name'] = 'Bright Hope'
    evac_transport['passenger_manifest'] = []
    princess_leia = get_swapi_resource(swapi_people_url, {'search': 'leia organa'})['results'][0]
    princess_leia = filter_data(princess_leia, PEOPLE_KEYS)
    princess_leia = clean_data(princess_leia)
    c3po_droid = get_swapi_resource(swapi_people_url, {'search': 'C-3PO'})['results'][0]
    c3po_droid = filter_data(c3po_droid, PEOPLE_KEYS)
    c3po_droid = clean_data(c3po_droid)
    evac_transport['passenger_manifest'] = [princess_leia, c3po_droid]

    evac_transport['escorts'] = []
    luke_xwing = tf_65.copy()
    wedge_xwing = tf_65.copy()
    luke = get_swapi_resource(swapi_people_url, {'search': 'luke skywalker'})['results'][0]
    luke = filter_data(luke, PEOPLE_KEYS) 
    luke = clean_data(luke)
    r2_d2 = get_swapi_resource(swapi_people_url, {'search': 'r2-d2'})['results'][0]
    r2_d2 = filter_data(r2_d2, PEOPLE_KEYS)
    r2_d2 = clean_data(r2_d2)
    luke_xwing = assign_crew(luke_xwing, {'pilot': luke, 'astromech_droid': r2_d2})
    evac_transport['escorts'].append(luke_xwing)

    wedge_antilles = get_swapi_resource(swapi_people_url, {'search': 'wedge antilles'})['results'][0]
    wedge_antilles = filter_data(wedge_antilles, PEOPLE_KEYS)
    wedge_antilles = clean_data(wedge_antilles)
    r5_d4 = get_swapi_resource(swapi_people_url, {'search': 'r5-d4'})['results'][0]
    r5_d4 = filter_data(r5_d4, PEOPLE_KEYS)
    r5_d4 = clean_data(r5_d4)
    wedge_xwing = assign_crew(wedge_xwing, {'pilot': wedge_antilles, 'astromech_droid': r5_d4})
    evac_transport['escorts'].append(wedge_xwing)

    evacuation_plan['transport_assignments'] = [evac_transport]
    echo_base['evacuation_plan'] = evacuation_plan
    write_json('swapi_echo_base-v1p1.json', echo_base)

if __name__ == '__main__':
    main()
