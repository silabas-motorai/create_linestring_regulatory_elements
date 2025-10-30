# create_linestring_regulatory_elements
This QGIS Python script generates linestrings for the regulatory element features (traffic signs and traffic lights) based on feature map geometries provided as **LineString** or **MultiLineString** inputs.

## Features
- Processes only features where `area_type` is `"traffic_sign"` or `"traffic_light"`.
- Automatically simplifies geometries with too many vertices:
  - `traffic_sign` → simplified with 0.6 m tolerance  
  - `traffic_light` → simplified with 0.25 m tolerance  
- Calculates centerlines by connecting the midpoints of opposite edges.
- Skips invalid or non-rectangular geometries and logs them with their `area_id`.
- Outputs results as a new **memory layer** named `centerlines_linestring`.

## Usage
1. Open your input layer in **QGIS**.
2. Make sure it contains an attribute named `area_type`.
3. Open the **Python Console** (`Ctrl+Alt+P`) → Paste the script → Press **Run**.
4. The script will create a new memory layer containing all generated centerlines.

## Requirements
- QGIS (3.x or newer)
- The input layer must contain closed rectangular geometries (in LineString format).

## Output Example
After execution, the console will print summary info:
✅ Input features: 2188
✅ Traffic element features: 742
✅ Centerlines created: 740
⚠ Skipped features: 2


<img width="409" height="391" alt="Screenshot from 2025-10-30 16-28-54" src="https://github.com/user-attachments/assets/4ca8344a-67c0-4b2b-9ca8-8f3b1c2f5b38" />
