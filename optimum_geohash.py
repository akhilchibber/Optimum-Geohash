'''
THE GOAL OF THIS PYTHON SCRIPT IS TO FIND THE SMALLEST POSSIBLE SINGLE GEOHASH FOR ANY GIVEN GEOSPATIAL DATASET
'''





# Importing the essential Libraries
import fiona
import pygeohash as gh
import geopandas as gpd
from shapely.geometry import Polygon, shape
import string
from pyproj import CRS, Transformer
import math
import pandas as pd





'''
PART 1: THE GOAL OF THIS PART OF THE PYTHON SCRIPT IS TO FIND THE SMALLEST POSSIBLE SINGLE GEOHASH FOR ANY GIVEN 
GEOSPATIAL DATASET
'''

# FUNCTION 1: Identify the Extremes
def load_and_calculate_bounds(shapefile):
    with fiona.open(shapefile, 'r') as src:
        bounds = src.bounds  # get the bounding box (minx, miny, maxx, maxy)
    # print(f"Bounds of the dataset: {bounds}")
    return bounds

# FUNCTION 2: Calculate Initial Geohash
def calculate_initial_geohash(bounds, precision):
    center_lng = (bounds[0] + bounds[2]) / 2  # calculate center longitude
    center_lat = (bounds[1] + bounds[3]) / 2  # calculate center latitude
    geohash = gh.encode(center_lat, center_lng, precision = precision)  # calculate geohash of center point with initial precision
    return geohash

# FUNCTION 3: Test Coverage
def check_coverage(geohash, bounds):
    lat_centroid, lon_centroid, lat_err, lon_err = gh.decode_exactly(geohash)  # decode geohash to its bounding box
    gh_bounds = {
        's': lat_centroid - lat_err,
        'w': lon_centroid - lon_err,
        'n': lat_centroid + lat_err,
        'e': lon_centroid + lon_err
    }
    covers_area = gh_bounds['s'] <= bounds[1] and gh_bounds['w'] <= bounds[0] and gh_bounds['n'] >= bounds[3] and gh_bounds['e'] >= bounds[2]
    # print(f"Does geohash {geohash} cover the entire area? {'Yes' if covers_area else 'No'}")
    return covers_area


# FUNCTION 4: Function to identify a list of smallest possible geohash which covers a given study area
# This function is useful when we are not able to bound a study area in 1 geohash
def generate_geohashes(bounds):
    lat_step = (bounds[3] - bounds[1]) / 5.0
    lon_step = (bounds[2] - bounds[0]) / 5.0
    geohashes = set()  # change this to a set to ensure uniqueness

    for lat in range(0, 5):
        for lon in range(0, 5):
            min_lat = bounds[1] + lat * lat_step
            max_lat = min_lat + lat_step
            min_lon = bounds[0] + lon * lon_step
            max_lon = min_lon + lon_step
            center_lat = (min_lat + max_lat) / 2.0
            center_lon = (min_lon + max_lon) / 2.0
            geohash = gh.encode(center_lat, center_lon, precision = 1)
            geohashes.add(geohash)  # add the geohash to the set

    return list(geohashes)  # convert back to a list for the return





# FUNCTION 5: Identify the Extremes, Precision Adjustment and Iterative Refinement
# FUNCTION TO IDENTIFY THE SMALLEST POSSIBLE GEOHASH WHICH COVERS A GIVEN STUDY AREA
def find_smallest_geohash(shapefile, initial_precision = 10):
    bounds = load_and_calculate_bounds(shapefile)

    geohash = calculate_initial_geohash(bounds, initial_precision)  # Step 2: Calculate initial geohash
    covers_area = check_coverage(geohash, bounds)  # Step 3: Test coverage

    # if the geohash bounding box doesn't cover the entire city, decrement precision
    while not covers_area and initial_precision > 1:  # Step 4: Precision adjustment
        initial_precision -= 1  # Step 5: Iterative refinement
        geohash = calculate_initial_geohash(bounds, initial_precision)
        covers_area = check_coverage(geohash, bounds)

    # Ensure the final geohash covers the entire area
    if covers_area:
        smallest_geohash = geohash
    else:
        smallest_geohash = generate_geohashes(bounds)  # Here we generate all geohashes for the area

    # print("Smallest geohash that covers the entire area: ", smallest_geohash)
    return smallest_geohash

