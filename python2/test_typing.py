from __future__ import absolute_import, unicode_literals
import re
import sys
from unittest import TestCase, main

from typing import Any
from typing import TypeVar, AnyStr
from typing import T, KT, VT  # Not in __all__.
from typing import Union, Optional
from typing import Tuple
from typing import Callable
from typing import Generic
from typing import cast
from typing import NamedTuple
from typing import IO, TextIO, BinaryIO
from typing import Pattern, Match
import typing


class Employee(object):
    pass


class Manager(Employee):
    pass


class Founder(Employee):
    pass


class ManagingFounder(Manager, Founder):
    pass


class AnyTests(TestCase):

    def test_any_instance_type_error(self):
        with self.assertRaises(TypeError):
            isinstance(42, Any)

    def test_any_subclass(self):
        self.assertTrue(issubclass(Employee, Any))
        self.assertTrue(issubclass(int, Any))
        self.assertTrue(issubclass(type(None), Any))
        self.assertTrue(issubclass(object, Any))

    def test_others_any(self):
        self.assertFalse(issubclass(Any, Employee))
        self.assertFalse(issubclass(Any, int))
        self.assertFalse(issubclass(Any, type(None)))
        # However, Any is a subclass of object (this can't be helped).
        self.assertTrue(issubclass(Any, object))

    def test_repr(self):
        self.assertEqual(repr(Any), 'typing.Any')

    def test_errors(self):
        with self.assertRaises(TypeError):
            issubclass(42, Any)
        with self.assertRaises(TypeError):
            Any[int]  # Any is not a generic type.

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class A(Any):
                pass

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Any()

    def test_cannot_subscript(self):
        with self.assertRaises(TypeError):
            Any[int]

    def test_any_is_subclass(self):
        # Any should be considered a subclass of everything.
        assert issubclass(Any, Any)
        assert issubclass(Any, typing.List)
        assert issubclass(Any, typing.List[int])
        assert issubclass(Any, typing.List[T])
        assert issubclass(Any, typing.Mapping)
        assert issubclass(Any, typing.Mapping[str, int])
        assert issubclass(Any, typing.Mapping[KT, VT])
        assert issubclass(Any, Generic)
        assert issubclass(Any, Generic[T])
        assert issubclass(Any, Generic[KT, VT])
        assert issubclass(Any, AnyStr)
        assert issubclass(Any, Union)
        assert issubclass(Any, Union[int, str])
        assert issubclass(Any, typing.Match)
        assert issubclass(Any, typing.Match[str])
        # These expressions must simply not fail.
        typing.Match[Any]
        typing.Pattern[Any]
        typing.IO[Any]


