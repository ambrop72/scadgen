import itertools
from spacemath import *


class Object(object):
    pass

class PrimitiveObject(Object):
    pass

class ComposedObject(Object):
    def __init__(self, children):
        assert all(isinstance(child, Object) for child in children), "A child of a composed object is not an object."
        
        self._children = [child for child in children]
    
    def child(self, index=0, context=None):
        index = _int_arg(index)
        assert 0 <= index < len(self._children), "Invalid child index."
        
        return ChildProxy(self, index, context)
    
    def get_child_transform(self, index):
        index = _int_arg(index)
        assert 0 <= index < len(self._children), "Invalid child index."
        
        if hasattr(self, 'get_child_transform_impl'):
            return self.get_child_transform_impl(index)
        else:
            return Mat4.ID
    
    def _openscad_child_ops(self):
        return [child._openscad_operation() for child in self._children]
    
    def _openjscad_child_ops(self):
        return [child._openjscad_operation() for child in self._children]

class ChildProxy(object):
    def __init__(self, parent, index, context):
        self._parent = parent
        self._index = index
        self._context = context
    
    def obj(self):
        return self._parent._children[self._index]
    
    def child(self, index=0):
        return self.obj().child(index, self)
    
    def get_transform(self):
        matrix = self._parent.get_child_transform(self._index)
        if self._context is not None:
            matrix = self._context.get_transform() * matrix
        return matrix
    
    def __getattr__(self, name):
        att = getattr(self.obj(), name)
        if not callable(att):
            return att
        def func(*args, **kwargs):
            res = att(*args, **kwargs)
            if hasattr(res, 'transform'):
                res = res.transform(self.get_transform())
            return res
        return func

class Cube(PrimitiveObject):
    def __init__(self, size, center_x=False, center_y=False, center_z=False, center=False):
        size = _vec3_arg(size)
        center_x = _bool_arg(center_x)
        center_y = _bool_arg(center_y)
        center_z = _bool_arg(center_z)
        center = _bool_arg(center)
        
        if center:
            center_x = True
            center_y = True
            center_z = True
        
        self._size = size
        self._centered = (center_x, center_y, center_z)
        self._offset = Vec3(
            -size.x/2 if center_x else 0.0,
            -size.y/2 if center_y else 0.0,
            -size.z/2 if center_z else 0.0
        )
        self._has_offset = (center_x or center_y or center_z)
    
    def left_center(self):
        return Vec3(self._dim_min(0), self._dim_center(1), self._dim_center(2))
    
    def right_center(self):
        return Vec3(self._dim_max(0), self._dim_center(1), self._dim_center(2))
    
    def front_center(self):
        return Vec3(self._dim_center(0), self._dim_min(1), self._dim_center(2))
    
    def back_center(self):
        return Vec3(self._dim_center(0), self._dim_max(1), self._dim_center(2))
    
    def bottom_center(self):
        return Vec3(self._dim_center(0), self._dim_center(1), self._dim_min(2))
    
    def top_center(self):
        return Vec3(self._dim_center(0), self._dim_center(1), self._dim_max(2))
    
    def left_front_bottom(self):
        return Vec3(self._dim_min(0), self._dim_min(1), self._dim_min(2))
    
    def right_front_bottom(self):
        return Vec3(self._dim_max(0), self._dim_min(1), self._dim_min(2))
    
    def left_back_bottom(self):
        return Vec3(self._dim_min(0), self._dim_max(1), self._dim_min(2))
    
    def right_back_bottom(self):
        return Vec3(self._dim_max(0), self._dim_max(1), self._dim_min(2))
    
    def left_front_top(self):
        return Vec3(self._dim_min(0), self._dim_min(1), self._dim_max(2))
    
    def right_front_top(self):
        return Vec3(self._dim_max(0), self._dim_min(1), self._dim_max(2))
    
    def left_back_top(self):
        return Vec3(self._dim_min(0), self._dim_max(1), self._dim_max(2))
    
    def right_back_top(self):
        return Vec3(self._dim_max(0), self._dim_max(1), self._dim_max(2))
    
    def _dim_min(self, dim):
        return -self._size[dim]/2 if self._centered[dim] else 0.0
    
    def _dim_center(self, dim):
        return 0.0 if self._centered[dim] else self._size[dim]/2
    
    def _dim_max(self, dim):
        return self._size[dim]/2 if self._centered[dim] else self._size[dim]
    
    def _openscad_operation(self):
        op = OpenscadOperation('cube', [self._size], {})
        if self._has_offset:
            op = OpenscadOperation('translate', [self._offset], {}, [op])
        return op
    
    def _openjscad_operation(self):
        op = OpenjsscadOperation('cube', kw_args={'size':self._size})
        if self._has_offset:
            op = OpenjsscadOperation('translate', pos_args=[self._offset], inputs=[op], is_method=True)
        return op

