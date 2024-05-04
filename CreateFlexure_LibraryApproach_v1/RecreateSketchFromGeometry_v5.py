'''
Author: William J. Reid
Description: Recreates a hard-coded sketch profile, automatically centers it on the selected extruded-cut circle selected, and automatically scales it to fit the extruded cut.
The hard-coded skech profile is extracted from the output of CreateSketchFromEdge_v4.py script. 
'''

import adsk.core, adsk.fusion, adsk.cam, traceback, math

def addScaledSketchEntities(sketch, entities, offsetX, offsetY, scaleFactor):
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    circles = sketch.sketchCurves.sketchCircles

    for entity in entities:
        entity_type, params = entity
        if entity_type == 'line':
            [(p1, p2)] = params
            lines.addByTwoPoints(
                adsk.core.Point3D.create((p1[0] * scaleFactor) + offsetX, (p1[1] * scaleFactor) + offsetY, p1[2]),
                adsk.core.Point3D.create((p2[0] * scaleFactor) + offsetX, (p2[1] * scaleFactor) + offsetY, p2[2])
            )
        elif entity_type == 'arc':
            [(center, start, sweep)] = params
            radius = math.dist(center, start) * scaleFactor
            angle = math.atan2(start[1] - center[1], start[0] - center[0])
            scaled_center = adsk.core.Point3D.create(center[0] * scaleFactor + offsetX, center[1] * scaleFactor + offsetY, center[2])
            scaled_start = adsk.core.Point3D.create(
                scaled_center.x + math.cos(angle) * radius,
                scaled_center.y + math.sin(angle) * radius,
                start[2]
            )
            arcs.addByCenterStartSweep(scaled_center, scaled_start, sweep)
        elif entity_type == 'circle':
            [(center, radius)] = params
            circles.addByCenterRadius(
                adsk.core.Point3D.create((center[0] * scaleFactor) + offsetX, (center[1] * scaleFactor) + offsetY, center[2]),
                radius * scaleFactor
            )

def scaleArc(arc, scaleFactor, centerPoint):
    """ Scales an arc's radius and repositions its center, start, and end points. """
    # Calculate new center, start, and end points
    newCenter = arc.center.copy()
    newCenter.x = (newCenter.x - centerPoint.x) * scaleFactor + centerPoint.x
    newCenter.y = (newCenter.y - centerPoint.y) * scaleFactor + centerPoint.y
    newStart = arc.startPoint.copy()
    newStart.x = (newStart.x - centerPoint.x) * scaleFactor + centerPoint.x
    newStart.y = (newStart.y - centerPoint.y) * scaleFactor + centerPoint.y
    newEnd = arc.endPoint.copy()
    newEnd.x = (newEnd.x - centerPoint.x) * scaleFactor + centerPoint.x
    newEnd.y = (newEnd.y - centerPoint.y) * scaleFactor + centerPoint.y

    # Move the arc's center, start, and end sketch points
    arc.centerSketchPoint.move(adsk.core.Vector3D.create(newCenter.x - arc.center.x, newCenter.y - arc.center.y, 0))
    arc.startSketchPoint.move(adsk.core.Vector3D.create(newStart.x - arc.startPoint.x, newStart.y - arc.startPoint.y, 0))
    arc.endSketchPoint.move(adsk.core.Vector3D.create(newEnd.x - arc.endPoint.x, newEnd.y - arc.endPoint.y, 0))

    # Scale the radius
    arc.radius *= scaleFactor

def calculateScaleFactor(selectedEdge, standardDiameter):
    selectedDiameter = selectedEdge.geometry.radius
    return selectedDiameter / standardDiameter     
            
