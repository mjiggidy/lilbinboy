"""
The icon registry maps icons to, like, their things or whatever.
At least for now.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import avbutils
from os import PathLike
from ..res import icons_binitems



type IconRegistryType = dict[avbutils.bins.BinDisplayItemTypes, PathLike[str]]

BIN_ITEM_TYPE_ICON_REGISTRY:IconRegistryType = {

	avbutils.bins.BinDisplayItemTypes.MASTER_CLIP:        ":/icons/binitems/item_masterclip.svg",
	avbutils.bins.BinDisplayItemTypes.LINKED_MASTER_CLIP: ":/icons/binitems/item_linkedclip.svg",
	avbutils.bins.BinDisplayItemTypes.STEREOSCOPIC_CLIP:  ":/icons/binitems/item_stereoclip.svg",
	avbutils.bins.BinDisplayItemTypes.SUBCLIP:            ":/icons/binitems/item_subclip.svg",
	avbutils.bins.BinDisplayItemTypes.SEQUENCE:           ":/icons/binitems/item_timeline.svg",
	avbutils.bins.BinDisplayItemTypes.GROUP:              ":/icons/binitems/item_groupclip.svg",
	avbutils.bins.BinDisplayItemTypes.SOURCE:             ":/icons/binitems/item_source.svg",
	avbutils.bins.BinDisplayItemTypes.EFFECT:             ":/icons/binitems/item_effect.svg",

}