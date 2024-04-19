'''
Author: William J. Reid
Description: Recreates a hard-coded sketch profile and allows user to center it on given location in the sketch.
The hard-coded skech profile is extracted from the output of CreateSketchFromEdge_v4.py script. 
'''

import adsk.core, adsk.fusion, adsk.cam, traceback, math

# Define a function to add sketch entities based on provided parameters
def addSketchEntities(sketch, entities, offsetX, offsetY):
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    for entity in entities:
        entity_type, params = entity  # Unpack entity type and parameters
        if entity_type == 'line':
            # Expect params to be a list containing a single tuple with start and end points
            [(p1, p2)] = params  # Unpack the single tuple from the list
            lines.addByTwoPoints(adsk.core.Point3D.create(p1[0] + offsetX, p1[1] + offsetY, p1[2]),
                                 adsk.core.Point3D.create(p2[0] + offsetX, p2[1] + offsetY, p2[2]))
        elif entity_type == 'arc':
            # Expect params to be a list containing a single tuple with center, start, and sweep
            [(center, start, sweep)] = params  # Unpack the single tuple from the list
            arcs.addByCenterStartSweep(adsk.core.Point3D.create(center[0] + offsetX, center[1] + offsetY, center[2]),
                                       adsk.core.Point3D.create(start[0] + offsetX, start[1] + offsetY, start[2]),
                                       sweep)
            
            

#TODO: Add ability to scale the profile entities

# Profiles defined as lists of entities with parameters. NOTE: These are extracted from the output of CreateSketchFromEdge_v4.
# Circular Flexure 1:
profile_1_entities = [
    ('line', [((1.2494080302136261, -0.2530324324719002, 0.0), (0.9674577965561877, -0.2530324324719002, 0.0))]),
    ('arc', [((-1.5439038936193583e-16, -1.5265566588595902e-16, 0.0), (1.0000000000000009, 1.3877787807814457e-16, 0.0), 6.027371896796864)]),
    ('arc', [((1.075000000000001, -0.0006149051189012211, 0.0), (1.0000000000000009, 1.3877787807814457e-16, 0.0), 3.1579897560334134)]),
    ('arc', [((0.0, 0.0, 0.0), (1.1500000000000021, 7.24247051220317e-17, 0.0), 2.7436903559136656)]),
    ('arc', [((-1.1526422635884934, 0.4844817440387874, 0.0), (-1.2490589427729168, 0.5122028479800905, 0.0), 3.0236527152676786)]),
    ('arc', [((1.1102230246251565e-16, 0.0, 0.0), (1.3386514609431721, -0.1746776062198933, 0.0), 2.882189252852549)]),
    ('arc', [((1.2494080302136261, -0.1630324324718983, 0.0), (1.2494080302136261, -0.2530324324719002, 0.0), 1.4410417167180833)])
]

profile_2_entities = [
    ('line', [((-1.6592789413458213, 1.966147787784119, 0.0), (-1.6949306912980673, 1.6653539313301584, 0.0))]),
    ('arc', [((-1.5, 2.5, 0.0), (-1.6964300916145159, 3.334294464481383, 0.0), 2.680923059993525)]),
    ('line', [((-1.6964300916145159, 3.334294464481383, 0.0), (-1.696430091614516, 3.1792755104582486, 0.0))]),
    ('arc', [((-1.5, 2.5, 0.0), (-1.696430091614516, 3.1792755104582486, 0.0), 1.8688250779369004)]),
    ('arc', [((-1.9440790574009414, 2.1636047615944496, 0.0), (-2.0916520976086757, 2.112769067099159, 0.0), 2.0278869566128774)]),
    ('arc', [((-1.5000000000000004, 2.5, 0.0), (-0.9982180699783582, 2.25796103547612, 0.0), 4.520412112076035)]),
    ('line', [((-0.9982180699783582, 2.25796103547612, 0.0), (-0.8356076914561631, 2.25796103547612, 0.0))]),
    ('arc', [((-1.5, 2.5, 0.0), (-0.8356076914561631, 2.25796103547612, 0.0), 1.6386573978738261)]),
    ('line', [((-1.303569908385485, 3.1792755104582486, 0.0), (-1.303569908385485, 3.334294464481383, 0.0))]),
    ('arc', [((-1.5, 2.5, 0.0), (-1.0198001139018031, 1.790042181712714, 0.0), 2.315663672647186)]),
    ('line', [((-1.0198001139018031, 1.790042181712714, 0.0), (-1.1931017772868793, 2.0350468340364123, 0.0))]),
    ('arc', [((-1.5000000000000004, 2.5000000000000013, 0.0), (-1.6592789413458213, 1.966147787784119, 0.0), 0.8733661086865097)]),
]


#TODO: Add additional profile entities here:
# profile_2_entities = []


# The goal is to have a library of predefined flexture profiles that can be centered and scaled to fit on an extruded-cut profile. 
profiles = {
    'Circular': {
        '1st Flexure': profile_1_entities,
        '2nd Flexure': profile_2_entities
        # Add more circular profiles here
    },
    'Triangular': {
        # Define triangular profiles and their creation functions here
    },
    'Square': {
        # Define square profiles and their creation functions here
    },
    # Additional categories and profiles can be added here
}

