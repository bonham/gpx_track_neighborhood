# Extraction Modes

There are two modes how you can display the tracks on the map

1. *Category mode*: Color coding depending on how often you passed the same road
2. *Plain mode*: Just display the tracks you have imported to the database in rotating colors

Usage: `usage: 4-export-geojson.py [-h] [-m {category,plain}] database dataset_label`

The mode is controlled by the `-m` flag. If you omit the flag then *category mode* is the default.

Note: If you only want to export in plain mode, then you can skip the python scripts *2-proximity-calc.py* and *3-category-calc.py* 
