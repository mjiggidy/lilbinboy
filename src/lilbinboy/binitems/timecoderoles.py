import enum

class BSTimecodeTrackRoles(enum.Enum):
	
	MASTER_TC = 1

	AUX_TC_1  = 3
	AUX_TC_2  = 4
	AUX_TC_3  = 5
	AUX_TC_4  = 6
	AUX_TC_5  = 7

	TC_25     = 10

	AUX_TC_24 = 12
	TC_30NP   = 13