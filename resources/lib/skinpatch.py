import os
import xml.etree.ElementTree as et

import xbmc
import xbmcgui
import xbmcaddon
import patch


class SkinPatch():
    def __init__(self, skin_id=None):
        self.skin_id = skin_id or xbmc.getSkinDir()
        self.skin_path = xbmcaddon.Addon(self.skin_id).getAddonInfo("path")
        self.applied_patch = None

        # Find patch files for the current skin
        patch_path = os.path.join(xbmcaddon.Addon().getAddonInfo("path"), "resources", "skins")
        self.patches = []
        for patch_file in os.listdir(patch_path):
            if patch_file.startswith(self.skin_id):
                self.patches.append(os.path.join(patch_path, patch_file))
        self.patches.sort(reverse=True)
        self.get_status()

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

    # Apply patch and reload skin, then revert files
    def sideload(self):
        name = xbmcaddon.Addon().getAddonInfo("id") + ".skinpatch-status"
        value = xbmcaddon.Addon().getAddonInfo("version")  # Force re-patch after addon update
        window = xbmcgui.Window(10000)
        if window.getProperty(name) != value:
            if self.apply():
                xbmc.executebuiltin("ReloadSkin()")
                xbmc.sleep(1000)
                window.setProperty(name, value)
                self.revert()

    # Load and verify skin patch info
    def get_status(self):
        self.patched = False
        self.version = None
        self.patch = None
        self.files = []

        # Check if status has been vefied already this session
        name = xbmcaddon.Addon().getAddonInfo("id") + ".skinpatch-status"
        window = xbmcgui.Window(10000)
        if window.getProperty(name) == xbmcaddon.Addon().getAddonInfo("version"):
            self.patched = True
        else:
            # Retrieve last-patch information from XML file
            xml_path = os.path.join(xbmcaddon.Addon().getAddonInfo("profile"), "skinpatch.xml")
            if os.path.isfile(xml_path):
                xml = et.parse(xml_path).getroot().find("skin[@id='{}']".format(self.skin_id))
                if xml is not None:
                    self.files = [(file.text, file.attrib["check"]) for file in xml.findall("file")]
                    self.patch = xml.find("patch").text, xml.find("patch").attrib["check"]
                    self.version = xml.attrib["version"]

            # Verify patch integrity by checking all modified files
            if len(self.files) > 0 and self.version is not None:
                for path, check in self.files:
                    if hash_file(path) != check:
                        break
                else:
                    self.patched = True
                    window.setProperty(name, self.version)


def hash_file(path):
    import hashlib
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(path, "rb") as file:
        buf = file.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()