# END OF PART 1





'''
PART 2: THE GOAL OF THIS PART OF THE PYTHON SCRIPT IS TO CONVERT A GIVEN GEOHASH OR A LIST OF GEOHASH TO A 
POLYGON SHAPEFILE
'''
# FUNCTION 5: The goal of this function is to convert a geohash ot a list of geohash into polygon Shapefile
def geohashes_to_shapefile(geohashes):
    # List to store the polygons
    polys = []
    # List to store the corresponding geohashes
    geohash_list = []
    for geohash in geohashes:
        # decode the geohash
        lat_centroid, lon_centroid, lat_err, lon_err = gh.decode_exactly(geohash)

        # create the bounds of the geohash
        bounds = {
            's': lat_centroid - lat_err,
            'w': lon_centroid - lon_err,
            'n': lat_centroid + lat_err,
            'e': lon_centroid + lon_err
        }

        # create a Polygon using the bounds
        poly = Polygon([(bounds['w'], bounds['s']), (bounds['e'], bounds['s']), (bounds['e'], bounds['n']), (bounds['w'], bounds['n'])])
        polys.append(poly)
        geohash_list.append(geohash)

    # create a GeoDataFrame
    gdf = gpd.GeoDataFrame({'geometry': polys, 'geohash': geohash_list}, crs = "EPSG:4326")

    # save to a shapefile
    # gdf.to_file(output_filename)
    return gdf

# END OF PART 2





'''
PART 3: THE GOAL OF THIS PART OF THE PYTHON SCRIPT IS TO CONVERT A GIVEN GEOHASH INTO A LIST OF 32 SUB-CELL GEOHASH
'''
# FUNCTION 6: The goal of this Python function is to get 32 sub-cells for a given Geo-Hash ID
def get_subgeohashes(geohashes):
    # Define the possible characters used in geohashing
    geohash_characters = string.digits + string.ascii_lowercase
    geohash_characters = geohash_characters.replace('a', '')
    geohash_characters = geohash_characters.replace('i', '')
    geohash_characters = geohash_characters.replace('l', '')
    geohash_characters = geohash_characters.replace('o', '')

    # Initialize the dictionary for the results
    results = {}

    # Loop over each geohash
    for geohash in geohashes:
        # Get the subgeohashes
        subgeohashes = [geohash + char for char in geohash_characters]

        # Print and store the subgeohashes
        for subgeohash in subgeohashes:
            subgeohash
            # print(subgeohash)
        results[geohash] = subgeohashes

    return results

# END OF PART 3