# Profiles defined as lists of entities with parameters. NOTE: These are extracted from the output of ExtractSketchProfilev3.
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
    ('arc', [((0.24282679737437718, -1.1751745174555575, 0.0), (0.4118152602072076, -1.0682030285933521, 0.0), 1.210220058493101)]),
    ('arc', [((0.0, 3.552713678800501e-15, 0.0), (-0.20235566447863854, -0.9793120978796335, 0.0), 0.4075255066923056)]),
    ('arc', [((-0.2428267973743667, -1.1751745174555601, 0.0), (-0.20235566447863854, -0.9793120978796335, 0.0), 1.2102200584930949)]),
    ('arc', [((-0.7497921858728598, -0.8542600508689449, 0.0), (-1.0136550613005706, -1.1548867013359654, 0.0), 1.7268198455300467)]),
    ('arc', [((2.220446049250313e-15, 8.992806499463768e-15, 0.0), (-0.9985190145316355, 1.167998139485566, 0.0), 1.713899499579518)]),
    ('arc', [((-0.9335383055107792, 1.0919882226644906, 0.0), (-0.8560413585054538, 1.1551880897913587, 0.0), 1.5939974002165846)]),
    ('line', [((-0.8560413585054538, 1.1551880897913587, 0.0), (-0.8041864823516549, 1.0916025986827826, 0.0))]),
    ('arc', [((-0.8735039664246798, 1.035073200399739, 0.0), (-0.8158169935873945, 0.9667160527608318, 0.0), 1.5539806322450322)]),
    ('arc', [((2.173574380481824e-15, 8.788040859464274e-15, 0.0), (-0.8158169935873945, 0.9667160527608318, 0.0), 1.4339701015339086)]),
    ('arc', [((-0.9428755400430393, -0.6301934528767331, 0.0), (-1.0689582038215373, -0.6763325011960175, 0.0), 3.3326374476121625)]),
    ('arc', [((0.0, -2.7755575615628914e-17, 0.0), (0.9347438288030558, -0.3553223529622128, 0.0), 4.100387675984592)]),
    ('arc', [((1.062194501722192, -0.39740539753378884, 0.0), (0.9347438288030558, -0.3553223529622128, 0.0), 3.119931942715165)]),
    ('arc', [((2.173574380481824e-15, 8.788040859464274e-15, 0.0), (1.1887037993675844, -0.44223902639899737, 0.0), 1.2273207739780094)]),
    ('arc', [((0.8743156529759705, 1.038774523577089, 0.0), (0.80554702633536, 1.095970349110266, 0.0), 1.5649341839123634)]),
    ('line', [((0.80554702633536, 1.095970349110266, 0.0), (0.855932377506641, 1.1565504940868263, 0.0))]),
    ('arc', [((0.9328157019040177, 1.0926055612961212, 0.0), (0.9977461127266836, 1.1686584491466154, 0.0), 1.583683587153986)]),
    ('arc', [((3.774758283725532e-15, 8.770761894538737e-15, 0.0), (1.013655061300581, -1.1548867013359603, 0.0), 1.7145610446097328)]),
    ('arc', [((0.7497921858728687, -0.8542600508689402, 0.0), (0.4118152602072076, -1.0682030285933521, 0.0), 1.726819845530045)]),
]

