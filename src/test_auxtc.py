import sys
import avb, avbutils, timecode

import enum

from lilbinboy.binitems.timecoderoles import BSTimecodeTrackRoles

def name_for_index(track_index:int):
	
	try:
		return BSTimecodeTrackRoles(track_index).name
	except:
		return f"UNKNOWN {track_index}"


def inspect_timecode_component(timecode_component:avb.components.Timecode):

	try:
		rate  = timecode_component.fps
		frame = timecode_component.start
		lenth = timecode_component.length
		
		tc_range = timecode.TimecodeRange(
			start=timecode.Timecode(frame, rate=rate),
			duration=lenth
		)

	except:
		tc_range = "Huh"

	return str(tc_range)



if __name__ == "__main__":

	if not len(sys.argv) > 1:

		import pathlib
		
		sys.exit(f"Usage: {pathlib.Path(__file__).name} binfile.avb")
	
	for bin_path in sys.argv[1:]:

		print(bin_path)

		with avb.open(bin_path) as bin_handle:

			bin_contents = bin_handle.content

			for item in bin_contents.items:
				
				print(item.mob)

				for track in item.mob.tracks:

					if not track.media_kind == "timecode":
						continue

					tc_component = track.component

					if isinstance(tc_component, avb.components.Timecode):

						print("STD TC:", BSTimecodeTrackRoles(track.index).name, name_for_index(track.index),  inspect_timecode_component(tc_component))
					
					elif isinstance(tc_component, avb.components.Sequence):
						
						if len(tc_component.components) == 1:

							print("\t".join(["AUX TC:", str(track.index), name_for_index(track.index),  "EMPTY"]))
							continue
						
						elif not len(tc_component.components) == 3:

							print("\t".join(["COMPLEX TC:", str(tc_component.components)]))
							continue

						print("\t".join(["AUX TC:", str(track.index), name_for_index(track.index), inspect_timecode_component(tc_component.components[1])]))

					else:
						print("\t".join(["OTHER :", str(track.index)]))

