# SimpleTPSMapping
Tool using Thin plate splines (TPS) transformation to convert pixel coordinates (x, y) to GPS-coordinates (lat, long).

#### Please note:
This is an very easy and not very precise approach but represents the general basics and gives first results. So far it requires much manual effort to 1. adjust the reference map image accordingly to the image representing the perspective of the fixed camera (see screenshots for illustration of this approach) as well as to 2. choose sets of points as inputs to the TPS transformation.
Also this easy approach just uses Google Maps to get an screenshot and it's corresponding GPS-coordinates (see chapter "Usage" for illustration).
Furthermore this approach does not take into account the altitude.
We will also present an more precise approach using official Ground Control Points(GCPs) and GIS system to do the mapping process (see [here]())

## Further development and research opportunities

* Add more tools to fine tune the transformation matrix manually to get better results.
* Investigate and test more sophisticated methods to automize or semi-automize the process of keypoint selection as well as to get better mapping results.
  * Keyword: Shape Context Matching

## Prerequisites: ###

- Ubuntu or Windows
- Python 3.6
- OpenCV 3.4

### Install Anaconda: ###

## Usage: ##

## Authors

* **Marc-André Vollstedt** - marc.vollstedt@gmail.com

## Acknowledgments
