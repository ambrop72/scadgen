import math
import itertools
import operator


class Vec3(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, v=None):
        if v is not None:
            self._v = v
        else:
            self._v = [float(x), float(y), float(z)]
    
    @staticmethod
    def new_fromfunc(func):
        return Vec3(v=[float(func(i)) for i in range(3)])
    
    def __repr__(self):
        return 'Vec3({}, {}, {})'.format(self._v[0], self._v[1], self._v[2])
    
    @property
    def x(self):
        return self._v[0]
    
    @property
    def y(self):
        return self._v[1]
    
    @property
    def z(self):
        return self._v[2]
    
    def __getitem__(self, index):
        return self._v[index]
    
    def elementwise(self, func, other):
        assert isinstance(other, Vec3) or type(other) is float or type(other) is int or type(other) is long
        if isinstance(other, Vec3):
            return Vec3(v=[(func(a, b)) for (a, b) in itertools.izip(self._v, other._v)])
        else:
            other = float(other)
            return Vec3(v=[func(a, other) for a in self._v])
    
    def __add__(self, other):
        return self.elementwise(operator.add, other)
    
    def __sub__(self, other):
        return self.elementwise(operator.sub, other)
    
    def __mul__(self, other):
        return self.elementwise(operator.mul, other)
    
    def __div__(self, other):
        return self.elementwise(operator.truediv, other)
    
    def __neg__(self):
        return Vec3(v=[-a for a in self._v])
    
    def length(self):
        return math.sqrt(sum((a * a) for a in self._v))
    
    def normalize(self):
        return self / self.length()
    
    def dot(self, other):
        assert isinstance(other, Vec3)
        return sum((a * b) for (a, b) in itertools.izip(self._v, other._v))
    
    def projected(self, other):
        assert isinstance(other, Vec3)
        return other * (self.dot(other) / other.dot(other))
    
    def orthonormalize(self, other):
        assert isinstance(other, Vec3)
        return (self - self.projected(other)).normalize()
    
    def cross(self, other):
        return Vec3(
            self[1] * other[2] - self[2] * other[1],
            self[2] * other[0] - self[0] * other[2],
            self[0] * other[1] - self[1] * other[0]
        )
    
    def transform(self, matrix):
        assert isinstance(matrix, Mat4)
        return matrix * self

Vec3.ZERO = Vec3(0.0,0.0,0.0)
Vec3.X = Vec3(1.0,0.0,0.0)
Vec3.Y = Vec3(0.0,1.0,0.0)
Vec3.Z = Vec3(0.0,0.0,1.0)


class Mat4(object):
    def __init__(self, rows=None, m=None):
        if m is not None:
            self._m = m
        else:
            self._m = [[0.0 for j in range(4)] for i in range(4)]
            if rows is not None:
                assert len(rows) == 4
                for i in range(4):
                    row = rows[i]
                    assert len(row) == 4
                    for j in range(4):
                        self._m[i][j] = float(row[j])
    
    @staticmethod
    def new_fromfunc(func):
        return Mat4(m=[[float(func(i, j)) for j in range(4)] for i in range(4)])
    
    def __repr__(self):
        return 'Mat4({})'.format(self._m)
    
    def at(self, i, j):
        return self._m[i][j]
    
    def __mul__(self, other):
        assert isinstance(other, Mat4) or isinstance(other, Vec3)
        if isinstance(other, Mat4):
            func = lambda i, j: sum(self.at(i, k) * other.at(k, j) for k in range(4))
            return Mat4.new_fromfunc(func)
        elif isinstance(other, Vec3):
            func = lambda i: self.at(i, 3) + sum(self.at(i, j) * other[j] for j in range(3))
            return Vec3.new_fromfunc(func)
    
    def transpose(self):
        func = lambda i, j: self.at(j, i)
        return Mat4.new_fromfunc(func)
    
    def elementwise(self, func, other):
        assert isinstance(other, Mat4) or type(other) is float or type(other) is int or type(other) is long
        if isinstance(other, Mat4):
            func = lambda i, j: func(self.at(i, j), other.at(i, j))
        else:
            func = lambda i, j: func(self.at(i, j), other)
        return Mat4.new_fromfunc(func)
    
    @staticmethod
    def new_translate(vec):
        assert isinstance(vec, Vec3)
        func = lambda i, j: 1.0 if i == j else vec[i] if j == 3 else 0.0
        return Mat4.new_fromfunc(func)
    
    @staticmethod
    def new_scale(vec):
        assert isinstance(vec, Vec3)
        func = lambda i, j: (vec[i] if i < 3 else 1.0) if i == j else 0.0
        return Mat4.new_fromfunc(func)
    
    @staticmethod
    def new_base(x_unit_vec, y_unit_vec, z_unit_vec, origin_vec):
        assert isinstance(x_unit_vec, Vec3)
        assert isinstance(y_unit_vec, Vec3)
        assert isinstance(z_unit_vec, Vec3)
        assert isinstance(origin_vec, Vec3)
        func = lambda i, j: (x_unit_vec[i] if j == 0 else y_unit_vec[i] if j == 1 else z_unit_vec[i] if j == 2 else origin_vec[i]) if i < 3 else 1.0 if i == j else 0.0
        return Mat4.new_fromfunc(func)
    
    @staticmethod
    def new_householder(normal):
        assert isinstance(normal, Vec3)
        normalized_normal = normal.normalize()
        a = normalized_normal[0]
        b = normalized_normal[1]
        c = normalized_normal[2]
        return Mat4([
            [1.0-2.0*a*a, -2.0*a*b, -2.0*a*c, 0.0],
            [-2.0*a*b, 1.0-2.0*b*b, -2.0*b*c, 0.0],
            [-2.0*a*c, -2.0*b*c, 1.0-2.0*c*c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

Mat4.ID = Mat4.new_fromfunc(lambda i, j: 1.0 if i == j else 0.0)
