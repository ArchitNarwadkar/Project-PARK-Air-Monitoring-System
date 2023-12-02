# Project PARK Air Monitoring System

## Repository Structure and Descriptions

### Data Calibration
Contains codes for calibrating new sensors using the Aeroqual sensor.

### Data Preprocessing
Holds codes for:
Extracting data from ThingSpeak.
Pre-processing using standard methods (like interquartile range and linear interpolation).
Storing data in a suitable format for website display.

### Website
Includes:
Python server code to run the website locally.
Images and assets in the static folder.
HTML pages in the templates folder.
Interfacing
Contains codes for running sensors:
Two folders for indoor and outdoor sensors.
Corresponding codes for interfacing these sensors.
Arduino IDE used for writing and uploading codes.
Codes collect sensor data and upload to ThingSpeak channels via internet connection.