class Cylinder(PrimitiveObject):
    def __init__(self, h, r=None, r1=None, r2=None, fn=32):
        h = _float_arg(h)
        r = _float_arg(r, allow_none=True)
        r1 = _float_arg(r1, allow_none=True)
        r2 = _float_arg(r2, allow_none=True)
        fn = _int_arg(fn)
        
        if r is not None:
            assert r1 is None and r2 is None, "If 'r' is given then 'r1' and 'r2' must not be given."
            r1 = r
            r2 = r
        else:
            assert r1 is not None and r2 is not None, "If either 'r1' or 'r2' is given then both must be."
        
        self._h = h
        self._r1 = r1
        self._r2 = r2
        self._fn = fn
    
    def bottom_center(self):
        return Vec3(0.0, 0.0, 0.0)
    
    def top_center(self):
        return Vec3(0.0, 0.0, self._h)
    
    def _openscad_operation(self):
        return OpenscadOperation('cylinder', [], {'h':self._h, 'r1':self._r1, 'r2':self._r2, '$fn':self._fn})
    
    def _openjscad_operation(self):
        return OpenjsscadOperation('cylinder', kw_args={'h':self._h, 'r1':self._r1, 'r2':self._r2, 'fn':self._fn})

class Sphere(PrimitiveObject):
    def __init__(self, r, fn=32):
        r = _float_arg(r)
        fn = _int_arg(fn)
        
        self._r = r
        self._fn = fn
    
    def _openscad_operation(self):
        return OpenscadOperation('sphere', [], {'r':self._r, '$fn':self._fn})
    
    def _openjscad_operation(self):
        return OpenjsscadOperation('sphere', kw_args={'r':self._r, 'fn':self._fn})

