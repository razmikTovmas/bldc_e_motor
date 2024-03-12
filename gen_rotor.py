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


def calculate_pattern_radius(base_radius: float,
                             base_height: float,
                             height: float):
    # (base_height + x) ** 2 + base_radius ** 2 == (height + x) ** 2
    # x = ?
    x = (base_radius ** 2 + base_height ** 2 - height ** 2) / (2 * (height - base_height))
    radius = x + height
    return radius

def create_rotor(rotor_radius_inner,
                 stator_height,
                 rotor_thickness,
                 bearing_radius_inner,
                 num_of_magnets,
                 magnet_height,
                 magnet_width,
                 magnet_thickness,
                 file_name: str):
    rotor_radius_outer = rotor_radius_inner + rotor_thickness
    rotor_height = stator_height + rotor_thickness
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=rotor_radius_outer,
                                        depth=rotor_height,
                                        location=(0, 0, rotor_height / 2))
    rotor = bpy.context.selected_objects[0]

    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=rotor_radius_inner,
                                        depth=rotor_height,
                                        location=(0, 0, rotor_height / 2))
    differ = bpy.context.selected_objects[0]
    bool_modifier(rotor, differ, 'DIFFERENCE')

    ####
    # pattern
    # need to implement
    pattern_height = 5.0
    sphere_radius_outer = calculate_pattern_radius(rotor_radius_outer, rotor_height, rotor_height + pattern_height)
    # sphere_radius_inner = calculate_pattern_radius(rotor_radius_inner, rotor_height, rotor_height + pattern_height)
    sphere_radius_inner = sphere_radius_outer - rotor_thickness
    sphere_center_z = rotor_height + pattern_height - sphere_radius_outer
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        # radius=sphere_radius_outer + 10,
                                        radius=sphere_radius_outer,
                                        depth=sphere_radius_outer * 2,
                                        location=(0, 0, sphere_center_z))
    big_cyl = bpy.context.selected_objects[0]
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=rotor_radius_outer,
                                        depth=sphere_radius_outer * 2,
                                        location=(0, 0, sphere_center_z))
    differ = bpy.context.selected_objects[0]
    bool_modifier(big_cyl, differ, 'DIFFERENCE')
    outer_differ = big_cyl

    bpy.ops.mesh.primitive_uv_sphere_add(segments=128,
                                         ring_count=32,
                                         radius=sphere_radius_outer,
                                         location=(0.0, 0.0, sphere_center_z))
    outer_sphere = bpy.context.selected_objects[0]
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128,
                                         ring_count=32,
                                         radius=sphere_radius_inner,
                                         location=(0.0, 0.0, sphere_center_z))
    inner_sphere = bpy.context.selected_objects[0]
    bool_modifier(outer_sphere, inner_sphere, 'DIFFERENCE')
    pattern_sphere = outer_sphere
    bool_modifier(pattern_sphere, outer_differ, 'DIFFERENCE')
    # pattern_sphere = bpy.context.selected_objects[0]
    bpy.data.objects.remove(outer_differ, do_unlink=True)
    # rotor + pattern_sphere

    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        radius=bearing_radius_inner,
                                        depth=rotor_height + pattern_height,
                                        location=(0, 0, (rotor_height + pattern_height) / 2))
    differ = bpy.context.selected_objects[0]
    bool_modifier(pattern_sphere, differ, 'DIFFERENCE')

    bpy.ops.mesh.primitive_cylinder_add(vertices=128,
                                        # radius=rotor_radius_outer + 10,
                                        radius=sphere_radius_outer,
                                        depth=sphere_radius_outer,
                                        location=(0, 0, sphere_center_z - sphere_radius_outer))
    big_cyl = bpy.context.selected_objects[0]
    bool_modifier(pattern_sphere, big_cyl, 'DIFFERENCE')

    # ctx = bpy.context.copy()
    # ctx['active_object'] = rotor
    # ctx['selected_editable_objects'] = [pattern_sphere]
    # bpy.ops.object.join(ctx)
    # rotor = bpy.data.objects[0]
    # bool_modifier(rotor, pattern_sphere, 'UNION')
    ####

    # if num_of_magnets:
    #     rotation_angle = int(360 / num_of_magnets)
    #     magnet_radius = rotor_radius_inner
    #     for z_angle in range(0, 360, rotation_angle):
    #         loc_x = math.sin(math.radians(-z_angle)) * magnet_radius
    #         loc_y = math.cos(math.radians(-z_angle)) * magnet_radius
    #         bpy.ops.mesh.primitive_cube_add(size=1.0,
    #                                         location=(loc_x, loc_y, stator_height / 2),
    #                                         scale=(magnet_width, magnet_thickness * 2, magnet_height),
    #                                         rotation=(0.0, 0.0, math.radians(z_angle)))
    #         bool_modifier(rotor, bpy.context.selected_objects[0], 'DIFFERENCE')

    bpy.ops.export_mesh.stl(filepath=file_name, use_selection=False)


def main():
    with open('config.json') as CFG:
        config = json.load(CFG)

    stator_radius = config['stator_radius']
    stator_height = config['stator_height']
    rotor_thickness = config['rotor_thickness']
    bearing_radius_inner = config['bearing_radius_inner']
    num_of_magnets = config['num_of_magnets']
    magnet_height = config['magnet_height']
    magnet_width = config['magnet_width']
    magnet_thickness = config['magnet_thickness']
    file_name = config['rotor_path']

    create_rotor(stator_radius + 0.5, stator_height + 0.5, rotor_thickness,
                 bearing_radius_inner, num_of_magnets, magnet_height,
                 magnet_width, magnet_thickness, file_name)


if __name__ == '__main__':
    main()