# BYU CMR BYUCMR_1012603 Ortho-Planar Spring. Link to model: https://www.printables.com/model/596315-ortho-planar-spring
profile_3_entities = [
    ('line', [((-6.265351877706298, -1.2210343694479402, 0.0), (-2.256028704301345, 4.834354190942541, 0.0))]),
    ('arc', [((-2.0892700771953963, 4.723941920934753, 0.0), (-1.9225114524162121, 4.61352964741279, 0.0), 3.141592653589793)]),
    ('line', [((-1.922511452416212, 4.613529647412791, 0.0), (-5.599240163575474, -0.9395325567964026, 0.0))]),
    ('arc', [((-5.432481538885704, -1.0499448302961025, 0.0), (-5.599240163575474, -0.9395325567964022, 0.0), 1.5707963267948968)]),
    ('line', [((-5.542893812385404, -1.2167034549858726, 0.0), (-5.042617937802252, -1.547940276328022, 0.0))]),
    ('arc', [((-4.932205664302553, -1.3811816516382507, 0.0), (-5.042617937802252, -1.547940276328022, 0.0), 1.5707963267948954)]),
    ('line', [((-4.765447039612782, -1.491593925137949, 0.0), (-1.0501310280540923, 4.119747717871052, 0.0))]),
    ('arc', [((-0.7999930909186993, 3.954129307453999, 0.0), (-0.49999568182418536, 3.954129307454002, 0.0), 2.55675246821543)]),
    ('line', [((-0.49999568182418536, 3.954129307454002, 0.0), (-0.5044057926436608, 2.092378729983172, 0.0))]),
    ('arc', [((-0.7216333491621711, 2.0983342529517293, 0.0), (-0.6569468481155115, 1.8908759772740111, 0.0), 1.2411356771439301)]),
    ('arc', [((-0.015526420367374087, -0.018911184783890412, 0.0), (-0.6569468481155113, 1.8908759772740116, 0.0), 1.4618380250357923)]),
    ('arc', [((-2.193290956580717, -0.46494827831482133, 0.0), (-2.0609445901811543, -0.6282144842435663, 0.0), 0.9662758355780897)]),
    ('line', [((-2.060944590181154, -0.6282144842435662, 0.0), (-4.333148818079964, -1.882345324263505, 0.0))]),
    ('arc', [((-4.236336331772661, -2.057350043325488, 0.0), (-4.333148818079964, -1.882345324263505, 0.0), 1.5707963273747172)]),
    ('line', [((-4.41134105077851, -2.1541625297342635, 0.0), (-3.9043543773315115, -3.0706255187692744, 0.0))]),
    ('arc', [((-3.7293496584756647, -2.973813033165222, 0.0), (-3.904354377331511, -3.0706255187692744, 0.0), 0.989046183847823)]),
    ('line', [((-3.744625431501045, -3.173227074168171, 0.0), (3.1108280322455264, -3.6983774017268076, 0.0))]),
    ('arc', [((3.0955522594913285, -3.8977914430118075, 0.0), (3.0802764867371315, -4.097205484296807, 0.0), 3.141592653589793)]),
    ('line', [((3.0802764867371315, -4.097205484296807, 0.0), (-4.03539614433892, -3.5518868026862584, 0.0))]),
    ('arc', [((-4.010494205662711, -3.3534448652208697, 0.0), (-4.149621953392134, -3.497120816258575, 0.0), 0.6444822567520844)]),
    ('line', [((-4.149621953392133, -3.4971208162585756, 0.0), (-6.2377210006787935, -1.4751225940970198, 0.0))]),
    ('arc', [((-6.098593252949369, -1.331446643059307, 0.0), (-6.265351877706299, -1.2210343694479402, 0.0), 1.386319507754715)]),
    ('line', [((-1.038934774834536, 5.313729624391899, 0.0), (1.9348786040456507, 6.110932987403883, 0.0))]),
    ('arc', [((1.9866645403182899, 5.9177555407409255, 0.0), (2.167003505251781, 6.004226153214592, 0.0), 1.3856077084835345)]),
    ('line', [((2.1670035052517806, 6.004226153214592, 0.0), (5.234110869405345, -0.39238596191685815, 0.0))]),
    ('arc', [((5.053771904471855, -0.47885657439052615, 0.0), (4.8734329395383655, -0.5653271868641943, 0.0), 3.1415926325163688)]),
    ('line', [((4.8734329395383655, -0.5653271868641941, 0.0), (1.9939615437159102, 5.43996034545461, 0.0))]),
    ('arc', [((1.8136225787824214, 5.353489732980943, 0.0), (1.9939615437159102, 5.43996034545461, 0.0), 1.570796326794913)]),
    ('line', [((1.727151966308753, 5.53382869791443, 0.0), (1.186135071761242, 5.274416860305623, 0.0))]),
    ('arc', [((1.27260568423491, 5.094077895372133, 0.0), (1.1861350717612429, 5.274416860305623, 0.0), 1.5707963267948994)]),
    ('line', [((1.0922667193014215, 5.007607282898465, 0.0), (4.0616932094964415, -1.1852862836541194, 0.0))]),
    ('arc', [((3.8125344393276315, -1.3047552595774805, 0.0), (3.6743742705377356, -1.5440556915038743, 0.0), 2.541499964531446)]),
    ('line', [((3.6743742705377347, -1.5440556915038741, 0.0), (2.0578140527918043, -0.6127716352343697, 0.0))]),
    ('arc', [((2.1578131891566406, -0.43956805033746305, 0.0), (1.9658278088400856, -0.38352411364881844, 0.0), 1.3312230260674665)]),
    ('arc', [((-0.015526420367374087, -0.018911184783890412, 0.0), (1.9658278088400853, -0.3835241136488188, 0.0), 1.4170953417143881)]),
    ('arc', [((0.7328492803348742, 2.1052600062061204, 0.0), (0.4955855710047106, 2.092378729983171, 0.0), 1.1519783866775823)]),
    ('line', [((0.49558557100471134, 2.0923787299831713, 0.0), (0.4999956818241896, 4.694122916553798, 0.0))]),
    ('arc', [((0.29999740909451894, 4.694122916553797, 0.0), (0.49999568182418974, 4.694122916553798, 0.0), 1.570796326794914)]),
    ('line', [((0.2999974090945146, 4.894121189283469, 0.0), (-0.7897641822599117, 4.894121189283471, 0.0))]),
    ('arc', [((-0.7897641822599104, 4.694122916553797, 0.0), (-0.7897641822599115, 4.89412118928347, 0.0), 0.9859561414205418)]),
    ('line', [((-0.956522807016837, 4.804535190165164, 0.0), (-4.684348156017309, -0.8256996400848076, 0.0))]),
    ('arc', [((-4.851106780774236, -0.7152873664734379, 0.0), (-5.017865405531163, -0.6048750928620678, 0.0), 3.141592653589793)]),
    ('line', [((-5.017865405531164, -0.604875092862068, 0.0), (-1.1539074633188227, 5.230964451340308, 0.0))]),
    ('arc', [((-0.9871488385618923, 5.1205521777289436, 0.0), (-1.038934774834536, 5.3137296243919, 0.0), 0.7240398975936545)]),
    ('line', [((5.125413703463568, -1.8369640216010046, 0.0), (4.362275616964679, -4.751480902709178, 0.0))]),
    ('arc', [((4.168799788832837, -4.700821126458193, 0.0), (4.1535240161501985, -4.900235167513607, 0.0), 1.3911592165597284)]),
    ('line', [((4.153524016150199, -4.900235167513607, 0.0), (-2.977478522472553, -4.353976872233059, 0.0))]),
    ('arc', [((-2.962202749718357, -4.15456283094806, 0.0), (-2.946926976964161, -3.95514878966306, 0.0), 3.141592653589793)]),
    ('line', [((-2.946926976964161, -3.9551487896630597, 0.0), (3.693560597590318, -4.463832022477165, 0.0))]),
    ('arc', [((3.708836370344515, -4.264417981192163, 0.0), (3.6935605975903187, -4.463832022477164, 0.0), 1.5707963267948988)]),
    ('line', [((3.908250411629515, -4.279693753946359, 0.0), (3.954077729845263, -3.6814516296203283, 0.0))]),
    ('arc', [((3.754663688560264, -3.6661758568661296, 0.0), (3.9540777298452627, -3.6814516296203283, 0.0), 1.5707963267949145)]),
    ('line', [((3.769939461314459, -3.4667618155811306, 0.0), (-3.147680031006757, -2.9368493651773058, 0.0))]),
    ('arc', [((-3.002461302028344, -2.674342286763573, 0.0), (-3.1476800310067627, -2.411835208349844, 0.0), 2.131000334223934)]),
    ('line', [((-3.147680031006762, -2.411835208349844, 0.0), (-1.5178510053316665, -1.5130658730975757, 0.0))]),
    ('arc', [((-1.4441596982725928, -1.6505187164899955, 0.0), (-1.3602446682015836, -1.5190578454259502, 0.0), 1.0602503303189499)]),
    ('arc', [((-0.015526420367374087, -0.018911184783890412, 0.0), (-1.360244668201584, -1.51905784542595, 0.0), 1.476435944132634)]),
    ('arc', [((1.471708286216937, -1.798276799854161, 0.0), (1.5957740166026528, -1.5004677177222807, 0.0), 0.7773876618315776)]),
    ('line', [((1.5957740166026526, -1.5004677177222807, 0.0), (3.8152318530316225, -2.7800704198838395, 0.0))]),
    ('arc', [((3.915230989518013, -2.606866834865378, 0.0), (3.815231853031622, -2.78007041988384, 0.0), 1.5707963267949017)]),
    ('line', [((4.088434574536475, -2.7068659713517675, 0.0), (4.601406629291171, -1.8183723097617248, 0.0))]),
    ('arc', [((4.426320974698369, -1.7183011540986417, 0.0), (4.60140662929117, -1.8183723097617248, 0.0), 0.9619895521206652)]),
    ('line', [((4.608542010084632, -1.6319025609232134, 0.0), (1.6221870041016389, 4.596296307426082, 0.0))]),
    ('arc', [((1.8023741537880307, 4.683083537932007, 0.0), (1.9828649335509652, 4.76923753210269, 0.0), 3.1451040172352247)]),
    ('line', [((1.9828649335509652, 4.76923753210269, 0.0), (5.11227684063445, -1.699833633035654, 0.0))]),
    ('arc', [((4.9404486825357425, -1.7854889234679623, 0.0), (5.125413703463568, -1.8369640216010048, 0.0), 0.7338702624799877)]),
    ('circle', [((0.0, 0.0, 0.0), 0.9999913636483746)]),
]

