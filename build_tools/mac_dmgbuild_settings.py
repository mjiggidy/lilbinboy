format = "UDBZ"

window_rect = ((800, 800), (615, 430))

show_status_bar = False
show_tab_view   = False
show_toolbar    = False
show_pathbar    = False
show_sidebar    = False

sidebar_width = 10

badge_icon = "build_tools/icons/macos_lilbinboy.icns"
background = "build_tools/bkgs/macos_dmg_bkg.tiff"
default_view = "icon-view"
include_icon_view_settings = True
icon_size = 128

files = ["build/Lil' Bin Boy.app"]
symlinks = { "Applications": "/Applications" }
icon_locations = {
	"Lil' Bin Boy.app": (135, 160),
	"Applications": (500, 160)
}

license = {
	"default-language": "en_US",
	"licenses": {
		"en_US": "EULA"
	}
}