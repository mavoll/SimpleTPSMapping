# SimpleTPSMapping
Tool using Thin plate splines (TPS) transformation to convert pixel coordinates (x, y) to GPS-coordinates (lat, long). OpenCVs [ThinPlateSplineShapeTransformer](https://docs.opencv.org/3.4.5/dc/d18/classcv_1_1ThinPlateSplineShapeTransformer.html) is used to perform TPS transformation.

#### Please note:
This is an very easy and not very precise approach but represents the general basics and gives first results. So far it requires much manual effort to 1. adjust the reference map image accordingly to the image representing the perspective of the fixed camera (see screenshots for illustration of this approach) as well as to 2. choose sets of points as inputs to the TPS transformation.

Also this easy approach just uses Google Maps to get an screenshot and it's corresponding GPS-coordinates (see chapter "Usage" for illustration).
Furthermore this approach does not take into account the altitude.

We will also present an more precise approach using official Ground Control Points(GCPs) and GIS system to do the mapping process (see [here]())

## Further development and research opportunities

* Add more tools to fine tune the transformation matrix manually to get better results.
* Are better TPS implementations than OpenCVs ThinPlateSplineShapeTransformer available or do exist better transformation methods than TPS to do the job?
* Investigate and test more sophisticated methods to automize or semi-automize the process of keypoint selection as well as to get better mapping results.
  * Keyword: Shape Context Matching

## Prerequisites: ###

- Ubuntu or Windows
- Python 3.6
- OpenCV 3.4

### Install: ###

## Usage: ##

<p align="center">
  <img src="/images/choose_transpa.png" width="800" align="middle">
</p>

<p align="center">
  <img src="/images/adjust_1.png" width="275" align="middle">
  <img src="/images/adjust_2.png" width="275" align="middle">
  <img src="/images/adjust_3.png" width="275" align="middle">
</p>
<p align="center">
  <img src="/images/draw_points_1.png" width="275" align="middle">
  <img src="/images/draw_points_2.png" width="275" align="middle">
  <img src="/images/draw_points_3.png" width="275" align="middle">
</p>

<p align="center">
  <img src="/images/result_1.png" width="800" align="middle">
</p>

## Authors

* **Marc-André Vollstedt** - marc.vollstedt@gmail.com

## Acknowledgments