class TypeVarTests(TestCase):

    def test_basic_plain(self):
        T = TypeVar('T')
        # Every class is a subclass of T.
        assert issubclass(int, T)
        assert issubclass(str, T)
        # T equals itself.
        assert T == T
        # T is a subclass of itself.
        assert issubclass(T, T)
        # T is an instance of TypeVar
        assert isinstance(T, TypeVar)

    def test_typevar_instance_type_error(self):
        T = TypeVar('T')
        with self.assertRaises(TypeError):
            isinstance(42, T)

    def test_basic_constrained(self):
        A = TypeVar('A', str, bytes)
        # Only str and bytes are subclasses of A.
        assert issubclass(str, A)
        assert issubclass(bytes, A)
        assert not issubclass(int, A)
        # A equals itself.
        assert A == A
        # A is a subclass of itself.
        assert issubclass(A, A)

    def test_constrained_error(self):
        with self.assertRaises(TypeError):
            X = TypeVar('X', int)

    def test_union_unique(self):
        X = TypeVar('X')
        Y = TypeVar('Y')
        assert X != Y
        assert Union[X] == X
        assert Union[X] != Union[X, Y]
        assert Union[X, X] == X
        assert Union[X, int] != Union[X]
        assert Union[X, int] != Union[int]
        assert Union[X, int].__union_params__ == (X, int)
        assert Union[X, int].__union_set_params__ == {X, int}

    def test_union_constrained(self):
        A = TypeVar('A', str, bytes)
        assert Union[A, str] != Union[A]

    def test_repr(self):
        self.assertEqual(repr(T), '~T')
        self.assertEqual(repr(KT), '~KT')
        self.assertEqual(repr(VT), '~VT')
        self.assertEqual(repr(AnyStr), '~AnyStr')
        T_co = TypeVar('T_co', covariant=True)
        self.assertEqual(repr(T_co), '+T_co')
        T_contra = TypeVar('T_contra', contravariant=True)
        self.assertEqual(repr(T_contra), '-T_contra')

    def test_no_redefinition(self):
        self.assertNotEqual(TypeVar('T'), TypeVar('T'))
        self.assertNotEqual(TypeVar('T', int, str), TypeVar('T', int, str))

    def test_subclass_as_unions(self):
        # None of these are true -- each type var is its own world.
        self.assertFalse(issubclass(TypeVar('T', int, str),
                                    TypeVar('T', int, str)))
        self.assertFalse(issubclass(TypeVar('T', int, float),
                                    TypeVar('T', int, float, str)))
        self.assertFalse(issubclass(TypeVar('T', int, str),
                                    TypeVar('T', str, int)))
        A = TypeVar('A', int, str)
        B = TypeVar('B', int, str, float)
        self.assertFalse(issubclass(A, B))
        self.assertFalse(issubclass(B, A))

    def test_cannot_subclass_vars(self):
        with self.assertRaises(TypeError):
            class V(TypeVar('T')):
                pass

    def test_cannot_subclass_var_itself(self):
        with self.assertRaises(TypeError):
            class V(TypeVar):
                pass

    def test_cannot_instantiate_vars(self):
        with self.assertRaises(TypeError):
            TypeVar('A')()

    def test_bound(self):
        X = TypeVar('X', bound=Employee)
        assert issubclass(Employee, X)
        assert issubclass(Manager, X)
        assert not issubclass(int, X)

    def test_bound_errors(self):
        with self.assertRaises(TypeError):
            TypeVar('X', bound=42)
        with self.assertRaises(TypeError):
            TypeVar('X', str, float, bound=Employee)


class UnionTests(TestCase):

    def test_basics(self):
        u = Union[int, float]
        self.assertNotEqual(u, Union)
        self.assertTrue(issubclass(int, u))
        self.assertTrue(issubclass(float, u))

    def test_union_any(self):
        u = Union[Any]
        self.assertEqual(u, Any)
        u = Union[int, Any]
        self.assertEqual(u, Any)
        u = Union[Any, int]
        self.assertEqual(u, Any)

    def test_union_object(self):
        u = Union[object]
        self.assertEqual(u, object)
        u = Union[int, object]
        self.assertEqual(u, object)
        u = Union[object, int]
        self.assertEqual(u, object)

    def test_union_any_object(self):
        u = Union[object, Any]
        self.assertEqual(u, Any)
        u = Union[Any, object]
        self.assertEqual(u, Any)

    def test_unordered(self):
        u1 = Union[int, float]
        u2 = Union[float, int]
        self.assertEqual(u1, u2)

    def test_subclass(self):
        u = Union[int, Employee]
        self.assertTrue(issubclass(Manager, u))

    def test_self_subclass(self):
        self.assertTrue(issubclass(Union[KT, VT], Union))
        self.assertFalse(issubclass(Union, Union[KT, VT]))

    def test_multiple_inheritance(self):
        u = Union[int, Employee]
        self.assertTrue(issubclass(ManagingFounder, u))

    def test_single_class_disappears(self):
        t = Union[Employee]
        self.assertIs(t, Employee)

    def test_base_class_disappears(self):
        u = Union[Employee, Manager, int]
        self.assertEqual(u, Union[int, Employee])
        u = Union[Manager, int, Employee]
        self.assertEqual(u, Union[int, Employee])
        u = Union[Employee, Manager]
        self.assertIs(u, Employee)

    def test_weird_subclasses(self):
        u = Union[Employee, int, float]
        v = Union[int, float]
        self.assertTrue(issubclass(v, u))
        w = Union[int, Manager]
        self.assertTrue(issubclass(w, u))

    def test_union_union(self):
        u = Union[int, float]
        v = Union[u, Employee]
        self.assertEqual(v, Union[int, float, Employee])

    def test_repr(self):
        self.assertEqual(repr(Union), 'typing.Union')
        u = Union[Employee, int]
        self.assertEqual(repr(u), 'typing.Union[%s.Employee, int]' % __name__)
        u = Union[int, Employee]
        self.assertEqual(repr(u), 'typing.Union[int, %s.Employee]' % __name__)

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):
            class C(Union):
                pass
        with self.assertRaises(TypeError):
            class C(Union[int, str]):
                pass

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Union()
        u = Union[int, float]
        with self.assertRaises(TypeError):
            u()

    def test_optional(self):
        o = Optional[int]
        u = Union[int, None]
        self.assertEqual(o, u)

    def test_empty(self):
        with self.assertRaises(TypeError):
            Union[()]

    def test_issubclass_union(self):
        assert issubclass(Union[int, str], Union)
        assert not issubclass(int, Union)

    def test_union_instance_type_error(self):
        with self.assertRaises(TypeError):
            isinstance(42, Union[int, str])

    def test_union_str_pattern(self):
        # Shouldn't crash; see http://bugs.python.org/issue25390
        A = Union[str, Pattern]


