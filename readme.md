7CUSMSDA Spatial Data Analysis
Bus stop placement in Melbourne and London, an analysis
k20074927

The below files were used to process data for the purposes of this analysis

* 'Melbourne Bus.ipynb' reads Melbourne stop data, performing initial analysis
* 'London Bus.ipynb' reads London stop data, performing initial analysis
* 'melbourne_process.py' uses osmnx to calculate distance from each Melbourne bus stop to its nearest intersection, in addition to some other statistics
* 'bus_data.py' accesses the Transport for London API to fetch all London bus stops, performing some initial filtering.
* 'london_process.py' uses osmnx to calculate distance from each London bus stop to its nearest intersection, in addition to some other statistics
* 'diversity.py' uses osmnx to calculate the number of points of interest and diversity at stops.
* 'Melbourne_bus_extra.ipynb' uses extra gtfs data to generate additional statistics regarding the distance between bus stops in the city
* 'Melb_Bus_Stats.ipynb' generates charts and statistics from all information previously generated for Melbourne
* 'London_Bus_Stats.ipynb' generates charts and statistics from all information previously generated for London