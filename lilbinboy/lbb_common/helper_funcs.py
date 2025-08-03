"""
Generic helper functions that don't be goin nowheres else.
"""

def make_unique_name(name:str, existing_names:list[str], *, default_index_start:int=1, default_index_padding:int=2) -> str:
	"""Ensure a unique name with the format "My Kewl Name.02" or something"""

	import re

	# Return the unaltered name if it isn't already in thurr
	if name not in existing_names:
		return name
	
	# Check for a ".01" or something
	match = re.match(r"^(?P<base_name>.*)(?P<current_index>\d+)$", name)
	if match:
		current_index = int(match.group("current_index")) + 1
		index_padding = len(match.group("current_index"))
		base_name = match.group("base_name")
	else:
		current_index = default_index_start
		index_padding = default_index_padding
		base_name = name.rstrip(".") + "."
		
	current_name = base_name + str(current_index).zfill(index_padding)

	while current_name in existing_names:
		current_index += 1
		current_name = base_name + str(current_index).zfill(index_padding)
	
	return current_name