class TypeVarUnionTests(TestCase):

    def test_simpler(self):
        A = TypeVar('A', int, str, float)
        B = TypeVar('B', int, str)
        assert issubclass(A, A)
        assert issubclass(B, B)
        assert not issubclass(B, A)
        assert issubclass(A, Union[int, str, float])
        assert not issubclass(Union[int, str, float], A)
        assert not issubclass(Union[int, str], B)
        assert issubclass(B, Union[int, str])
        assert not issubclass(A, B)
        assert not issubclass(Union[int, str, float], B)
        assert not issubclass(A, Union[int, str])

    def test_var_union_subclass(self):
        self.assertTrue(issubclass(T, Union[int, T]))
        self.assertTrue(issubclass(KT, Union[KT, VT]))

    def test_var_union(self):
        TU = TypeVar('TU', Union[int, float], None)
        assert issubclass(int, TU)
        assert issubclass(float, TU)


class TupleTests(TestCase):

    def test_basics(self):
        self.assertTrue(issubclass(Tuple[int, str], Tuple))
        self.assertTrue(issubclass(Tuple[int, str], Tuple[int, str]))
        self.assertFalse(issubclass(int, Tuple))
        self.assertFalse(issubclass(Tuple[float, str], Tuple[int, str]))
        self.assertFalse(issubclass(Tuple[int, str, int], Tuple[int, str]))
        self.assertFalse(issubclass(Tuple[int, str], Tuple[int, str, int]))
        self.assertTrue(issubclass(tuple, Tuple))
        self.assertFalse(issubclass(Tuple, tuple))  # Can't have it both ways.

    def test_tuple_subclass(self):
        class MyTuple(tuple):
            pass
        self.assertTrue(issubclass(MyTuple, Tuple))

    def test_tuple_instance_type_error(self):
        with self.assertRaises(TypeError):
            isinstance((0, 0), Tuple[int, int])
        with self.assertRaises(TypeError):
            isinstance((0, 0), Tuple)

    def test_tuple_ellipsis_subclass(self):

        class B(object):
            pass

        class C(B):
            pass

        assert not issubclass(Tuple[B], Tuple[B, ...])
        assert issubclass(Tuple[C, ...], Tuple[B, ...])
        assert not issubclass(Tuple[C, ...], Tuple[B])
        assert not issubclass(Tuple[C], Tuple[B, ...])

    def test_repr(self):
        self.assertEqual(repr(Tuple), 'typing.Tuple')
        self.assertEqual(repr(Tuple[()]), 'typing.Tuple[]')
        self.assertEqual(repr(Tuple[int, float]), 'typing.Tuple[int, float]')
        self.assertEqual(repr(Tuple[int, ...]), 'typing.Tuple[int, ...]')

    def test_errors(self):
        with self.assertRaises(TypeError):
            issubclass(42, Tuple)
        with self.assertRaises(TypeError):
            issubclass(42, Tuple[int])


