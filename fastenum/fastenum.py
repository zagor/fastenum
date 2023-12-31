#cython: annotation_typing=False
'''
Almost all metaclass attributes in these classes
must be ignored for mypy as mypy does not understand
metaclasses properly.

More on this topic https://mypy.readthedocs.io/en/latest/metaclasses.html
'''

from typing import Any, Iterator, SupportsIndex, Tuple, Type, cast
import collections


def _is_descriptor(obj: Any) -> bool:
	''' Returns True if obj is a descriptor, False otherwise. '''
	return hasattr(obj, '__get__') or hasattr(obj, '__set__') or hasattr(obj, '__delete__')


class EnumMeta(type):

	# Ignoring mypy annotation at prepare method
	# as mypy does not understand metaclasses properly
	@classmethod
	def __prepare__(mcs, cls: type, bases: Tuple[type, ...]) -> collections.OrderedDict:  # type: ignore
		# pylint: disable=unused-argument
		return collections.OrderedDict()

	def __new__(
		mcs,
		cls: str,
		bases: Tuple[type, ...],
		classdict: collections.OrderedDict,  # type: ignore
	) -> 'EnumMeta':
		# pylint: disable=protected-access
		enum_class = super().__new__(mcs, cls, bases, classdict)
		# name->value map
		enum_class._member_map_ = collections.OrderedDict()  # type: ignore
		# Reverse value->name map for hashable values.
		enum_class._value_to_member_map_ = {}  # type: ignore

		for name, value in classdict.items():
			if not name.startswith('_') and not _is_descriptor(value):
				member = enum_class.__new__(enum_class)  # type: ignore
				member.name = name  # type: ignore
				member.value = value  # type: ignore
				# name and value are not expected to change, so we can cache __repr__ and __hash__.
				member._repr = '<%s.%s: %r>' % (enum_class.__name__, name, value)  # type: ignore[attr-defined]
				member._hash = hash(name)  # type: ignore[attr-defined]

				# args = value if isinstance(value, tuple) else (value,)
				member.__init__()  # type: ignore[misc]
				setattr(enum_class, name, member)
				enum_class._member_map_[name] = member  # type: ignore
				try:
					# This may fail if value is not hashable. We can't add the value
					# to the map, and by-value lookups for this value will be linear.
					enum_class._value_to_member_map_[value] = member  # type: ignore
				except TypeError:
					pass

		return enum_class

	def __call__(cls, value: Any) -> 'Enum':  # type: ignore
		# For lookups like Color(Color.red)
		if isinstance(value, cls):
			return cast('Enum', value)
		# by-value search for a matching enum member
		# see if it's in the reverse mapping (for hashable values)
		try:
			return cls._value_to_member_map_[value]  # type: ignore
		except (KeyError, TypeError):
			# not there, now do long search -- O(n) behavior
			for member in cls._member_map_.values():  # type: ignore
				if member.value == value:
					return cast('Enum', member)
		raise ValueError('%s is not a valid %s' % (value, cls.__name__))

	def __getitem__(cls, name: str) -> 'Enum':
		return cls._member_map_[name]  # type: ignore

	def __iter__(cls) -> Iterator['Enum']:
		return (v for v in cls._member_map_.values())  # type: ignore

	def __reversed__(cls) -> Iterator['Enum']:
		return reversed(list(cls))

	def __len__(cls) -> int:
		return len(cls._member_map_)  # type: ignore


class Enum(metaclass = EnumMeta):
	_repr: str
	_hash: int

	def __repr__(self) -> str:
		# cache of `'<%s.%s: %r>' % (self.__class__.__name__, self.name, self.value)`
		return self._repr

	def __str__(self) -> str:
		return '%s.%s' % (self.__class__.__name__, self.name)

	def __hash__(self) -> int:
		# cache of `hash(self.name)`
		return self._hash

	def __format__(self, format_spec: str) -> str:
		return str.__format__(str(self), format_spec)

	def __reduce_ex__(self, proto: SupportsIndex) -> Tuple[Type['Enum'], Tuple[Any]]:
		return self.__class__, (self.value,)  # type: ignore
