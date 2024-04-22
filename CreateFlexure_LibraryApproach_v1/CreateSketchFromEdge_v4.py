import adsk.core, adsk.fusion, adsk.cam, traceback, math

def get_sketch_normal(sketch):
    """
    Attempts to determine the normal vector of the sketch plane with added validation checks.
    """
    try:
        # Check if the sketch has a valid referencePlane before accessing it
        if sketch.referencePlane and sketch.referencePlane.geometry:
            return sketch.referencePlane.geometry.normal
        else:
            # Log an error or warning if the reference plane is not available
            print("Warning: Sketch does not have a valid reference plane. Using default Z normal.")
            return adsk.core.Vector3D.create(0, 0, 1)  # Default to Z normal if unspecified
    except Exception as e:
        print(f"Error accessing sketch normal: {str(e)}")
        return adsk.core.Vector3D.create(0, 0, 1)  # Fallback to default normal on any error


def get_arc_parameters(arc_entity, sketch_normal):
    """
    Extracts and computes the parameters for an arc entity.
    """
    center = arc_entity.geometry.center
    start_point = arc_entity.startSketchPoint.geometry
    end_point = arc_entity.endSketchPoint.geometry

    vector_start = center.vectorTo(start_point)
    vector_end = center.vectorTo(end_point)

    # Normalize vectors to use for angle calculation
    vector_start.normalize()
    vector_end.normalize()

    dot_product = vector_start.dotProduct(vector_end)
    angle = math.acos(min(max(dot_product, -1.0), 1.0))  # Clamped to avoid precision issues

    # Determine the direction of the sweep based on the cross product
    cross_product = vector_start.crossProduct(vector_end)
    cross_product_sign = cross_product.dotProduct(sketch_normal)

    # Adjust angle for arcs that are larger than 180 degrees
    if cross_product_sign < 0:
        angle = 2 * math.pi - angle

    return (center.asArray(), start_point.asArray(), angle)

def get_circle_parameters(circle_entity):
    """
    Extracts parameters for a circle entity.
    """
    center = circle_entity.geometry.center
    radius = circle_entity.geometry.radius
    return (center.asArray(), radius)

def get_spline_parameters(spline_entity):
    """
    Extracts parameters for a spline entity.
    """
    points = [point.geometry.asArray() for point in spline_entity.fitPoints]
    return points

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
        sketch_normal = get_sketch_normal(sketch)

        profile_entities = []

        for edge in selected_edge.faces.item(0).loops.item(0).edges:
            projected_entity = sketch.project(edge)
            for entity in projected_entity:
                if isinstance(entity, adsk.fusion.SketchLine):
                    start = entity.startSketchPoint.geometry
                    end = entity.endSketchPoint.geometry
                    profile_entities.append(('line', [((start.x, start.y, start.z), (end.x, end.y, end.z))]))
                elif isinstance(entity, adsk.fusion.SketchArc):
                    center, start_point, sweep_angle = get_arc_parameters(entity, sketch_normal)
                    profile_entities.append(('arc', [(center, start_point, sweep_angle)]))
                elif isinstance(entity, adsk.fusion.SketchCircle):
                    center, radius = get_circle_parameters(entity)
                    profile_entities.append(('circle', [(center, radius)]))
                elif isinstance(entity, adsk.fusion.SketchFittedSpline):
                    points = get_spline_parameters(entity)
                    profile_entities.append(('spline', [points]))

        # Format the output for display in a message box to mimic a Python list
        entity_strings = ["    ('{}', {}),".format(e[0], e[1]) for e in profile_entities]
        display_text = "profile_entities = [\n" + "\n".join(entity_strings) + "\n]"
        ui.messageBox(display_text)

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

run()
