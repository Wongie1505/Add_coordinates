# Add Coordinates

Add Coordinates is a QGIS plugin that allows you to add points to your map using either projected or geographic coordinates. Each point requires a unique ID and can be previewed in memory before being saved. Supports export to CSV and Shapefile formats.

## Features

- Input points using:
  - Projected coordinates (EPSG:32376)
  - Geographic coordinates (EPSG:4326)
- Ensure **unique IDs** for all points
- Preview points on the QGIS map
- Export points to:
  - CSV
  - Shapefile
- Clear all points from memory with a single click

## Usage

1. Open the plugin from Plugins → Add Coordinates
2. Choose the coordinate type (Projected or Geographic)
3. Enter the coordinates and a unique ID
4. Click **Add Coordinate**
5. Use **Map** to preview points
6. Click **Save** to export and close the plugin
7. Use **Clear** to reset points

## Screenshots

![Add Coordinates UI](icon.png)

## Installation

- Copy the `add_coordinates` folder to your QGIS plugins directory

- Enable the plugin in Plugins → Manage and Install Plugins

## Requirements

- QGIS 3.22 or later
- Python 3.x

## License

MIT License

## Repository

[GitHub Repository](https://github.com/yourusername/add_coordinates)