#TODO: Add additional profile entities here:
# profile_4_entities = []


# The goal is to have a library of predefined flexture profiles that can be centered and scaled to fit on an extruded-cut profile. 
profiles = {
    'Circular': {
        '1st Flexure': profile_1_entities,
        '2nd Flexure': profile_2_entities,
        '3rd Flexure': profile_3_entities,
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

def scaleEntity(entity, scaleFactor, center):
    """Scales a given sketch entity around a center point by the scaleFactor."""
    if isinstance(entity, adsk.fusion.SketchLine):
        # Scale line end points
        start = entity.startSketchPoint.geometry.copy()
        end = entity.endSketchPoint.geometry.copy()
        entity.startSketchPoint.move(adsk.core.Vector3D.create((start.x - center.x) * scaleFactor + center.x - start.x,
                                                              (start.y - center.y) * scaleFactor + center.y - start.y,
                                                              (start.z - center.z) * scaleFactor + center.z - start.z))
        entity.endSketchPoint.move(adsk.core.Vector3D.create((end.x - center.x) * scaleFactor + center.x - end.x,
                                                            (end.y - center.y) * scaleFactor + center.y - end.y,
                                                            (end.z - center.z) * scaleFactor + center.z - end.z))
    elif isinstance(entity, adsk.fusion.SketchCircle):
        # Scale circle radius and center
        centerPoint = entity.centerSketchPoint.geometry.copy()
        entity.centerSketchPoint.move(adsk.core.Vector3D.create((centerPoint.x - center.x) * scaleFactor + center.x - centerPoint.x,
                                                                (centerPoint.y - center.y) * scaleFactor + center.y - centerPoint.y,
                                                                (centerPoint.z - center.z) * scaleFactor + center.z - centerPoint.z))
        entity.radius = entity.radius * scaleFactor
    elif type(entity) == adsk.fusion.SketchArc:
            scaleArc(entity, scaleFactor, centerPoint)

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
        
        standardDiameter = 1.0  # Should match reference profile edge diameter (all sketches drawn should have an inner diameter of 10mm = 1cm for the placement of the cylindrical piece). This is in reference to the script ExtractSketchProfilev3.py which is used to extract such sketches.
        scaleFactor = calculateScaleFactor(selectedEdge, standardDiameter)

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

        # Offset XY-Plane
        offsetX = profileCentroid.x
        offsetY = profileCentroid.y

        # Add entities for the selected profile
        addScaledSketchEntities(sketch, profiles[selectedCategory][selectedProfile], offsetX, offsetY, scaleFactor)
        
        # Notify the user
        ui.messageBox('The sketch has been scaled and centered successfully onto the selected profile.')

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

run()