def calculateProfileCentroid(loop):
    """Calculate the centroid of a profile that may include lines, arcs, and circles."""
    
    centroid_x = centroid_y = centroid_z = 0
    total_length = 0  # Use total arc length for arcs and circles, and total length for lines
    
    for edge in loop.edges:
        geom = edge.geometry
        
        if isinstance(geom, adsk.core.Line3D):
            # Handle lines
            startPoint = geom.startPoint
            endPoint = geom.endPoint
            edge_length = startPoint.distanceTo(endPoint)
            centroid_x += (startPoint.x + endPoint.x) / 2 * edge_length
            centroid_y += (startPoint.y + endPoint.y) / 2 * edge_length
            centroid_z += (startPoint.z + endPoint.z) / 2 * edge_length
            total_length += edge_length
            
        elif isinstance(geom, adsk.core.Arc3D):
            # Handle arcs
            center = geom.center
            radius = geom.radius
            startAngle = geom.startAngle
            endAngle = geom.endAngle
            arc_length = radius * abs(endAngle - startAngle)
            # Approximation: Centroid of arc segment as the midpoint of the chord for simplicity
            startPoint = geom.startPoint
            endPoint = geom.endPoint
            centroid_x += (startPoint.x + endPoint.x) / 2 * arc_length
            centroid_y += (startPoint.y + endPoint.y) / 2 * arc_length
            centroid_z += (startPoint.z + endPoint.z) / 2 * arc_length
            total_length += arc_length
            
        elif isinstance(geom, adsk.core.Circle3D):
            # Handle circles
            center = geom.center
            circumference = 2 * math.pi * geom.radius
            centroid_x += center.x * circumference
            centroid_y += center.y * circumference
            centroid_z += center.z * circumference
            total_length += circumference

    # Calculate the weighted average of centroids
    if total_length == 0:
        return None  # Avoid division by zero
    
    centroid = adsk.core.Point3D.create(centroid_x / total_length, centroid_y / total_length, centroid_z / total_length)
    return centroid


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        root_comp = design.rootComponent

        # User interface logic for selecting a category
        categories = ', '.join(profiles.keys())
        categoryResult = ui.inputBox('Enter profile category [Circular, Triangular, Square]:', 'Select Category', 'Circular')[0]
                    
        # Check if the user canceled the input operation
        if categoryResult is None:
            ui.messageBox('Operation canceled by the user.')
            return
        
        selectedCategory = str(categoryResult).strip()  # Ensure it's a string and remove any whitespace

        if selectedCategory not in profiles:
            ui.messageBox(f'Invalid category selected: {selectedCategory}')
            return
        
        # Similar handling for profile selection within the category
        profileNames = ', '.join(profiles[selectedCategory].keys())
        profileResult = ui.inputBox('Enter profile name:', 'Select Profile', list(profiles[selectedCategory].keys())[0])[0]

        if profileResult is None:
            ui.messageBox('Operation canceled by the user.')
            return
        
        selectedProfile = str(profileResult).strip()

        if selectedProfile not in profiles[selectedCategory]:
            ui.messageBox(f'Invalid profile selected: {selectedProfile}')
            return

        
         # Prompt the user to select an edge of the profile to center the sketch
        edgeSelection = ui.selectEntity('Select an edge of the profile to center the sketch', 'Edges')
        if not edgeSelection:
            ui.messageBox('No edge selected.')
            return
        selectedEdge = adsk.fusion.BRepEdge.cast(edgeSelection.entity)

        # Identify the loop (profile) containing the selected edge
        face = selectedEdge.faces.item(0)  # Assuming the first face is relevant
        loop = None
        for l in face.loops:
            if selectedEdge in l.edges:
                loop = l
                break
        
        if not loop:
            ui.messageBox('Failed to identify the loop containing the selected edge.')
            return

        # Calculate the centroid of the selected profile
        profileCentroid = calculateProfileCentroid(loop)
        if not profileCentroid:
            ui.messageBox('Failed to calculate the profile centroid.')
            return

        # Prompt the user to select a planar face or construction plane for the new sketch
        planarEntity = ui.selectEntity('Select a planar face or construction plane for the new sketch', 'PlanarFaces,ConstructionPlanes')
        if not planarEntity:
            ui.messageBox('No planar entity selected.')
            return

        selectedEntity = adsk.fusion.ConstructionPlane.cast(planarEntity.entity) or adsk.fusion.BRepFace.cast(planarEntity.entity)
        if not selectedEntity:
            ui.messageBox('Invalid selection.')
            return

        # Create a new sketch on the selected plane
        sketch = root_comp.sketches.add(selectedEntity)

        #TODO: Fix Centroid calculation and placement for Profile 2. Works correctly for Profile 1.
        offsetX = profileCentroid.x
        offsetY = profileCentroid.y

        # Add entities for the selected profile
        addSketchEntities(sketch, profiles[selectedCategory][selectedProfile], offsetX, offsetY)

        # Notify the user
        ui.messageBox('The sketch centered on the selected profile has been created successfully.')

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

run()
