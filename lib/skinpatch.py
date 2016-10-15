import os
import re

import xbmc
import xbmcaddon
import patch


class SkinPatcher():
	def __init__(self, skin_id = None):
		if skin_id is None:
			self.skin_id = xbmc.getSkinDir()
		else:
			self.skin_id = skin_id

		# Find patch files for the current skin
		patch_path = os.path.join(xbmcaddon.Addon().getAddonInfo("path"), "resources", "skins")
		self.patches = []
		for patch_file in os.listdir(patch_path):
			if self.skin_id in patch_file:
				self.patches.append(os.path.join(patch_path, patch_file))

	# Apply the patch using python-patch https://github.com/techtonik/python-patch
	def patch(self):
		for patch_file in self.patches:
			patchset = patch.fromfile(patch_file)
			if patchset.apply(root=xbmcaddon.Addon(self.skin_id).getAddonInfo("path")):
				return True
		return False
