'''
Author: William J. Reid
Description: This Fusion 360 script creates a single offset sketch from a selected sketch profile. 
The sketch profile does not need to be a closed sketch. It supports creating a offsets for lines, arcs, circles and splines.
'''

import adsk.core, adsk.fusion, adsk.cam, traceback

# Function to calculate the centroid of given curves within a sketch
def calculate_centroid(sketch, curves):
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

# Main function to run the script
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()  # Get the application instance
        ui = app.userInterface  # Get the user interface instance
        design = adsk.fusion.Design.cast(app.activeProduct)  # Cast the active product to a Design object
        rootComp = design.rootComponent  # Get the root component of the design
        
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
        offsetDistanceInput = ui.inputBox('Enter the offset distance in cm (e.g., 0.2 for 2mm inner offset, -0.2 for 2mm outer offset):', 'Offset Distance', '0.2')
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
        offsetCurves = sketch.offset(curves, dirPoint, offsetDistance)

        ui.messageBox('Offset created successfully.')  # Notify user of success
    except Exception as e:
        if ui:
            ui.messageBox(f'Failed:\n{traceback.format_exc()}')  # Show error message if an exception occurs

run()
