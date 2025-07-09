import dataclasses
from lilbinboy.lbb_features.trt import panel_trt
from lilbinboy.lbb_common import LBUtilityTab

@dataclasses.dataclass
class LBFeature:
	title:str
	id:str
	factory:LBUtilityTab

features = [
	LBFeature(
		title="Runtime Metrics",
		id="trt",
		factory=panel_trt.LBTRTCalculator
	)
]