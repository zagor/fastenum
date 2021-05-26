fastenum
========

A roughly 3x faster drop-in replacement of Python's `enum <https://docs.python.org/3/library/enum.html>`_.


Installation
-------------

::
	pip install fastenum


Usage
------
Simply use ``fastenum.Enum`` instead of ``enum.Enum``:

.. code:: python
	import fastenum

	class Color(fastenum.Enum):
		RED = 0
		BLUE = 1
		GREEN = 2

	assert isinstance(Color.RED, Color)
	assert Color.RED is Color['RED']
	assert Color.BLUE != 1
	assert Color.GREEN.value == 2

	def is_red(c: Color) -> bool:
		return c is Color.RED


Running tests & benchmarks
---------------------------

::
	pip install -r dev-requirements.txt
	PYTHONPATH=. cq && pytest
