format = "UDBZ"

widow_rect = (1000, 1000, 800, 400)

show_status_bar = False
show_tab_view   = False
show_toolbar    = False
show_pathbar    = False
show_sidebar    = False

badge_icon = "build_tools/icons/macos_lilbinboy.icns"
background = "build_tools/bkgs/macos_dmg_bkg.tiff"
default_view = "icon-view"
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