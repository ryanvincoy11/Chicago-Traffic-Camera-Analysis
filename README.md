The chicago-traffic-cameras.db was too big of a file to upload so here are the links to access that data:
https://data.cityofchicago.org/Transportation/Red-Light-Camera-Violations/spqx-js37/about_data
https://data.cityofchicago.org/Transportation/Speed-Camera-Violations/hhkd-xvj4/about_data
There are 5 tables in the database: Intersections, RedCameras, SpeedCameras, RedViolations, and SpeedViolations.
(The database uses foreign keys. A foreign key is a primary key stored in another table, typically used to join those tables. You may think of a foreign key as a pointer to the table where it is a primary key.
Code uses matplotlib import to plot data pulled from the databases using SQL queries that were implemented using the sqlite3 import.