class Union(ComposedObject):
    def __init__(self, children):
        ComposedObject.__init__(self, children)
    
    def _openscad_operation(self):
        return OpenscadOperation('union', [], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        return OpenjsscadOperation('union', inputs=self._openjscad_child_ops())

class Intersection(ComposedObject):
    def __init__(self, children):
        ComposedObject.__init__(self, children)
    
    def _openscad_operation(self):
        return OpenscadOperation('intersection', [], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        return OpenjsscadOperation('intersection', inputs=self._openjscad_child_ops())

class Difference(ComposedObject):
    def __init__(self, children):
        ComposedObject.__init__(self, children)
    
    def _openscad_operation(self):
        return OpenscadOperation('difference', [], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        return OpenjsscadOperation('difference', inputs=self._openjscad_child_ops())

class Minkowski(ComposedObject):
    def __init__(self, children):
        ComposedObject.__init__(self, children)
    
    def get_child_transform_impl(self, index):
        raise ValueError('Transform matrix for Minkowski not defined yet.')
    
    def _openscad_operation(self):
        return OpenscadOperation('minkowski', [], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        raise ValueError('OpenJSCAD does not support Minkowski.')

class Hull(ComposedObject):
    def __init__(self, children):
        ComposedObject.__init__(self, children)
    
    def get_child_transform_impl(self, index):
        raise ValueError('Transform matrix for Hull not defined yet.')
    
    def _openscad_operation(self):
        return OpenscadOperation('hull', [], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        raise ValueError('OpenJSCAD does not support Hull.')

class Translate(ComposedObject):
    def __init__(self, offset, children):
        ComposedObject.__init__(self, children)
        assert len(self._children) == 1, "A single child object must be given."
        offset = _vec3_arg(offset)
        
        self._offset = offset
    
    def get_child_transform_impl(self, index):
        return Mat4.new_translate(self._offset)
    
    def _openscad_operation(self):
        return OpenscadOperation('translate', [self._offset], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        return OpenjsscadOperation('translate', pos_args=[self._offset], inputs=self._openjscad_child_ops(), is_method=True)

class Mirror(ComposedObject):
    def __init__(self, plane, children):
        ComposedObject.__init__(self, children)
        assert len(self._children) == 1, "A single child object must be given."
        plane = _vec3_arg(plane)
        
        self._plane = plane
    
    def get_child_transform_impl(self, index):
        return Mat4.new_householder(self._plane)
    
    def _openscad_operation(self):
        return OpenscadOperation('mirror', [self._plane], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        matrix = Mat4.new_householder(self._plane)
        return OpenjsscadOperation('transform', pos_args=[matrix], inputs=self._openjscad_child_ops(), is_method=True)

class Transform(ComposedObject):
    def __init__(self, matrix, children):
        ComposedObject.__init__(self, children)
        assert len(self._children) == 1, "A single child object must be given."
        matrix = _mat4_arg(matrix)
        
        self._matrix = matrix
    
    def get_child_transform_impl(self, index):
        return self._matrix
    
    def _openscad_operation(self):
        return OpenscadOperation('multmatrix', [self._matrix], {}, self._openscad_child_ops())
    
    def _openjscad_operation(self):
        return OpenjsscadOperation('transform', pos_args=[self._matrix], inputs=self._openjscad_child_ops(), is_method=True)


class OpenscadOperation(object):
    def __init__(self, name, pos_args, kw_args, inputs=None):
        self._name = name
        self._pos_args = pos_args
        self._kw_args = kw_args
        self._inputs = inputs
    
    def build(self, indent):
        istr = '    ' * indent
        kw_args_sorted = [(key, self._kw_args[key]) for key in sorted(self._kw_args)]
        args_str = ', '.join(itertools.chain((_val_to_openscad(val) for val in self._pos_args), ('{}={}'.format(key, _val_to_openscad(val)) for (key, val) in kw_args_sorted)))
        if self._inputs is None:
            return '{}{}({});\n'.format(istr, self._name, args_str)
        else:
            inputs_str = ''.join(inp.build((indent + 1)) for inp in self._inputs)
            return '{}{}({}) {{\n{}{}}}\n'.format(istr, self._name, args_str, inputs_str, istr)

class OpenjsscadOperation(object):
    def __init__(self, name, pos_args=None, kw_args=None, inputs=None, is_method=False):
        assert sum((pos_args is not None, kw_args is not None)) <= 1
        assert not is_method or len(inputs) == 1
        self._name = name
        self._pos_args = pos_args
        self._kw_args = kw_args
        self._inputs = inputs
        self._is_method = is_method
    
    def build(self, indent):
        istr = '    ' * indent
        args_str = ''
        if self._pos_args is not None:
            args_str = ', '.join(_val_to_openjscad(val) for val in self._pos_args)
        elif self._kw_args is not None:
            kw_args_sorted = [(key, self._kw_args[key]) for key in sorted(self._kw_args)]
            args_str = '{{{}}}'.format(', '.join('{}: {}'.format(key, _val_to_openjscad(val)) for (key, val) in kw_args_sorted))
        if self._is_method:
            return '{}.{}({})'.format(self._inputs[0].build(indent + 1), self._name, args_str)
        else:
            if self._inputs is None:
                return '{}({})'.format(self._name, args_str)
            else:
                inputs_str = ', '.join(inp.build((indent + 1)) for inp in self._inputs)
                if args_str != '':
                    return '{}({}, {})'.format(self._name, args_str, inputs_str)
                else:
                    return '{}({})'.format(self._name, inputs_str)


def build_output(obj, fmt):
    if fmt == 'openscad':
        res = obj._openscad_operation().build(0)
    elif fmt == 'openjscad':
        res = 'function main() {{\n    return (\n{}\n    );\n}}'.format(obj._openjscad_operation().build(2))
    else:
        raise ValueError('Unknown output format: {}.'.format(fmt))
    return res


def _val_to_openscad(val):
    if isinstance(val, Vec3):
        return '[{}]'.format(', '.join(_number_to_openscad(val[i]) for i in range(3)))
    if isinstance(val, Mat4):
        return '[{}]'.format(', '.join( '[{}]'.format(', '.join(_number_to_openscad(val.at(i, j)) for j in range(4))) for i in range(4)))
    if type(val) is bool:
        return 'true' if val else 'false'
    if type(val) is int or type(val) is long:
        return str(val)
    if type(val) is float:
        return _number_to_openscad(val)
    raise TypeError()

def _number_to_openscad(val):
    return '{:.9E}'.format(val)

def _val_to_openjscad(val):
    if isinstance(val, Vec3):
        return '[{}]'.format(', '.join(_number_to_openjscad(val[i]) for i in range(3)))
    if isinstance(val, Mat4):
        return 'new CSG.Matrix4x4([{}])'.format(', '.join(_number_to_openjscad(val.at(i, j)) for j in range(4) for i in range(4)))
    if type(val) is bool:
        return 'true' if val else 'false'
    if type(val) is int or type(val) is long:
        return str(val)
    if type(val) is float:
        return _number_to_openjscad(val)
    raise TypeError()

def _number_to_openjscad(val):
    return '{:.9E}'.format(val)

def _bool_arg(x):
    assert type(x) is bool, "Argument must be a bool."
    return x

def _int_arg(x, allow_none=False):
    if x is None:
        assert allow_none, "Argument must be provided."
        return None
    assert type(x) is int or type(x) is long, "Argument must be an integer."
    return x

def _float_arg(x, allow_none=False):
    if x is None:
        assert allow_none, "Argument must be provided."
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        assert False, "Argument must be convertible to float."
    return f

def _vec3_arg(x, allow_none=False):
    if x is None:
        assert allow_none, "Argument must be provided."
        return None
    assert type(x) is Vec3, "Argument must be a Vec3."
    return x

def _mat4_arg(x, allow_none=False):
    if x is None:
        assert allow_none, "Argument must be provided."
        return None
    assert type(x) is Mat4, "Argument must be a Mat4."
    return x

