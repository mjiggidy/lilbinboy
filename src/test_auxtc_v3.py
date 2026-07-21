import sys
import avb, avbutils, timecode

import enum

import avbutils

def resolve_track_component(component:avb.components.Component):

	if isinstance(component, avb.components.SourceClip):

		source_mob    = component.mob
		source_offset = component.start_time
		source_track  = component.track_id

		tc_tracks = next(avbutils.timeline.get_tracks_from_composition(source_mob, avbutils.timeline.TrackTypes.TIMECODE, avbutils.timeline.TimecodeTrackRoles.MASTER_TC))
		print(tc_tracks)

		print(f"SOURCE CLIP: {source_mob.name=} {source_offset=} {source_track=}")
		return source_mob

	else:
		print(component)
	



def print_timecode_tracks_for_bin_item(item:avb.bin.BinItem):

	# For a given bin item:
	# 	For each of its tracks:
	#		Resolve its component
	#			Is base component? Return
	#			Is SourceClip? Go up one level

	print(f"{item.mob.name=}")

	
	# Start with master mob
	
	mob = item.mob
	main_track = avbutils.sourcerefs.primary_track_for_composition(mob)

	# Picture SCLP of Masterclip
	component = main_track.component

	if not isinstance(component, avb.components.SourceClip):
		print("Expected a source clip, but got", component)
		sys.exit(1)

	print("Main component:", component, mob)

	source_mob = component.mob

	# Get the appropriate track
	source_track = next(avbutils.timeline.get_tracks_from_composition(source_mob, avbutils.timeline.TrackTypes.from_track(component.track), component.track_id))

	# Get source mob track I'm interested in
#	source_track     = component.track
#	source_mob       = component.mob	# NOT NEEDED??  .track gets track from mob!
	source_component = source_track.component

	if not isinstance(source_component, avb.components.SourceClip):
		print("Expected a source clip, but got", source_component)
		sys.exit()
	
	print("Source component:", source_component, source_mob)

	file_mob = source_component.mob
	file_track = next(avbutils.timeline.get_tracks_from_composition(file_mob, avbutils.timeline.TrackTypes.from_track(source_component.track), source_component.track_id))

	print(file_track.component)
	
	
	exit()

	component = resolve_track_component(component)
	component = resolve_track_component(component)
	component = resolve_track_component(component)


	#print(avbutils.timeline.format_track_label(main_track), component)

	
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
				exit()