# FUNCTION 7: The goal of this Python function is to come out with a set of geohash for covering a given study area
def unl_optimum_geohash(input_shapefile, output_shapefile, max_geohash = 10, max_coverage = 10):
    '''
    STEP 1: Calculating the smallest Geo-Hash which covers the entire Study Area and convert it into 32 Sub_Cells
    '''
    # Time to Run the Function and Find the Smallest possible Geohash
    smallest_geohash = find_smallest_geohash(input_shapefile)

    # Calling the function "get_subgeohashes"
    a = get_subgeohashes(smallest_geohash)

    # Identify the Values of Geo-Hash from keys
    a1 = list(a.values())

    # Print the Geo-Hash of Sub-Cells
    print(a1)

    # Flatten the list of lists into a single list
    flat_list_0 = [item for sublist in a1 for item in sublist]

    # Convert the Geo-Hash to Shapefile
    b = geohashes_to_shapefile(flat_list_0)





    '''
    STEP 2: FILTER OUT THE GEOHASH POLYGON FEATURES WHICH INTERSECTS WITH THE STUDY AREA CONCAVE HULL
    '''
    # Load the shapefiles
    study_area = gpd.read_file(input_shapefile)

    # Assuming that `study_area` is your GeoDataFrame
    study_area = study_area.to_crs("EPSG:4326")  # EPSG:4326 is for WGS 84 (world geodetic system)

    # Perform the spatial join operation
    intersect_polygons = gpd.sjoin(b, study_area, predicate = 'intersects', how = 'inner')

    '''
    TIME FOR OUTPUT: POSSIBLE GEOHASH OUTPUT 1
    '''
    # Append the retained geohashes to the subdivided ones
    final_geohashes_0 = intersect_polygons





    '''
    STEP 3: IDENTIFY THE PERCENTAGE (IN %) OF GEOHASH WHICH IS COVERED BY STUDY AREA
    '''
    intersect_polygons['COVERAGE'] = 0

    # Loop through each geohash polygon and calculate coverage
    for i, row in intersect_polygons.iterrows():
        # Calculate the intersection with the study area
        intersect = gpd.overlay(study_area, gpd.GeoDataFrame([row]), how = 'intersection')

        # Calculate the area of the intersection and the geohash
        intersect_area = intersect['geometry'].area.sum()
        geohash_area = row['geometry'].area

        # Calculate the coverage and save it to the geohash_polygons dataframe
        intersect_polygons.at[i, 'COVERAGE'] = (intersect_area / geohash_area) * 100





    '''
    STEP 4: IF STUDY AREA COVERAGE INSIDE A GEO-HASH IS LESS THAN OR EQUAL TO 10 % DIVIDE THE GEOHASH INTO SUB-CELLS
    '''
    # Load the shapefile
    geohashes = intersect_polygons

    # Filter the geohashes where coverage <= 10 %
    filtered_geohashes = geohashes[geohashes['COVERAGE'] <= max_coverage]['geohash'].tolist()

    # Filter the geohashes where coverage > 10 %
    retained_geohashes = geohashes[geohashes['COVERAGE'] > max_coverage]

    # Run the function on the filtered geohashes
    c = get_subgeohashes(filtered_geohashes)

    # Identify the Values of Geo-Hash from keys
    d = list(c.values())

    # Print the Geo-Hash of Sub-Cells
    print(d)

    # Flatten the list of lists into a single list
    flat_list_1 = [item for sublist in d for item in sublist]

    # Convert the Geo-Hash to Shapefile
    e = geohashes_to_shapefile(flat_list_1)





    '''
    STEP 2 AGAIN: FILTER OUT ONLY THOSE GEOHASH POLYGON FEATURES WHICH INTERSECTS WITH THE STUDY AREA CONCAVE HULL
    '''
    # Perform the spatial join operation
    intersect_polygons_2 = gpd.sjoin(e, study_area, predicate = 'intersects', how = 'inner')

    '''
    TIME FOR OUTPUT: POSSIBLE GEOHASH OUTPUT 1
    '''
    # Append the retained Geo-Hash to the subdivided ones
    final_geohashes_1 = pd.concat([retained_geohashes, intersect_polygons_2])





    '''
    STEP 3 AGAIN: IDENTIFY THE PERCENTAGE (IN %) OF GEOHASH WHICH IS COVERED BY STUDY AREA
    '''
    # Initialize a column for coverage
    intersect_polygons_2['COVERAGE'] = 0

    # Loop through each geohash polygon and calculate coverage
    for i, row in intersect_polygons_2.iterrows():
        # Calculate the intersection with the study area
        intersect = gpd.overlay(study_area, gpd.GeoDataFrame([row]), how = 'intersection')

        # Calculate the area of the intersection and the geohash
        intersect_area = intersect['geometry'].area.sum()
        geohash_area = row['geometry'].area

        # Calculate the coverage and save it to the geohash_polygons dataframe
        intersect_polygons_2.at[i, 'COVERAGE'] = (intersect_area / geohash_area) * 100





    '''
    STEP 4 AGAIN: IF STUDY AREA COVERAGE INSIDE A GEOHASH IS LESS THAN OR EQUAL TO 10% DIVIDE THE GEOHASH INTO SUB-CELLS
    '''
    # Load the shapefile
    geohashes_2 = intersect_polygons_2

    # Filter the geohashes where coverage <= 10 %
    filtered_geohashes_2 = geohashes_2[geohashes_2['COVERAGE'] <= max_coverage]['geohash'].tolist()

    # Filter the geohashes where coverage > 10 %
    retained_geohashes_2 = geohashes_2[geohashes_2['COVERAGE'] > max_coverage]

    # Run the function on the filtered geohashes
    f = get_subgeohashes(filtered_geohashes_2)

    # Identify the Values of Geo-Hash from keys
    g = list(f.values())

    # Print the Geo-Hash of Sub-Cells
    print(g)

    # Flatten the list of lists into a single list
    flat_list_2 = [item for sublist in g for item in sublist]

    # Convert the Geo-Hash to Shapefile
    h = geohashes_to_shapefile(flat_list_2)





    '''
    STEP 2 AGAIN: FILTER OUT ONLY THOSE GEOHASH POLYGON FEATURES WHICH INTERSECTS WITH THE STUDY AREA CONCAVE HULL
    '''
    # Perform the spatial join operation
    intersect_polygons_3 = gpd.sjoin(h, study_area, predicate = 'intersects', how = 'inner')

    '''
     TIME FOR OUTPUT: POSSIBLE GEOHASH OUTPUT 2
    '''
    # Append the retained Geo-Hash to the subdivided ones
    final_geohashes_2 = pd.concat([retained_geohashes, retained_geohashes_2])
    final_geohashes_3 = pd.concat([final_geohashes_2, intersect_polygons_3])





    '''
    STEP 3 AGAIN: IDENTIFY THE PERCENTAGE (IN %) OF GEOHASH WHICH IS COVERED BY STUDY AREA
    '''
    # Initialize a column for coverage
    intersect_polygons_3['COVERAGE'] = 0

    # Loop through each geohash polygon and calculate coverage
    for i, row in intersect_polygons_3.iterrows():
        # Calculate the intersection with the study area
        intersect = gpd.overlay(study_area, gpd.GeoDataFrame([row]), how = 'intersection')

        # Calculate the area of the intersection and the geohash
        intersect_area = intersect['geometry'].area.sum()
        geohash_area = row['geometry'].area

        # Calculate the coverage and save it to the geohash_polygons dataframe
        intersect_polygons_3.at[i, 'COVERAGE'] = (intersect_area / geohash_area) * 100





    '''
    STEP 4 AGAIN: IF STUDY AREA COVERAGE INSIDE A GEOHASH IS LESS THAN OR EQUAL TO 10% DIVIDE THE GEOHASH INTO SUB-CELLS
    '''
    # Load the shapefile
    geohashes_3 = intersect_polygons_3

    # Filter the geohashes where coverage <= 10 %
    filtered_geohashes_3 = geohashes_3[geohashes_3['COVERAGE'] <= max_coverage]['geohash'].tolist()

    # Filter the geohashes where coverage > 10 %
    retained_geohashes_3 = geohashes_3[geohashes_3['COVERAGE'] > max_coverage]

    # Run the function on the filtered geohashes
    i = get_subgeohashes(filtered_geohashes_3)

    # Identify the Values of Geo-Hash from keys
    j = list(i.values())

    # Print the Geo-Hash of Sub-Cells
    print(j)

    # Flatten the list of lists into a single list
    flat_list_3 = [item for sublist in j for item in sublist]

    # Convert the Geo-Hash to Shapefile
    k = geohashes_to_shapefile(flat_list_3)





    '''
    STEP 2 AGAIN: FILTER OUT ONLY THOSE GEOHASH POLYGON FEATURES WHICH INTERSECTS WITH THE STUDY AREA CONCAVE HULL
    '''
    # Perform the spatial join operation
    intersect_polygons_4 = gpd.sjoin(k, study_area, predicate = 'intersects', how = 'inner')

    '''
     TIME FOR OUTPUT: POSSIBLE GEOHASH OUTPUT 3
    '''
    # Append the retained geohashes to the subdivided ones
    final_geohashes_4 = pd.concat([retained_geohashes, retained_geohashes_2])
    final_geohashes_5 = pd.concat([final_geohashes_4, retained_geohashes_3])
    final_geohashes_6 = pd.concat([final_geohashes_5, intersect_polygons_4])





    '''
    STEP 3 AGAIN: IDENTIFY THE PERCENTAGE (IN %) OF GEOHASH WHICH IS COVERED BY STUDY AREA
    '''
    # Initialize a column for coverage
    intersect_polygons_4['COVERAGE'] = 0

    # Loop through each geohash polygon and calculate coverage
    for i, row in intersect_polygons_4.iterrows():
        # Calculate the intersection with the study area
        intersect = gpd.overlay(study_area, gpd.GeoDataFrame([row]), how='intersection')

        # Calculate the area of the intersection and the geohash
        intersect_area = intersect['geometry'].area.sum()
        geohash_area = row['geometry'].area

        # Calculate the coverage and save it to the geohash_polygons dataframe
        intersect_polygons_4.at[i, 'COVERAGE'] = (intersect_area / geohash_area) * 100





    '''
    STEP 4 AGAIN: IF STUDY AREA COVERAGE INSIDE A GEOHASH IS LESS THAN OR EQUAL TO 10% DIVIDE THE GEOHASH INTO SUB-CELLS
    '''
    # Load the shapefile
    geohashes_4 = intersect_polygons_4

    # Filter the geohashes where coverage <= 10 %
    filtered_geohashes_4 = geohashes_4[geohashes_4['COVERAGE'] <= max_coverage]['geohash'].tolist()

    # Filter the geohashes where coverage > 10 %
    retained_geohashes_4 = geohashes_4[geohashes_4['COVERAGE'] > max_coverage]

    # Run the function on the filtered geohashes
    l = get_subgeohashes(filtered_geohashes_4)

    # Identify the Values of Geo-Hash from keys
    m = list(l.values())

    # Print the Geo-Hash of Sub-Cells
    print(m)

    # Flatten the list of lists into a single list
    flat_list_4 = [item for sublist in m for item in sublist]

    # Convert the Geo-Hash to Shapefile
    n = geohashes_to_shapefile(flat_list_4)





    '''
    STEP 2 AGAIN: FILTER OUT ONLY THOSE GEOHASH POLYGON FEATURES WHICH INTERSECTS WITH THE STUDY AREA CONCAVE HULL
    '''
    # Perform the spatial join operation
    intersect_polygons_5 = gpd.sjoin(n, study_area, predicate = 'intersects', how = 'inner')

    '''
     TIME FOR OUTPUT: POSSIBLE GEOHASH OUTPUT 4
    '''
    # Append the retained Geo-Hash to the subdivided ones
    final_geohashes_7 = pd.concat([retained_geohashes, retained_geohashes_2])
    final_geohashes_8 = pd.concat([final_geohashes_7, retained_geohashes_3])
    final_geohashes_9 = pd.concat([final_geohashes_8, retained_geohashes_4])
    final_geohashes_10 = pd.concat([final_geohashes_9, intersect_polygons_5])





    '''
    TIME TO SAVE THE OUTPUT AS SHAPEFILE
    '''
    # Store the list of Geo-Hash and their lengths in tuples
    geohashes_lengths = [(final_geohashes_10, len(final_geohashes_10)),
                         (final_geohashes_6, len(final_geohashes_6)),
                         (final_geohashes_3, len(final_geohashes_3)),
                         (final_geohashes_1, len(final_geohashes_1)),
                         (final_geohashes_0, len(final_geohashes_0))]

    # All possible lengths of the different list of Geo-Hash
    all_geohash = [len(final_geohashes_0), len(final_geohashes_1), len(final_geohashes_3),
                        len(final_geohashes_6), len(final_geohashes_10)]

    # Filter out those with length more than the "max_geohash"
    acceptable_geohashes = [(gh, l) for gh, l in geohashes_lengths if l <= max_geohash]

    # Save the output as Shapefile with highest number of Geo-Hash within "max_geohash"
    if acceptable_geohashes:
        # sort by length in descending order, and pick the first
        best_geohash, _ = sorted(acceptable_geohashes, key = lambda x: x[1], reverse = True)[0]
        best_geohash.to_file(output_shapefile)
        print("Study Area can be divided into different Number of Geo-Hash: ", all_geohash)
    else:
        print("Least Number of Geo-Hash for covering the Study Area: ", min(all_geohash))
        print("Study Area can be divided into different Number of Geo-Hash: ", all_geohash)

# End of the Python Script