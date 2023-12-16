# GeoHash Optimization for Geospatial Datasets
<p align="center">
  <img src="https://github.com/akhilchibber/Optimum-Geohash/blob/main/geohash.jpeg?raw=true" alt="earthml Logo">
</p>

Welcome to this repository, where we focus on optimizing the use of GeoHash for any given geospatial dataset. This Python script is designed to find the smallest possible set of GeoHashes that can completely cover a given geospatial area.

## What is GeoHash?

GeoHash is a system of encoding geographical locations into short strings of letters and digits. It is a form of geocoding that divides the world into a grid and assigns a unique code to each cell in the grid. This method is widely used for simplifying and indexing spatial data.

## Purpose of the Script

The script aims to:
1. Determine the smallest possible single or set of GeoHashes for a given geospatial dataset.
2. Convert these GeoHashes into polygonal representations in the form of shapefiles.

## How the Script Works

The script operates in multiple steps:
1. **Loading and Bounds Calculation:** It starts by loading the geospatial dataset and calculating its bounds.
2. **GeoHash Calculation:** The script calculates an initial GeoHash based on the dataset's center and iteratively refines it to find the smallest GeoHash covering the entire area.
3. **Sub-division into Sub-Cells:** If the area cannot be covered by a single GeoHash, the script subdivides it into smaller GeoHash cells.
4. **Intersection Analysis:** It filters out GeoHashes based on their intersection with the study area and their coverage percentage.
5. **Final Output:** The script produces a list of optimal GeoHashes and saves them as a shapefile.

### Key Features

- **Efficient Coverage:** Finds the smallest possible GeoHashes covering the entire study area.
- **Customizable Precision:** Allows adjustment of GeoHash precision based on dataset needs.
- **Shapefile Conversion:** Converts GeoHashes into polygon shapefiles for easy visualization and analysis.

## Getting Started

To use this script, ensure you have Python installed along with libraries like `fiona`, `pygeohash`, `geopandas`, and `shapely`.

### Prerequisites

- Python 3.x
- Libraries: `fiona`, `pygeohash`, `geopandas`, `shapely`, `pyproj`, `pandas`, `math`, `string`

### Running the Script

1. Place your geospatial dataset in the script's designated file path.
2. Run the script using Python.
3. The output will be a shapefile representing the optimal set of GeoHashes for your dataset.

## Benefits of Using This Script

- **Optimization:** Maximizes the efficiency of spatial data representation.
- **Ease of Use:** Simplifies complex geospatial calculations into a few steps.
- **Versatility:** Applicable to various types of geospatial datasets.

## Contributing

We welcome contributions to enhance the functionality and efficiency of this script. Feel free to fork, modify, and make pull requests to this repository. To contribute:

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request against the `main` branch.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contact

Author - Akhil Chhibber

LinkedIn: https://www.linkedin.com/in/akhilchhibber/
