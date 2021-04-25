# Processing Melbourne's bus stops using osmnx

import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx
from shapely.geometry import Point, LineString
import re
import matplotlib.pyplot as plt

# Reads stop information
all_stops = pd.read_csv("melb_bus_gtfs/stops.txt")
stop_points = gpd.GeoDataFrame(all_stops,
                               geometry=[Point(xy) for xy
                                         in zip(all_stops.stop_lon,
                                                all_stops.stop_lat)])

# Generates Melbourne graph
melbourne_polygon = \
    osmnx.geocode_to_gdf('Melbourne, Victoria, Australia').geometry[0]
melbourne_graph = osmnx.graph_from_polygon(melbourne_polygon,
                                           network_type='walk')
# Filters stops not within the study area
melbourne_stops = stop_points[stop_points.geometry.within(melbourne_polygon)]
# Gets Melbourne CBD's node
MELB_LOCATION = (-37.81361111, 144.96305556)
city_node = osmnx.get_nearest_node(melbourne_graph, MELB_LOCATION)

nearests = []  # Nearest nodes
node_dists = []  # Distance from intersection
cbd_dists = []  # Distance from Melbourne
suburbs = []  # Suburb extracted from stop name
#       ...(Hillside  (30 )   )
REGEXP = "\([^\(\)]*(\(.*\))*\)$"

# Calculates statistics for each stop
for i in range(len(melbourne_stops)):
    stop = melbourne_stops.iloc[i]
    n, node_d = osmnx.get_nearest_node(melbourne_graph,
                                       (stop.stop_lat, stop.stop_lon),
                                       return_dist=True)
    cbd_d = nx.shortest_path_length(melbourne_graph, source=city_node, target=n,
                                    weight='length')
    nearests.append(n)
    node_dists.append(node_d)
    cbd_dists.append(cbd_d)
    suburbs.append(re.search(REGEXP, stop.stop_name)[0][1:-1])
    print('+', end='')
print('Finished stops')

melbourne_stops['nearest'] = nearests
melbourne_stops['node_dist'] = node_dists
melbourne_stops['cbd_dist'] = cbd_dists
melbourne_stops['suburb'] = suburbs

melbourne_stops.to_file('melbourne_processed.shp')

# Generates map of all stops
fig, ax = osmnx.plot_graph(melbourne_graph, figsize=(20, 20),
                           node_color='#999999', show=False, close=False)
ax.scatter(list(melbourne_stops.stop_lon), list(melbourne_stops.stop_lat),
           c='#f68a24', s=20)
plt.savefig('melb_all_stops.png')


# Colours stops by distance
def colour(dist):
    if dist < 20:
        return 'b'
    elif dist < 50:
        return 'g'
    elif dist < 100:
        return 'y'
    else:
        return 'r'


# Generates map of all stops
colours = [colour(d) for d in melbourne_stops.node_dist]
fig, ax = osmnx.plot_graph(melbourne_graph, figsize=(20, 20),
                           node_color='#999999', show=False, close=False)
ax.scatter(list(melbourne_stops.stop_lon), list(melbourne_stops.stop_lat),
           c=colours, s=20)
plt.savefig('melb_all_stops_dist.png')

# Generates map of far stops
far_stops = melbourne_stops[melbourne_stops.node_dist > 200]
fig, ax = osmnx.plot_graph(melbourne_graph, figsize=(20, 20),
                           node_color='#999999', show=False, close=False)
ax.scatter(list(far_stops.stop_lon), list(far_stops.stop_lat), c='r', s=50)
plt.savefig('melb_far_stops.png')

# Generates histogram
melbourne_stops[melbourne_stops.node_dist < 200].node_dist.hist(bins=40)
plt.xlabel('Distance to intersection (metres)')
plt.ylabel('Number of stops')
plt.savefig('histogram.png')

# Prints statistics
print('Mean distance:', melbourne_stops.node_dist.mean())
print('Median distance:', melbourne_stops.node_dist.median())
print('Standard deviation:', melbourne_stops.node_dist.std())
melbourne_area = osmnx.projection.project_geometry(melbourne_polygon)[0].area
print(osmnx.basic_stats(melbourne_graph, area=melbourne_area))