class CallableTests(TestCase):

    def test_self_subclass(self):
        self.assertTrue(issubclass(Callable[[int], int], Callable))
        self.assertFalse(issubclass(Callable, Callable[[int], int]))
        self.assertTrue(issubclass(Callable[[int], int], Callable[[int], int]))
        self.assertFalse(issubclass(Callable[[Employee], int],
                                    Callable[[Manager], int]))
        self.assertFalse(issubclass(Callable[[Manager], int],
                                    Callable[[Employee], int]))
        self.assertFalse(issubclass(Callable[[int], Employee],
                                    Callable[[int], Manager]))
        self.assertFalse(issubclass(Callable[[int], Manager],
                                    Callable[[int], Employee]))

    def test_eq_hash(self):
        self.assertEqual(Callable[[int], int], Callable[[int], int])
        self.assertEqual(len({Callable[[int], int], Callable[[int], int]}), 1)
        self.assertNotEqual(Callable[[int], int], Callable[[int], str])
        self.assertNotEqual(Callable[[int], int], Callable[[str], int])
        self.assertNotEqual(Callable[[int], int], Callable[[int, int], int])
        self.assertNotEqual(Callable[[int], int], Callable[[], int])
        self.assertNotEqual(Callable[[int], int], Callable)

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError):

            class C(Callable):
                pass

        with self.assertRaises(TypeError):

            class C(Callable[[int], int]):
                pass

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            Callable()
        c = Callable[[int], str]
        with self.assertRaises(TypeError):
            c()

    def test_callable_instance_works(self):
        def f():
            pass
        assert isinstance(f, Callable)
        assert not isinstance(None, Callable)

    def test_callable_instance_type_error(self):
        def f():
            pass
        with self.assertRaises(TypeError):
            assert isinstance(f, Callable[[], None])
        with self.assertRaises(TypeError):
            assert isinstance(f, Callable[[], Any])
        with self.assertRaises(TypeError):
            assert not isinstance(None, Callable[[], None])
        with self.assertRaises(TypeError):
            assert not isinstance(None, Callable[[], Any])

    def test_repr(self):
        ct0 = Callable[[], bool]
        self.assertEqual(repr(ct0), 'typing.Callable[[], bool]')
        ct2 = Callable[[str, float], int]
        self.assertEqual(repr(ct2), 'typing.Callable[[str, float], int]')
        ctv = Callable[..., str]
        self.assertEqual(repr(ctv), 'typing.Callable[..., str]')


XK = TypeVar('XK', unicode, bytes)
XV = TypeVar('XV')


class SimpleMapping(Generic[XK, XV]):

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    def get(self, key, default=None):
        pass


class MySimpleMapping(SimpleMapping):

    def __init__(self):
        self.store = {}

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def get(self, key, default=None):
        try:
            return self.store[key]
        except KeyError:
            return default


class ProtocolTests(TestCase):

    def test_supports_int(self):
        assert issubclass(int, typing.SupportsInt)
        assert not issubclass(str, typing.SupportsInt)

    def test_supports_float(self):
        assert issubclass(float, typing.SupportsFloat)
        assert not issubclass(str, typing.SupportsFloat)

    def test_supports_complex(self):

        # Note: complex itself doesn't have __complex__.
        class C(object):
            def __complex__(self):
                return 0j

        assert issubclass(C, typing.SupportsComplex)
        assert not issubclass(str, typing.SupportsComplex)

    def test_supports_abs(self):
        assert issubclass(float, typing.SupportsAbs)
        assert issubclass(int, typing.SupportsAbs)
        assert not issubclass(str, typing.SupportsAbs)

    def test_reversible(self):
        assert issubclass(list, typing.Reversible)
        assert not issubclass(int, typing.Reversible)

    def test_protocol_instance_type_error(self):
        with self.assertRaises(TypeError):
            isinstance([], typing.Reversible)


