from scadgen import *

def model():
    local_x = Vec3(0,20,3).normalize()
    local_z = (Vec3.Z*2).orthonormalize(local_x)
    local_y = local_z.cross(local_x)
    local_origin = Vec3(3, -6, -1.5)
    
    obj = Union([
        Union([
            Translate(-Vec3.Y*6.0, [
                Cube(Vec3(6, 20, 3), center_x=True, center_z=True)
            ]),
            Translate(Vec3(0,6,0), [
                Cylinder(h=8, r=3)
            ])
        ]),
        Transform(Mat4.new_base(local_x, local_y, local_z, local_origin), [
            Cube(Vec3(2,3,5), center_x=True, center_y=True)
        ])
    ])
    
    # Coordinates obtained from child objects are automagically transformed.
    return Union([
        obj,
        Translate(obj.child(1).child().bottom_center(), [Sphere(r=0.3)]),
        Translate(obj.child(1).child().right_center(), [Sphere(r=0.5)]),
        Translate(obj.child(1).child().left_front_bottom(), [Sphere(r=0.5)]),
        Translate(obj.child(0).child(0).child().top_center(), [Sphere(r=0.5)]),
        Translate(obj.child(0).child(1).child().top_center(), [Sphere(r=0.5)]),
        Translate(obj.child(0).child(0).child().center(), [Sphere(r=5)])
    ])

