import sys
import avb, avbutils, timecode

import enum

import avbutils

def print_timecode_tracks_for_bin_item(item:avb.bin.BinItem):

	# For a given bin item:
	# 	For each of its tracks:
	#		Resolve its component
	#			Is base component? Return
	#			Is SourceClip? Go up one level

	
	mob = item.mob
	main_track = avbutils.sourcerefs.primary_track_for_composition(mob)

	component = main_track.component
	offset    = 0

	while isinstance(component, avb.components.SourceClip) or isinstance(component, avb.components.Sequence):

		print(component)

		component, offset = avbutils.resolve_base_component_from_component(main_track.component, offset)

	print(avbutils.timeline.format_track_label(main_track), component)

	
	print("--")





if __name__ == "__main__":

	if not len(sys.argv) > 1:

		import pathlib
		
		sys.exit(f"Usage: {pathlib.Path(__file__).name} binfile.avb")
	
	for bin_path in sys.argv[1:]:

		with avb.open(bin_path) as bin_handle:

			bin_contents = bin_handle.content

			for item in bin_contents.items:
				print_timecode_tracks_for_bin_item(item)