class GenericTests(TestCase):

    def test_basics(self):
        X = SimpleMapping[unicode, Any]
        Y = SimpleMapping[XK, unicode]
        X[unicode, unicode]
        Y[unicode, unicode]
        with self.assertRaises(TypeError):
            X[int, unicode]
        with self.assertRaises(TypeError):
            Y[unicode, bytes]

    def test_init(self):
        T = TypeVar('T')
        S = TypeVar('S')
        with self.assertRaises(TypeError):
            Generic[T, T]
        with self.assertRaises(TypeError):
            Generic[T, S, T]

    def test_repr(self):
        self.assertEqual(repr(SimpleMapping),
                         __name__ + '.' + 'SimpleMapping[~XK, ~XV]')
        self.assertEqual(repr(MySimpleMapping),
                         __name__ + '.' + 'MySimpleMapping[~XK, ~XV]')

    def test_errors(self):
        with self.assertRaises(TypeError):
            B = SimpleMapping[XK, Any]

            class C(Generic[B]):
                pass

    def test_repr_2(self):
        PY32 = sys.version_info[:2] < (3, 3)

        class C(Generic[T]):
            pass

        assert C.__module__ == __name__
        if not PY32:
            assert C.__qualname__ == 'GenericTests.test_repr_2.<locals>.C'
        assert repr(C).split('.')[-1] == 'C[~T]'
        X = C[int]
        assert X.__module__ == __name__
        if not PY32:
            assert X.__qualname__ == 'C'
        assert repr(X).split('.')[-1] == 'C[int]'

        class Y(C[int]):
            pass

        assert Y.__module__ == __name__
        if not PY32:
            assert Y.__qualname__ == 'GenericTests.test_repr_2.<locals>.Y'
        assert repr(Y).split('.')[-1] == 'Y[int]'

    def test_eq_1(self):
        assert Generic == Generic
        assert Generic[T] == Generic[T]
        assert Generic[KT] != Generic[VT]

    def test_eq_2(self):

        class A(Generic[T]):
            pass

        class B(Generic[T]):
            pass

        assert A == A
        assert A != B
        assert A[T] == A[T]
        assert A[T] != B[T]

    def test_multiple_inheritance(self):

        class A(Generic[T, VT]):
            pass

        class B(Generic[KT, T]):
            pass

        class C(A, Generic[KT, VT], B):
            pass

        assert C.__parameters__ == (T, VT, KT)

    def test_type_erasure(self):
        T = TypeVar('T')

        class Node(Generic[T]):
            def __init__(self, label,
                         left = None,
                         right = None):
                self.label = label  # type: T
                self.left = left  # type: Optional[Node[T]]
                self.right = right  # type: Optional[Node[T]]

        def foo(x):
            a = Node(x)
            b = Node[T](x)
            c = Node[Any](x)
            assert type(a) is Node
            assert type(b) is Node
            assert type(c) is Node

        foo(42)


