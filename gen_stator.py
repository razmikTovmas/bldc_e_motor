import json
import bpy
import math


def bool_modifier(main, other, action, op_type='OBJECT'):
    if action not in ('DIFFERENCE', 'INTERSECT', 'UNION'):
        return
    if op_type not in ('OBJECT', 'COLLECTION'):
        return
    bpy.context.view_layer.objects.active = main
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers['Boolean'].operation = action
    bpy.context.object.modifiers['Boolean'].operand_type = op_type
    bpy.context.object.modifiers['Boolean'].use_self = True
    bpy.context.object.modifiers['Boolean'].object = other
    bpy.ops.object.modifier_apply({'object': main}, modifier='Boolean')
    bpy.ops.object.delete()


def create_stator(num_of_legs: int,
                  radius: float,
                  height: float,
                  thickness: float,
                  bearing_radius_outter: float,
                  bearing_radius_inner: float,
                  bearing_height: float,
                  bearing_wall_thickness: float,
                  number_of_holes: int,
                  holes_radius: float,
                  hole_depth: float,
                  file_name: str):
    rotation_angle = int(360 / num_of_legs)
    # legs
    cubes = []
    for z_angle in range(0, 360, rotation_angle):
        loc_x = math.sin(math.radians(-z_angle)) * radius / 2
        loc_y = math.cos(math.radians(-z_angle)) * radius / 2
        bpy.ops.mesh.primitive_cube_add(size=1.0,
                                        location=(loc_x, loc_y, height / 2),
                                        scale=(thickness, radius, height),
                                        rotation=(0.0, 0.0, math.radians(z_angle)))
        cubes.append(bpy.context.selected_objects[0])

    # ...
    objs = []
    for z_angle in range(0, 360, rotation_angle):
        loc_x = math.sin(math.radians(-z_angle)) * radius
        loc_y = math.cos(math.radians(-z_angle)) * radius
        bpy.ops.mesh.primitive_cube_add(size=1.0,
                                        location=(loc_x, loc_y, height / 2),
                                        scale=(thickness + 5.0, 5.0, height),
                                        rotation=(0.0, 0.0, math.radians(z_angle)))
        objs.append(bpy.context.selected_objects[0])

    # Join objects
    scene = bpy.context.scene
    ctx = bpy.context.copy()
    ctx['active_object'] = bpy.data.objects[0]
    ctx['selected_editable_objects'] = cubes + objs
    bpy.ops.object.join(ctx)
    stator = bpy.data.objects[0]

    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=radius,
                                        depth=height,
                                        location=(0, 0, height / 2))
    differ = bpy.context.selected_objects[0]
    bool_modifier(stator, differ, 'INTERSECT')

    # bearing walls - bearing_wall_thickness
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=bearing_radius_outter + bearing_wall_thickness,
                                        depth=height,
                                        location=(0, 0, height / 2))
    bearing = bpy.context.selected_objects[0]
    bool_modifier(stator, bearing, 'UNION')

    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=bearing_radius_outter,
                                        depth=bearing_height,
                                        location=(0, 0, bearing_height / 2))
    bearing = bpy.context.selected_objects[0]
    bool_modifier(stator, bearing, 'DIFFERENCE')

    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=bearing_radius_inner,
                                        depth=height - bearing_height,
                                        location=(0, 0, bearing_height + (height - bearing_height) / 2))
    bearing_upper = bpy.context.selected_objects[0]
    bool_modifier(stator, bearing_upper, 'DIFFERENCE')

    if number_of_holes:
        hole_loc_radius = radius - hole_depth / 2
        for z_angle in range(0, 360, rotation_angle):
            loc_x = math.sin(math.radians(-z_angle)) * hole_loc_radius
            loc_y = math.cos(math.radians(-z_angle)) * hole_loc_radius
            rot_x = math.radians(-90 - z_angle)
            rot_y = math.radians(90)
            rot_z = 0
            for i in range(number_of_holes):
                loc_z = height / number_of_holes * i + height / number_of_holes / 2
                bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                                    radius=holes_radius,
                                                    depth=hole_depth,
                                                    location=(loc_x, loc_y, loc_z),
                                                    rotation=(rot_x, rot_y, rot_z))
                hole = bpy.context.selected_objects[0]
                bool_modifier(stator, hole, 'DIFFERENCE')

    bpy.ops.export_mesh.stl(filepath=file_name, use_selection=False)


def main():
    with open('config.json') as CFG:
        config = json.load(CFG)

    num_of_legs = config['num_of_legs']
    radius = config['stator_radius']
    height = config['stator_height']
    thickness = config['thickness']
    bearing_radius_outer = config['bearing_radius_outer']
    bearing_radius_inner = config['bearing_radius_inner']
    bearing_height = config['bearing_height']
    bearing_wall_thickness = config['bearing_wall_thickness']
    number_of_holes = config['number_of_holes']
    holes_radius = config['holes_radius']
    hole_depth = config['hole_depth']
    file_name = 'stator.stl'

    create_stator(num_of_legs,
                  radius,
                  height,
                  thickness,
                  bearing_radius_outer,
                  bearing_radius_inner,
                  bearing_height,
                  bearing_wall_thickness,
                  number_of_holes,
                  holes_radius,
                  hole_depth,
                  file_name)


if __name__ == '__main__':
    main()
