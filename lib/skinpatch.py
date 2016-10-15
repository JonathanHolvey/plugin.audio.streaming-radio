import os
import re

import xbmc
import xbmcaddon
import patch


class SkinPatch():
	def __init__(self):
		self.skin_id = xbmc.getSkinDir()
		self.skin_path = xbmcaddon.Addon(self.skin_id).getAddonInfo("path")
		self.applied_patch = None

		# Find patch files for the current skin
		patch_path = os.path.join(xbmcaddon.Addon().getAddonInfo("path"), "resources", "skins")
		self.patches = []
		for patch_file in os.listdir(patch_path):
			if patch_file.startswith(self.skin_id):
				self.patches.append(os.path.join(patch_path, patch_file))

	# Apply the patch using python-patch https://github.com/techtonik/python-patch
	def apply(self):
		for patch_file in self.patches:
			patchset = patch.fromfile(patch_file)
			if patchset.apply(root=self.skin_path):
				self.applied_patch = patch_file
				return True
		return False

	# Remove the patch using python-patch
	def revert(self):
		if self.applied_patch is not None:
			patchset = patch.fromfile(self.applied_patch)
			if patchset.revert(root=self.skin_path):
				self.applied_patch = None
				return True
		return False