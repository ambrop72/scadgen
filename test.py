from scadgen import *

def model():
    local_x = Vec3(0,20,3).normalize()
    local_y = (Vec3.Z*2).orthonormalize(local_x)
    local_z = local_x.cross(local_y)
    local_origin = Vec3(3, -6, -1.5)
    
    return Union([
        Union([
            Translate(-Vec3.Y*6.0, [
                Cube(Vec3(6, 20, 3), center_x=True, center_z=True)
            ]),
            Cylinder(h=8, r=3)
        ]),
        Transform(Mat4.new_base(local_x, local_y, local_z, local_origin), [
            Cube(Vec3(2,2,2), center_x=True, center_y=True)
        ])
    ])
