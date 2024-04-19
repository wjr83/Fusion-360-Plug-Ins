'''
Author: William J. Reid
Description: This Fusion 360 script creates a double offset sketch of a selected extruded-cut body profile. 
Offset support exists for: Lines, Arcs, and Circles. The script does not yet support offsetting a spline.
'''

import adsk.core, adsk.fusion, adsk.cam, traceback, math

# Function to calculate the centroid of given curves within a sketch
def calculate_centroid(sketch, curves):
    """
    Calculate the centroid (geometric center) of a collection of sketch entities (lines, arcs, circles).

    Parameters:
    - sketch (adsk.fusion.Sketch): The sketch containing the entities.
    - curves (list): A list of sketch entities (adsk.fusion.SketchLine, SketchArc, SketchCircle).

    Returns:
    - adsk.core.Point3D: The calculated centroid as a Point3D object, or None if no entities are provided.
    """
    x_sum = y_sum = z_sum = 0
    count = 0
    # Iterate through each curve in the collection
    for entity in curves:
        # Handle SketchLine entities
        if type(entity) == adsk.fusion.SketchLine:
            geom = entity.worldGeometry  # Get the geometry of the line
            # Calculate midpoint of the line and add to sum
            x_sum += (geom.startPoint.x + geom.endPoint.x) / 2
            y_sum += (geom.startPoint.y + geom.endPoint.y) / 2
            z_sum += (geom.startPoint.z + geom.endPoint.z) / 2
            count += 1  # Increment count for averaging
        # Handle SketchArc and SketchCircle entities
        elif type(entity) == adsk.fusion.SketchArc or type(entity) == adsk.fusion.SketchCircle:
            geom = entity.worldGeometry  # Get the geometry of the arc or circle
            # Use the center point of arc/circle and add to sum
            x_sum += geom.center.x
            y_sum += geom.center.y
            z_sum += geom.center.z
            count += 1  # Increment count for averaging
    # If curves were processed, return the centroid; otherwise, return None
    if count > 0:
        return adsk.core.Point3D.create(x_sum / count, y_sum / count, z_sum / count)
    else:
        return None
    
def get_arc_parameters(arc_entity):
    """
    Calculate the parameters for a given arc entity including center, start point, end point, and sweep angle.

    Parameters:
    - arc_entity (adsk.fusion.SketchArc): The arc entity from which to calculate parameters.

    Returns:
    - Tuple: Contains the center point, start point, end point (all as adsk.core.Point3D), and the sweep angle (float).
    """
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


# Main function to run the script
def run(context):
    """
    Main function to execute the script. Prompts user for selection and calculates offsets.

    Parameters:
    - context: The application context passed to the script.
    """
    ui = None
    try:
        app = adsk.core.Application.get()  # Get the application instance
        ui = app.userInterface  # Get the user interface instance
        design = adsk.fusion.Design.cast(app.activeProduct)  # Cast the active product to a Design object
        rootComp = design.rootComponent  # Get the root component of the design
        
        selected_edge_obj = ui.selectEntity('Select an edge of the extruded geometry', 'Edges')
        if not selected_edge_obj:
            ui.messageBox('No edge selected.')
            return

        selected_edge = adsk.fusion.BRepEdge.cast(selected_edge_obj.entity)
        face = selected_edge.faces.item(0)
        sketches = rootComp.sketches
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
        # ui.messageBox(f"Generated Geometry Code:\n{final_code}") ## Uncomment to display geometry code
        
        # Prompt user to select an edge or sketch entity
        selectedEdgeInput = ui.selectEntity('Select an edge of the extruded body or a sketch edge', 'Edges,SketchLines,SketchCurves,SketchCircles')
        if not selectedEdgeInput:
            ui.messageBox('No edge selected. Exiting...')  # Exit if nothing is selected
            return
        selectedEntity = selectedEdgeInput.entity  # Get the selected entity

        sketch, curves = None, adsk.core.ObjectCollection.create()
        # Handle selection of a BRepEdge (body edge)
        if isinstance(selectedEntity, adsk.fusion.BRepEdge):
            face = selectedEntity.faces.item(0)  # Assume the first face is relevant
            sketch = rootComp.sketches.add(face)  # Create a new sketch on that face
            proj = sketch.project(selectedEntity)  # Project the edge onto the sketch
            curves.add(proj)  # Add the projected curve to the collection
        # Handle selection of a sketch entity (line, arc, or circle)
        elif isinstance(selectedEntity, (adsk.fusion.SketchLine, adsk.fusion.SketchArc, adsk.fusion.SketchCircle)):
            sketch = selectedEntity.parentSketch  # Use the parent sketch of the selected entity
            connectedCurves = sketch.findConnectedCurves(selectedEntity)  # Find connected curves
            for curve in connectedCurves:
                curves.add(curve)  # Add each connected curve to the collection

        if sketch is None:
            ui.messageBox('Failed to identify or create a sketch based on the selection.')
            return

        # Prompt user for offset distance
        offsetDistanceInput = ui.inputBox('Enter the offset distance in cm (e.g., 0.2 for 2mm inner offset, -0.2 for 2mm outer offset):', 'Offset Distance', '-0.2')
        if not offsetDistanceInput:
            ui.messageBox('Invalid input or operation cancelled.')
            return
        offsetDistance = float(offsetDistanceInput[0])  # Convert input to a float, first item in list is the user's input

        # Calculate centroid for determining offset direction
        dirPoint = calculate_centroid(sketch, curves)
        if not dirPoint:
            ui.messageBox('Failed to calculate centroid.')
            return

        # Perform the offset operation 
        offsetCurve1 = sketch.offset(curves, dirPoint, offsetDistance)
        offsetCurve2 = sketch.offset(curves, dirPoint, offsetDistance*2)  # Creates a second offset
        # To add more offsets, see below:
        # offsetCurve3 = sketch.offset(curves, dirPoint, offsetDistance*3)
        # offsetCurve4 = sketch.offset(curves, dirPoint, offsetDistance*3.5)
        
        ui.messageBox('Offset created successfully.')  # Notify user of success
    except Exception as e:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}')  # Show error message if an exception occurs

run()

