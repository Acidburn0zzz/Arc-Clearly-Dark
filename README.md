# Arc-Clearly-Dark

**Arc Clearly Dark** is a customized patch set for the dark flavor of the [Arc](https://github.com/horst3180/Arc-theme) GNOME Shell theme (aka. the *Arc Dark* theme). It features:

* Increased padding in the system status icons area, making the icons look less squished, closer to the default GNOME look
* Toned down colors for hovering and selection in the Dash Sidebar, the Applications Overview, and the search bar
* No borders and no background (aka. *clear*-ness) for all major elements in the Activities Overview, allowing for a simple, fluid, and unified look

## Installation

**Arc Clearly Dark** is distributed as a python patch script for the vanilla *Arc Dark* theme. Installation can generaly be done as follows:

1. Build the vanilla *Arc Dark* theme from the upstream [Arc](https://github.com/horst3180/Arc-theme) repo.
2. Copy `patch.py` from this repo to the `Arc-Dark` theme directory.
3. Execute `patch.py` in the `Arc-Dark` theme folder. Please note that `patch.py` is written in Python 3 and needs an up-to-date Python runtime.
4. If `patch.py` executes successfully, you've just transformed the *Arc Dark* theme into the *Arc Clearly Dark* theme! Rename your `Arc-Dark` theme folder to `Arc-Clearly-Dark` or something else as you see fit.

Note that *Arc Clearly Dark* affects only the GNOME Shell portion of the original theme. The GTK and other themes are not touched.
