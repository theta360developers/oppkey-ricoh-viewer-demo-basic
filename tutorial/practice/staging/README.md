# Image Transformations From RICOH360 Cloud API

![main gui](readme_assets/main_gui.png)

You can perform transformations directly with the RICOH
Cloud API and display it in the viewer.

This example shows different staging transformations.

![blue couch and plant](readme_assets/blue_couch_plant.png)

## process

1. generate viewer token and save in app for duration of session or specified time
1. generate content token and save in app
1. get content_id from RICOH360 Cloud using content token
1. pass content_id and viewer token to RICOH360 Viewer to start or switchScene

![corner placement](readme_assets/corner_placement.png)

![green couch](readme_assets/green_couch.png)

## Cloud API enhancement

The most popular API is enhancement.  There are three different types of
enhancement. The enhancement in the RICOH360 Viewer API is for automatic
selection.  You can get more control of the enhancement by accessing
the Cloud API directly.

