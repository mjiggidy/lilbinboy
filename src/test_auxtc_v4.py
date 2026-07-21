import sys
import avb, avbutils, timecode

import enum

import avbutils


def print_timecode_tracks_for_bin_item(bin_item:avb.bin.BinItem, timecode_role:avbutils.timeline.TimecodeTrackRoles|None):

	master_mob = bin_item.mob
	primary_track = avbutils.sourcerefs.primary_track_for_composition(master_mob)

	tc_range = None

	for source, offset in avbutils.source_references_for_component(primary_track.component):

		try:
			tc_track = next(avbutils.get_tracks_from_composition(source.mob, type=avbutils.TrackTypes.TIMECODE, index=timecode_role))

		except:
			continue

		else:
			
			tc_component, offset = avbutils.resolve_base_component_from_component(tc_track.component, offset + source.start_time)
			
			if not isinstance(tc_component, avb.components.Timecode):
				tc_range = f"Got {tc_component} instead"
				print("Hmm")
				continue
			
			tc_range = timecode.TimecodeRange(
				start = timecode.Timecode(tc_component.start + offset.frame_number, rate=offset.rate),
				duration=master_mob.length
			)

			tc_range = "\t".join(str(x) for x in [tc_range.start, tc_range.end, str(tc_range.duration).lstrip("00:"), tc_range.rate])
			break
	
	print(timecode_role.name, tc_range)


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