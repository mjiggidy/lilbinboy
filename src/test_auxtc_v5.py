import sys
import avb, avbutils, timecode

import enum

import avbutils

def resolve_timecode_component_for_compositiion(mob:avb.trackgroups.Composition, track:avb.trackgroups.Track, timecode_role:avbutils.timeline.TimecodeTrackRoles, offset:int=0):


	try:
	
		# Look for track in mob
		timecode_track = next(avbutils.timeline.get_tracks_from_composition(mob, type=avbutils.timeline.TrackTypes.TIMECODE, index=int(timecode_role)))
		return avbutils.sourcerefs.resolve_base_component_from_component(timecode_track.component, offset=offset)
	
	except StopIteration:

		# Resolve the track component and look in thurr
		source_component, next_offset = avbutils.sourcerefs.resolve_base_component_from_component(track.component, offset)

		if not isinstance(source_component, avb.components.SourceClip):

			print("Got down to ", source_component)
			return None, next_offset
		
		return resolve_timecode_component_for_compositiion(mob=source_component.mob, track=source_component.track, timecode_role=timecode_role, offset=next_offset)
		



	# Match back


def print_timecode_tracks_for_bin_item(item:avb.bin.BinItem, timecode_role:avbutils.timeline.TimecodeTrackRoles):

	mob = item.mob
	track = avbutils.sourcerefs.primary_track_for_composition(mob)

	timecoe_component, offset = resolve_timecode_component_for_compositiion(mob=mob, track=track, timecode_role=timecode_role)

	if timecoe_component is None:

		print(mob.name, timecode_role, "No tc")

	else:


		if isinstance(timecoe_component, avb.components.Timecode):
			tc = timecode.TimecodeRange(
				start=timecode.Timecode(timecoe_component.start, rate=round(timecoe_component.edit_rate)),
				duration=timecoe_component.length,
			)
			print(timecode_role.name, tc)

		else:
			print("No:",timecode_role.name, timecoe_component, offset)




if __name__ == "__main__":

	if not len(sys.argv) > 1:

		import pathlib
		
		sys.exit(f"Usage: {pathlib.Path(__file__).name} binfile.avb")
	
	for bin_path in sys.argv[1:]:

		with avb.open(bin_path) as bin_handle:

			bin_contents = bin_handle.content

			for item in bin_contents.items:

				print(item.mob.name, item.mob)

				for timecode_role in avbutils.timeline.TimecodeTrackRoles:
				
					print_timecode_tracks_for_bin_item(item, timecode_role=timecode_role)
				
				print("")