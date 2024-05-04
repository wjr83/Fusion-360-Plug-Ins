'''
Author: William J. Reid
Description: Recreates a hard-coded circular-type sketch profile, centers it on the extruded-vut circle profile selected, and scales it to the extrusion diameter.
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
            scaled_center = adsk.core.Point3D.create(center[0] * scaleFactor + offsetX, center[1] * scaleFactor + offsetY, center[2])
            radius = math.dist(center, start) * scaleFactor
            angle = math.atan2(start[1] - center[1], start[0] - center[0])
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
    ('line', [((1.79952504534584, 1.9820908523069647, 0.0), (1.79952504534584, 1.6686944587899628, 0.0))]),
    ('arc', [((1.9995250453458402, 2.5040679344259122, 0.0), (1.5821382509401096, 3.254825623465323, 0.0), 2.39919897074878)]),
    ('line', [((1.5821382509401096, 3.254825623465323, 0.0), (1.5821382509401096, 3.074846581412386, 0.0))]),
    ('arc', [((1.99952504534584, 2.5040679344259122, 0.0), (1.5821382509401096, 3.074846581412386, 0.0), 1.5035170128434714)]),
    ('arc', [((1.47245761974255, 2.1517897951238485, 0.0), (1.401977410861636, 2.1259980671760434, 0.0), 3.3375383870207784)]),
    ('arc', [((1.9995250453458397, 2.5040679344259122, 0.0), (2.5221917667248683, 2.305877186356514, 0.0), 4.0989119043814854)]),
    ('arc', [((2.5932917703656937, 2.2819183177443403, 0.0), (2.5221917667248683, 2.305877186356514, 0.0), 3.1260360646671463)]),
    ('arc', [((1.99952504534584, 2.5040679344259122, 0.0), (2.6640104675776195, 2.2568563192695836, 0.0), 1.297475396617283)]),
    ('line', [((2.4169250453458404, 3.0771575426258417, 0.0), (2.41692504534584, 3.2548182816093734, 0.0))]),
    ('arc', [((1.9995250453458397, 2.504067934425912, 0.0), (2.19952504534584, 1.668694458789962, 0.0), 2.3991813809737663)]),
    ('line', [((2.19952504534584, 1.668694458789962, 0.0), (2.19952504534584, 1.9820908523069647, 0.0))]),
    ('arc', [((1.99952504534584, 2.504067934425909, 0.0), (1.79952504534584, 1.9820908523069647, 0.0), 0.7318082934870419)]),
]

profile_3_entities = [
    ('line', [((2.19952504534584, 1.668694458789962, 0.0), (2.19952504534584, 1.9820908523069647, 0.0))]),
    ('arc', [((1.99952504534584, 2.504067934425909, 0.0), (1.79952504534584, 1.9820908523069647, 0.0), 0.7318082934870419)]),
    ('line', [((1.79952504534584, 1.9820908523069647, 0.0), (1.79952504534584, 1.668694458789962, 0.0))]),
    ('arc', [((1.9995250453458397, 2.5040679344259122, 0.0), (1.4860438266699516, 3.1926794953680826, 0.0), 2.2658738527981552)]),
    ('line', [((1.4860438266699516, 3.1926794953680826, 0.0), (1.5499848028036456, 3.114273785606787, 0.0))]),
    ('arc', [((1.5112363293009832, 3.0826738520433534, 0.0), (1.5434833470386655, 3.0444622066060583, 0.0), 1.5539806322450316)]),
    ('arc', [((1.99952504534584, 2.5040679344259122, 0.0), (1.5434833470386655, 3.0444622066060583, 0.0), 1.4339701015339084)]),
    ('arc', [((1.47245761974255, 2.1517897951238485, 0.0), (1.401977410861636, 2.125998067176043, 0.0), 3.337538387020768)]),
    ('arc', [((1.9995250453458397, 2.504067934425912, 0.0), (2.5221917667248683, 2.305877186356514, 0.0), 4.0989119043814854)]),
    ('arc', [((2.5932917703656937, 2.2819183177443403, 0.0), (2.5221917667248683, 2.305877186356514, 0.0), 3.1260360646672174)]),
    ('arc', [((1.99952504534584, 2.5040679344259122, 0.0), (2.6640104675776217, 2.256856319269589, 0.0), 1.227320773978009)]),
    ('arc', [((2.488267494171766, 3.084742891694462, 0.0), (2.449825831973078, 3.116715358089815, 0.0), 1.5649341839123678)]),
    ('line', [((2.449825831973078, 3.116715358089815, 0.0), (2.513006264021728, 3.192679495368083, 0.0))]),
    ('arc', [((1.9995250453458406, 2.5040679344259122, 0.0), (2.19952504534584, 1.668694458789962, 0.0), 2.2658738527981566)]),
]

# BYU CMR BYUCMR_1012603 Ortho-Planar Spring. Link to model: https://www.printables.com/model/596315-ortho-planar-spring
profile_4_entities = [
    ('arc', [((-0.03108870371668105, 0.18478198915634916, 0.0), (-0.031088703716681088, 0.1926548291564475, 0.0), 0.9859561414205409)]),
    ('line', [((-0.03765308026568379, 0.189128317513716, 0.0), (-0.18439721020454758, -0.032503286482443716, 0.0))]),
    ('arc', [((-0.19096158675355035, -0.028156958125076726, 0.0), (-0.19752596330255312, -0.023810629767709743, 0.0), 3.1415926325163688)]),
    ('line', [((-0.19752596330255312, -0.023810629767709746, 0.0), (-0.04542303645745732, 0.20591450920813037, 0.0))]),
    ('arc', [((-0.03885865990845427, 0.20156818085076336, 0.0), (-0.04089718946656156, 0.2091725221705541, 0.0), 0.7240398975936291)]),
    ('line', [((-0.04089718946656156, 0.2091725221705541, 0.0), (0.07616560613928225, 0.24055406581526817, 0.0))]),
    ('arc', [((0.07820413569738922, 0.2329497244954776, 0.0), (0.085303096090031, 0.23635360037612502, 0.0), 1.3856077084835412)]),
    ('line', [((0.085303096090031, 0.23635360037612502, 0.0), (0.20603836650780283, -0.015446092880170015, 0.0))]),
    ('arc', [((0.1989394061151611, -0.018849968760817515, 0.0), (0.19184044572251935, -0.022253844641465022, 0.0), 3.141592653589793)]),
    ('line', [((0.19184044572251935, -0.022253844641464994, 0.0), (0.07849137887927053, 0.21414153643482736, 0.0))]),
    ('arc', [((0.07139241848662882, 0.2107376605541799, 0.0), (0.07849137887927053, 0.2141415364348274, 0.0), 1.5707963267949014)]),
    ('line', [((0.06798854260598129, 0.21783662094682157, 0.0), (0.04669166143801369, 0.2076249932974862, 0.0))]),
    ('arc', [((0.050095537318661176, 0.2005260329048445, 0.0), (0.04669166143801369, 0.2076249932974862, 0.0), 1.5707963267948954)]),
    ('line', [((0.04299657692601947, 0.197122157024197, 0.0), (0.15988668467688752, -0.04665824928464776, 0.0))]),
    ('arc', [((0.15007866431057318, -0.05136109056213984, 0.0), (0.14464005282446482, -0.06078104197870725, 0.0), 2.5414999645314484)]),
    ('line', [((0.14464005282446482, -0.06078104197870725, 0.0), (0.08100490352474991, -0.02412147352552138, 0.0))]),
    ('arc', [((0.08494132352479908, -0.017303394085505883, 0.0), (0.07738390734834419, -0.015097250299845702, 0.0), 1.3312230260674645)]),
    ('arc', [((-0.000611190395088182, -0.0007444300892393146, 0.0), (0.07738390734834419, -0.01509725029984568, 0.0), 1.4170953417143883)]),
    ('arc', [((0.02884827478516348, 0.0828725916541765, 0.0), (0.019508498016636042, 0.08236552614147867, 0.0), 1.1519783866775843)]),
    ('line', [((0.019508498016636053, 0.08236552614147867, 0.0), (0.01968210000024612, 0.1847819891563492, 0.0))]),
    ('arc', [((0.01180926000014788, 0.18478198915634916, 0.0), (0.01968210000024612, 0.1847819891563492, 0.0), 1.570796326794915)]),
    ('line', [((0.01180926000014771, 0.1926548291564474, 0.0), (-0.03108870371668109, 0.1926548291564475, 0.0))]),
    ('circle', [((0.0, 0.0, 0.0), 0.2855966862072149)]),
    ('line', [((0.0628169100540586, -0.05906522144272293, 0.0), (0.1501848467601301, -0.109436193153204, 0.0))]),
    ('arc', [((0.1541212667649642, -0.10261811370840354, 0.0), (0.1501848467601301, -0.10943619315320399, 0.0), 1.5707963267949014)]),
    ('line', [((0.1609393462097647, -0.1065545337132376, 0.0), (0.1811322551608539, -0.07157938946159374, 0.0))]),
    ('arc', [((0.17424008891307463, -0.06764013445500039, 0.0), (0.1811322551608539, -0.07157938946159374, 0.0), 0.9619895521206667)]),
    ('line', [((0.1814131361432743, -0.0642390935808968, 0.0), (0.06385664515609714, 0.18093108969155394, 0.0))]),
    ('arc', [((0.07094962941137693, 0.18434742909538632, 0.0), (0.07805456592493987, 0.18773884144219188, 0.0), 3.1451040172353193)]),
    ('line', [((0.07805456592493985, 0.18773884144219188, 0.0), (0.2012424260129711, -0.06691316898403421, 0.0))]),
    ('arc', [((0.1944784896161242, -0.07028495008759908, 0.0), (0.2017595525748424, -0.07231124364533674, 0.0), 0.7338702624799766)]),
    ('line', [((0.2017595525748424, -0.07231124364533674, 0.0), (0.17171897286889792, -0.18703985989476063, 0.0))]),
    ('arc', [((0.16410288589985025, -0.18504566110783482, 0.0), (0.16350156213556533, -0.192895503096842, 0.0), 1.3911592165597466)]),
    ('line', [((0.16350156213556533, -0.192895503096842, 0.0), (-0.11720707229726846, -0.1713922966002383, 0.0))]),
    ('arc', [((-0.11660574853016674, -0.1635424546021935, 0.0), (-0.11600442476306502, -0.15569261260414868, 0.0), 3.141592638688632)]),
    ('line', [((-0.11600442476306502, -0.15569261260414868, 0.0), (0.1453953137625366, -0.17571669405254833, 0.0))]),
    ('arc', [((0.14599663752963832, -0.16786685205450347, 0.0), (0.1453953137625366, -0.17571669405254833, 0.0), 1.5707963267948966)]),
    ('line', [((0.15384647952768318, -0.1684681758216052, 0.0), (0.15565045082714452, -0.14491864980892882, 0.0))]),
    ('arc', [((0.14780060882909973, -0.14431732604182698, 0.0), (0.15565045082714452, -0.14491864980892882, 0.0), 1.570796326794914)]),
    ('line', [((0.14840193259620144, -0.1364674840437822, 0.0), (-0.1239069763823219, -0.11560772421111448, 0.0))]),
    ('arc', [((-0.1181905079215667, -0.10527425383140777, 0.0), (-0.1239069763823221, -0.09494078345170116, 0.0), 2.1310003342239363)]),
    ('line', [((-0.12390697638232209, -0.09494078345170116, 0.0), (-0.05974950656257179, -0.05956114203349791, 0.0))]),
    ('arc', [((-0.05684868216066117, -0.06497190998072805, 0.0), (-0.05354540560564082, -0.059797013267696375, 0.0), 1.0602503303189397)]),
    ('arc', [((-0.0006111903950886052, -0.0007444300892395089, 0.0), (-0.05354540560564083, -0.05979701326769635, 0.0), 1.4764359441326371)]),
    ('arc', [((0.057933119651816974, -0.07078833895869026, 0.0), (0.06281691005405858, -0.05906522144272292, 0.0), 0.7773876618315902)]),
    ('circle', [((0.0, 0.0, 0.0), 0.03936420000049205)]),
    ('arc', [((0.12185499063713819, -0.15343476703952302, 0.0), (0.12125366687003641, -0.16128460903756783, 0.0), 3.141592653589793)]),
    ('line', [((-0.1588515128044926, -0.1398183900008301, 0.0), (0.12125366687003641, -0.16128460903756783, 0.0))]),
    ('arc', [((-0.15787125944422956, -0.1320068144224437, 0.0), (-0.16334795923017367, -0.13766255213929252, 0.0), 0.6444822567520757)]),
    ('line', [((-0.2455450176311016, -0.058067522310820435, 0.0), (-0.16334795923017367, -0.13766255213929252, 0.0))]),
    ('arc', [((-0.24006831784515748, -0.0524117845939714, 0.0), (-0.24663269439416025, -0.04806545623660452, 0.0), 1.3863195077547286)]),
    ('line', [((-0.08880753209604324, 0.1903021287615782, 0.0), (-0.24663269439416025, -0.04806545623660452, 0.0))]),
    ('arc', [((-0.08224315545457232, 0.18595580054606456, 0.0), (-0.07567877890469343, 0.18160947219221701, 0.0), 3.1415926833921155)]),
    ('line', [((-0.22041151320110308, -0.03698426688184063, 0.0), (-0.07567877890469343, 0.18160947219221701, 0.0))]),
    ('arc', [((-0.21384713665474392, -0.0413305952348118, 0.0), (-0.22041151320110308, -0.03698426688184063, 0.0), 1.570796326794898)]),
    ('line', [((-0.1985003353484105, -0.06093395687327067, 0.0), (-0.21819346500771508, -0.04789497178117097, 0.0))]),
    ('arc', [((-0.19415400699543942, -0.05436958032691146, 0.0), (-0.1985003353484105, -0.06093395687327068, 0.0), 1.5707963267948946)]),
    ('line', [((-0.04133792482389785, 0.1621719736920354, 0.0), (-0.18758963044908017, -0.05871590867988258, 0.0))]),
    ('arc', [((-0.03149136000039363, 0.15565248115598496, 0.0), (-0.01968210000024595, 0.1556524811559851, 0.0), 2.556752468215423)]),
    ('line', [((-0.01985570198385589, 0.08236552614147871, 0.0), (-0.01968210000024595, 0.1556524811559851, 0.0))]),
    ('arc', [((-0.028406764814254092, 0.08259996256339588, 0.0), (-0.025860410458509772, 0.07443346297909902, 0.0), 1.2411356771439337)]),
    ('arc', [((-0.000611190395088626, -0.0007444300892395488, 0.0), (-0.025860410458509765, 0.07443346297909902, 0.0), 1.4618380250357972)]),
    ('arc', [((-0.08633788951848635, -0.018302475084079513, 0.0), (-0.0811281356889296, -0.024729374172540536, 0.0), 0.9662758355780883)]),
    ('line', [((-0.17057240983010435, -0.07409765774772661, 0.0), (-0.0811281356889296, -0.024729374172540536, 0.0))]),
    ('arc', [((-0.1667614308436042, -0.08098663800556828, 0.0), (-0.17057240983010435, -0.07409765774772661, 0.0), 1.5707963273747194)]),
    ('line', [((-0.15369311392984852, -0.12087376095575028, 0.0), (-0.17365041109923618, -0.08479761699606282, 0.0))]),
    ('arc', [((-0.14680413368012132, -0.11706278199693329, 0.0), (-0.15369311392984852, -0.12087376095575028, 0.0), 0.9890461838478235)]),
    ('line', [((0.12245631440423996, -0.1455849250414782, 0.0), (-0.1474054574578981, -0.12491262398387529, 0.0))]),
]

#TODO: Add additional profile entities here:
# profile_2_entities = []


# The goal is to have a library of predefined flexture profiles that can be centered and scaled to fit on an extruded-cut profile. 
profiles = {
    'Circular': {
        '1st Flexure': profile_1_entities,
        '2nd Flexure': profile_2_entities,
        '3rd Flexure': profile_3_entities,
        'Ortho Planar Spring': profile_4_entities
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
        
        standardDiameter = 1.0  # This should match your reference profile edge diameter
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

        #TODO: Fix Centroid calculation and placement for Profile 2. Works correctly for Profile 1.
        offsetX = profileCentroid.x
        offsetY = profileCentroid.y

        # Add entities for the selected profile
        # sketch = addSketchEntities(sketch, profiles[selectedCategory][selectedProfile], offsetX, offsetY)
        addScaledSketchEntities(sketch, profiles[selectedCategory][selectedProfile], offsetX, offsetY, scaleFactor)
        
        # Notify the user
        ui.messageBox('The sketch centered on the selected profile has been created successfully.')

        # Notify the user
        ui.messageBox('The sketch has been scaled successfully.')


    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

run()
