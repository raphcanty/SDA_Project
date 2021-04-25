# Processing London's bus stops using osmnx

import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx
from shapely.geometry import Point, LineString, Polygon
import re
import matplotlib.pyplot as plt

# Reads stop information
all_stops = pd.read_csv("london_stops.csv")
stop_points = gpd.GeoDataFrame(all_stops,
                               geometry=[Point(xy) for xy
                                         in zip(all_stops.lon,
                                                all_stops.lat)])

# Generates London graph
london_polygon = \
    osmnx.geocode_to_gdf('London, England, United Kingdom').geometry[0]
# Removes City of London hole
london_polygon = Polygon(london_polygon.exterior)
london_graph = osmnx.graph_from_polygon(london_polygon,
                                        network_type='walk')
# Filters stops not within the study area
london_stops = stop_points[stop_points.geometry.within(london_polygon)]
# Gets London CBD's node
LONDON_LOCATION = (51.50722222, -0.12750000)
city_node = osmnx.get_nearest_node(london_graph, LONDON_LOCATION)

nearests = []  # Nearest nodes
node_dists = []  # Distance from intersection
cbd_dists = []  # Distance from London

# Calculates statistics for each stop
for i in range(len(london_stops)):
    stop = london_stops.iloc[i]
    n, node_d = osmnx.get_nearest_node(london_graph,
                                       (stop.lat, stop.lon),
                                       return_dist=True)
    cbd_d = nx.shortest_path_length(london_graph, source=city_node, target=n,
                                    weight='length')
    nearests.append(n)
    node_dists.append(node_d)
    cbd_dists.append(cbd_d)
    print('+', end='')
print('Finished stops')

london_stops['nearest'] = nearests
london_stops['node_dist'] = node_dists
london_stops['cbd_dist'] = cbd_dists

london_stops.to_file('london_processed.shp')

# Generates map of all stops
fig, ax = osmnx.plot_graph(london_graph, figsize=(20, 20),
                           node_color='#999999', show=False, close=False)
ax.scatter(list(london_stops.lon), list(london_stops.lat),
           c='#f68a24', s=20)
plt.savefig('london_all_stops.png')


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
colours = [colour(d) for d in london_stops.node_dist]
fig, ax = osmnx.plot_graph(london_graph, figsize=(20, 20),
                           node_color='#999999', show=False, close=False)
ax.scatter(list(london_stops.lon), list(london_stops.lat),
           c=colours, s=20)
plt.savefig('london_all_stops_dist.png')

# Generates map of far stops
far_stops = london_stops[london_stops.node_dist > 200]
fig, ax = osmnx.plot_graph(london_graph, figsize=(20, 20),
                           node_color='#999999', show=False, close=False)
ax.scatter(list(far_stops.lon), list(far_stops.lat), c='r', s=50)
plt.savefig('london_far_stops.png')

# Generates histogram
london_stops[london_stops.node_dist < 200].node_dist.hist(bins=40)
plt.xlabel('Distance to intersection (metres)')
plt.ylabel('Number of stops')
plt.savefig('histogram.png')

# Prints statistics
print('Mean distance:', london_stops.node_dist.mean())
print('Median distance:', london_stops.node_dist.median())
print('Standard deviation:', london_stops.node_dist.std())
london_area = osmnx.projection.project_geometry(london_polygon)[0].area
print(osmnx.basic_stats(london_graph, area=london_area))