class VarianceTests(TestCase):

    def test_invariance(self):
        # Because of invariance, List[subclass of X] is not a subclass
        # of List[X], and ditto for MutableSequence.
        assert not issubclass(typing.List[Manager], typing.List[Employee])
        assert not issubclass(typing.MutableSequence[Manager],
                              typing.MutableSequence[Employee])
        # It's still reflexive.
        assert issubclass(typing.List[Employee], typing.List[Employee])
        assert issubclass(typing.MutableSequence[Employee],
                          typing.MutableSequence[Employee])

    def test_covariance_tuple(self):
        # Check covariace for Tuple (which are really special cases).
        assert issubclass(Tuple[Manager], Tuple[Employee])
        assert not issubclass(Tuple[Employee], Tuple[Manager])
        # And pairwise.
        assert issubclass(Tuple[Manager, Manager], Tuple[Employee, Employee])
        assert not issubclass(Tuple[Employee, Employee],
                              Tuple[Manager, Employee])
        # And using ellipsis.
        assert issubclass(Tuple[Manager, ...], Tuple[Employee, ...])
        assert not issubclass(Tuple[Employee, ...], Tuple[Manager, ...])

    def test_covariance_sequence(self):
        # Check covariance for Sequence (which is just a generic class
        # for this purpose, but using a covariant type variable).
        assert issubclass(typing.Sequence[Manager], typing.Sequence[Employee])
        assert not issubclass(typing.Sequence[Employee],
                              typing.Sequence[Manager])

    def test_covariance_mapping(self):
        # Ditto for Mapping (covariant in the value, invariant in the key).
        assert issubclass(typing.Mapping[Employee, Manager],
                          typing.Mapping[Employee, Employee])
        assert not issubclass(typing.Mapping[Manager, Employee],
                              typing.Mapping[Employee, Employee])
        assert not issubclass(typing.Mapping[Employee, Manager],
                              typing.Mapping[Manager, Manager])
        assert not issubclass(typing.Mapping[Manager, Employee],
                              typing.Mapping[Manager, Manager])


class CastTests(TestCase):

    def test_basics(self):
        assert cast(int, 42) == 42
        assert cast(float, 42) == 42
        assert type(cast(float, 42)) is int
        assert cast(Any, 42) == 42
        assert cast(list, 42) == 42
        assert cast(Union[str, float], 42) == 42
        assert cast(AnyStr, 42) == 42
        assert cast(None, 42) == 42

    def test_errors(self):
        # Bogus calls are not expected to fail.
        cast(42, 42)
        cast('hello', 42)


class ForwardRefTests(TestCase):

    def test_forwardref_instance_type_error(self):
        fr = typing._ForwardRef('int')
        with self.assertRaises(TypeError):
            isinstance(42, fr)

    def test_syntax_error(self):

        with self.assertRaises(SyntaxError):
            Generic['/T']


class OverloadTests(TestCase):

    def test_overload_exists(self):
        from typing import overload

    def test_overload_fails(self):
        from typing import overload

        with self.assertRaises(RuntimeError):

            @overload
            def blah():
                pass

            blah()

    def test_overload_succeeds(self):
        from typing import overload

        @overload
        def blah():
            pass

        def blah():
            pass

        blah()


