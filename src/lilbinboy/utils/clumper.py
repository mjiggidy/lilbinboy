import typing

# Look at me tryna be Mr. Algarhyddm over here

def clumpValues(
		iterable:typing.Iterable[typing.Any],
		/,
		key     :typing.Callable[[typing.Any], typing.Any]|None=None,
		reverse :bool=False
	) -> typing.Iterator[list[typing.Any]]:
	"""Clump contiguous values together"""

	clump_key  = key or (lambda x: x)
	clump_step = 1 if reverse else -1

	clump = []

	for item in sorted(iterable, key=clump_key, reverse=reverse):
		
		# If the current value neighbors the previous, add it to the clump
		if not clump or clump_key(clump[-1]) == clump_key(item) + clump_step:
			clump.append(item)

		# Otherwise yield the last clump and start anew
		else:
			yield clump
			clump = [item]
		
	if clump:
		yield clump

if __name__ == "__main__":

	thing = clumpValues(
		[
			("PeePee", 2),
			("PooPoo", 1),
			("PeePee", 3),
			("PeePee", 5),
			("PooPoo", 7),
			("PooPoo", 8),
			("PeePee", 9),
		],
		key=lambda x: x[1],
		reverse=False
	)

	print(list(thing))
