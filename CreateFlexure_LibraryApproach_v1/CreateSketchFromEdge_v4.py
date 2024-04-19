

import adsk.core, adsk.fusion, adsk.cam, traceback, math

def get_arc_parameters(arc_entity):
    center = arc_entity.geometry.center
    start_point = arc_entity.startSketchPoint.geometry
    end_point = arc_entity.endSketchPoint.geometry
    
    # Create vectors from the center to the start and end points
    vector_start = center.vectorTo(start_point)
    vector_end = center.vectorTo(end_point)
    
    # Normalize vectors
    vector_start.normalize()
    vector_end.normalize()
    
    # Calculate the dot product for the angle
    dot_product = vector_start.dotProduct(vector_end)
    angle = math.acos(dot_product)

    # Calculate the cross product for determining the sweep direction
    cross_product = vector_start.crossProduct(vector_end)
    sketch_normal = adsk.core.Vector3D.create(0, 0, 1)  # Assuming sketch is on XY plane, adjust if necessary
    if cross_product.dotProduct(sketch_normal) < 0:
        angle = 2 * math.pi - angle  # Adjusting for clockwise direction
    
    return center, start_point, end_point, angle

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        root_comp = design.rootComponent

        selected_edge_obj = ui.selectEntity('Select an edge of the extruded geometry', 'Edges')
        if not selected_edge_obj:
            ui.messageBox('No edge selected.')
            return

        selected_edge = adsk.fusion.BRepEdge.cast(selected_edge_obj.entity)
        face = selected_edge.faces.item(0)
        sketches = root_comp.sketches
        sketch = sketches.add(face)

        geometry_creation_code = []

        for edge in selected_edge.faces.item(0).loops.item(0).edges:
            projected_entity = sketch.project(edge)
            for entity in projected_entity:
                if isinstance(entity, adsk.fusion.SketchLine):
                    start = entity.startSketchPoint.geometry
                    end = entity.endSketchPoint.geometry
                    line_code = f"sketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create({start.x}, {start.y}, {start.z}), adsk.core.Point3D.create({end.x}, {end.y}, {end.z}))"
                    geometry_creation_code.append(line_code)
                elif isinstance(entity, adsk.fusion.SketchArc):
                    center, start_point, end_point, sweep_angle = get_arc_parameters(entity)
                    arc_code = f"sketch.sketchCurves.sketchArcs.addByCenterStartSweep(adsk.core.Point3D.create({center.x}, {center.y}, {center.z}), adsk.core.Point3D.create({start_point.x}, {start_point.y}, {start_point.z}), {sweep_angle})"
                    geometry_creation_code.append(arc_code)

        final_code = "\n".join(geometry_creation_code)
        ui.messageBox(f"Generated Geometry Code:\n{final_code}")

    except Exception as e:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

run()