class CollectionsAbcTests(TestCase):

    def test_hashable(self):
        assert isinstance(42, typing.Hashable)
        assert not isinstance([], typing.Hashable)

    def test_iterable(self):
        assert isinstance([], typing.Iterable)
        # Due to ABC caching, the second time takes a separate code
        # path and could fail.  So call this a few times.
        assert isinstance([], typing.Iterable)
        assert isinstance([], typing.Iterable)
        assert isinstance([], typing.Iterable[int])
        assert not isinstance(42, typing.Iterable)
        # Just in case, also test issubclass() a few times.
        assert issubclass(list, typing.Iterable)
        assert issubclass(list, typing.Iterable)

    def test_iterator(self):
        it = iter([])
        assert isinstance(it, typing.Iterator)
        assert isinstance(it, typing.Iterator[int])
        assert not isinstance(42, typing.Iterator)

    def test_sized(self):
        assert isinstance([], typing.Sized)
        assert not isinstance(42, typing.Sized)

    def test_container(self):
        assert isinstance([], typing.Container)
        assert not isinstance(42, typing.Container)

    def test_abstractset(self):
        assert isinstance(set(), typing.AbstractSet)
        assert not isinstance(42, typing.AbstractSet)

    def test_mutableset(self):
        assert isinstance(set(), typing.MutableSet)
        assert not isinstance(frozenset(), typing.MutableSet)

    def test_mapping(self):
        assert isinstance({}, typing.Mapping)
        assert not isinstance(42, typing.Mapping)

    def test_mutablemapping(self):
        assert isinstance({}, typing.MutableMapping)
        assert not isinstance(42, typing.MutableMapping)

    def test_sequence(self):
        assert isinstance([], typing.Sequence)
        assert not isinstance(42, typing.Sequence)

    def test_mutablesequence(self):
        assert isinstance([], typing.MutableSequence)
        assert not isinstance((), typing.MutableSequence)

    def test_bytestring(self):
        assert isinstance(b'', typing.ByteString)
        assert isinstance(bytearray(b''), typing.ByteString)

    def test_list(self):
        assert issubclass(list, typing.List)

    def test_set(self):
        assert issubclass(set, typing.Set)
        assert not issubclass(frozenset, typing.Set)

    def test_frozenset(self):
        assert issubclass(frozenset, typing.FrozenSet)
        assert not issubclass(set, typing.FrozenSet)

    def test_dict(self):
        assert issubclass(dict, typing.Dict)

    def test_no_list_instantiation(self):
        with self.assertRaises(TypeError):
            typing.List()
        with self.assertRaises(TypeError):
            typing.List[T]()
        with self.assertRaises(TypeError):
            typing.List[int]()

    def test_list_subclass_instantiation(self):

        class MyList(typing.List[int]):
            pass

        a = MyList()
        assert isinstance(a, MyList)

    def test_no_dict_instantiation(self):
        with self.assertRaises(TypeError):
            typing.Dict()
        with self.assertRaises(TypeError):
            typing.Dict[KT, VT]()
        with self.assertRaises(TypeError):
            typing.Dict[str, int]()

    def test_dict_subclass_instantiation(self):

        class MyDict(typing.Dict[str, int]):
            pass

        d = MyDict()
        assert isinstance(d, MyDict)

    def test_no_set_instantiation(self):
        with self.assertRaises(TypeError):
            typing.Set()
        with self.assertRaises(TypeError):
            typing.Set[T]()
        with self.assertRaises(TypeError):
            typing.Set[int]()

    def test_set_subclass_instantiation(self):

        class MySet(typing.Set[int]):
            pass

        d = MySet()
        assert isinstance(d, MySet)

    def test_no_frozenset_instantiation(self):
        with self.assertRaises(TypeError):
            typing.FrozenSet()
        with self.assertRaises(TypeError):
            typing.FrozenSet[T]()
        with self.assertRaises(TypeError):
            typing.FrozenSet[int]()

    def test_frozenset_subclass_instantiation(self):

        class MyFrozenSet(typing.FrozenSet[int]):
            pass

        d = MyFrozenSet()
        assert isinstance(d, MyFrozenSet)

    def test_no_tuple_instantiation(self):
        with self.assertRaises(TypeError):
            Tuple()
        with self.assertRaises(TypeError):
            Tuple[T]()
        with self.assertRaises(TypeError):
            Tuple[int]()

    def test_generator(self):
        def foo():
            yield 42
        g = foo()
        assert issubclass(type(g), typing.Generator)
        assert issubclass(typing.Generator[Manager, Employee, Manager],
                          typing.Generator[Employee, Manager, Employee])
        assert not issubclass(typing.Generator[Manager, Manager, Manager],
                              typing.Generator[Employee, Employee, Employee])

    def test_no_generator_instantiation(self):
        with self.assertRaises(TypeError):
            typing.Generator()
        with self.assertRaises(TypeError):
            typing.Generator[T, T, T]()
        with self.assertRaises(TypeError):
            typing.Generator[int, int, int]()

    def test_subclassing(self):

        class MMA(typing.MutableMapping):
            pass

        with self.assertRaises(TypeError):  # It's abstract
            MMA()

        class MMC(MMA):
            def __len__(self):
                return 0

        assert len(MMC()) == 0

        class MMB(typing.MutableMapping[KT, VT]):
            def __len__(self):
                return 0

        assert len(MMB()) == 0
        assert len(MMB[str, str]()) == 0
        assert len(MMB[KT, VT]()) == 0


