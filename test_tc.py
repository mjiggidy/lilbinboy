from timecode import Timecode

tc_raw = "123456"

def raw_to_tc_string(tc_raw:str) -> str:

	tc_raw_rev = tc_raw[::-1]

	return ":".join([tc_raw_rev[i:i+2] for i in range(0,len(tc_raw),2)])[::-1]

print(raw_to_tc_string(tc_raw))