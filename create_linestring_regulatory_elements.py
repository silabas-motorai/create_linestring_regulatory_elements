from qgis.core import *
from qgis.utils import iface
from PyQt5.QtCore import QVariant

layer = iface.activeLayer()
if not layer:
    raise Exception("Please select a layer.")

# Create memory layer for centerlines
centerline_layer = QgsVectorLayer(
    "LineString?crs=" + layer.crs().authid(),
    "center_linesegment",
    "memory"
)
prov = centerline_layer.dataProvider()

new_fields = layer.fields()
new_fields.append(QgsField("source_id", QVariant.Int))
prov.addAttributes(new_fields)
centerline_layer.updateFields()

def midpoint(p1, p2):
    return QgsPointXY((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)

input_count = 0
centerline_count = 0
traffic_element_count = 0
skipped_features = 0

for feat in layer.getFeatures():
    input_count += 1
    geom = feat.geometry()
    if geom.isEmpty():
        continue

    area_type = feat["area_type"].lower() if feat["area_type"] else ""
    if area_type not in ["traffic_sign", "traffic_light"]:
        continue

    traffic_element_count += 1

    if geom.isMultipart():
        lines_to_process = geom.asMultiPolyline()
    else:
        lines_to_process = [geom.asPolyline()]

    for ring in lines_to_process:
        if not ring or len(ring) < 5:
            skipped_features += 1
            area_id = feat["area_id"] if "area_id" in feat.fields().names() else feat.id()
            print(f"⚠ Skipped feature area_id={area_id} - too few nodes ({len(ring)})")
            continue

        # Simplify if too many nodes
        if len(ring) > 5:
            threshold = 0.6 if area_type == "traffic_sign" else 0.25
            geom_simplified = geom.simplify(threshold)
            ring = geom_simplified.asPolyline()
            if len(ring) > 5:
                skipped_features += 1
                area_id = feat["area_id"] if "area_id" in feat.fields().names() else feat.id()
                print(f"⚠ Skipped feature area_id={area_id} - still too many nodes after simplify ({len(ring)})")
                continue

        try:
            p0, p1, p2, p3, _ = ring
        except Exception:
            skipped_features += 1
            area_id = feat["area_id"] if "area_id" in feat.fields().names() else feat.id()
            print(f"⚠ Skipped feature area_id={area_id} - invalid ring after simplify (nodes={len(ring)})")
            continue

        pair1_len = p0.distance(p1)
        pair2_len = p1.distance(p2)

        if area_type == "traffic_sign":
            if pair1_len <= pair2_len:
                mid1 = midpoint(p0, p1)
                mid2 = midpoint(p2, p3)
            else:
                mid1 = midpoint(p1, p2)
                mid2 = midpoint(p3, p0)
        elif area_type == "traffic_light":
            if pair1_len >= pair2_len:
                mid1 = midpoint(p0, p1)
                mid2 = midpoint(p2, p3)
            else:
                mid1 = midpoint(p1, p2)
                mid2 = midpoint(p3, p0)

        centerline = QgsFeature()
        centerline.setGeometry(QgsGeometry.fromPolylineXY([mid1, mid2]))
        centerline.setAttributes(feat.attributes() + [feat.id()])
        prov.addFeature(centerline)
        centerline_count += 1

centerline_layer.updateExtents()
QgsProject.instance().addMapLayer(centerline_layer)

print(f"✅ Input features: {input_count}")
print(f"✅ Traffic element features: {traffic_element_count}")
print(f"✅ Center line segments created: {centerline_count}")
print(f"⚠ Skipped features: {skipped_features}")