class NamedTupleTests(TestCase):

    def test_basics(self):
        Emp = NamedTuple('Emp', [('name', str), ('id', int)])
        assert issubclass(Emp, tuple)
        joe = Emp('Joe', 42)
        jim = Emp(name='Jim', id=1)
        assert isinstance(joe, Emp)
        assert isinstance(joe, tuple)
        assert joe.name == 'Joe'
        assert joe.id == 42
        assert jim.name == 'Jim'
        assert jim.id == 1
        assert Emp.__name__ == 'Emp'
        assert Emp._fields == ('name', 'id')
        assert Emp._field_types == dict(name=str, id=int)


class IOTests(TestCase):

    def test_io_submodule(self):
        from typing.io import IO, TextIO, BinaryIO, __all__, __name__
        assert IO is typing.IO
        assert TextIO is typing.TextIO
        assert BinaryIO is typing.BinaryIO
        assert set(__all__) == set(['IO', 'TextIO', 'BinaryIO'])
        assert __name__ == 'typing.io'


class RETests(TestCase):
    # Much of this is really testing _TypeAlias.

    def test_basics(self):
        pat = re.compile('[a-z]+', re.I)
        assert issubclass(pat.__class__, Pattern)
        assert issubclass(type(pat), Pattern)
        assert issubclass(type(pat), Pattern[str])

        mat = pat.search('12345abcde.....')
        assert issubclass(mat.__class__, Match)
        assert issubclass(mat.__class__, Match[str])
        assert issubclass(mat.__class__, Match[bytes])  # Sad but true.
        assert issubclass(type(mat), Match)
        assert issubclass(type(mat), Match[str])

        p = Pattern[Union[str, bytes]]
        assert issubclass(Pattern[str], Pattern)
        assert issubclass(Pattern[str], p)

        m = Match[Union[bytes, str]]
        assert issubclass(Match[bytes], Match)
        assert issubclass(Match[bytes], m)

    def test_errors(self):
        with self.assertRaises(TypeError):
            # Doesn't fit AnyStr.
            Pattern[int]
        with self.assertRaises(TypeError):
            # Can't change type vars?
            Match[T]
        m = Match[Union[str, bytes]]
        with self.assertRaises(TypeError):
            # Too complicated?
            m[str]
        with self.assertRaises(TypeError):
            # We don't support isinstance().
            isinstance(42, Pattern)
        with self.assertRaises(TypeError):
            # We don't support isinstance().
            isinstance(42, Pattern[str])

    def test_repr(self):
        assert repr(Pattern) == 'Pattern[~AnyStr]'
        assert repr(Pattern[unicode]) == 'Pattern[unicode]'
        assert repr(Pattern[str]) == 'Pattern[str]'
        assert repr(Match) == 'Match[~AnyStr]'
        assert repr(Match[unicode]) == 'Match[unicode]'
        assert repr(Match[str]) == 'Match[str]'

    def test_re_submodule(self):
        from typing.re import Match, Pattern, __all__, __name__
        assert Match is typing.Match
        assert Pattern is typing.Pattern
        assert set(__all__) == set(['Match', 'Pattern'])
        assert __name__ == 'typing.re'

    def test_cannot_subclass(self):
        with self.assertRaises(TypeError) as ex:

            class A(typing.Match):
                pass

        assert str(ex.exception) == "A type alias cannot be subclassed"


class AllTests(TestCase):
    """Tests for __all__."""

    def test_all(self):
        from typing import __all__ as a
        # Just spot-check the first and last of every category.
        assert 'AbstractSet' in a
        assert 'ValuesView' in a
        assert 'cast' in a
        assert 'overload' in a
        # Check that io and re are not exported.
        assert 'io' not in a
        assert 're' not in a
        # Spot-check that stdlib modules aren't exported.
        assert 'os' not in a
        assert 'sys' not in a


if __name__ == '__main__':
    main()
