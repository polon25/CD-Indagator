# CD-Indagator
Software of the system for smartphone's localization based on Bluetooth signal analysis.

System is based on three parts:
- Bluetooth beacons based on HM-10 MLT-BT05
- Android client which constanlty reads RSSI of nearby devices and sends the values (with time, device's name and MAC of the smarthone) to the server via local Wi-Fi
- Server written in Python reading receiving data and saving them in SQL database after some cleaning

Test were done in two configurations:
1) Localization based on receiving data from at least four beacons, for which distance from the Android device is calculated. Then they're treated as a center of spheres with radius equal to calculated distances - Smartphone is in their intersection point.
2) Simplified localization based only on the information about the closest beacon.
