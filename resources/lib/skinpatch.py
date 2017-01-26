import os
import xml.etree.ElementTree as et
import shutil

import xbmc
import xbmcgui
import xbmcaddon
import patch

STATUS_CLEAN = 0
STATUS_PATCHED = 1
STATUS_UPDATED = 2  # The addon has been updated since patching

data_path = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo("profile"))
property_name = xbmcaddon.Addon().getAddonInfo("id") + ".skinpatch-status"
window = xbmcgui.Window(10000)


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
        if self.status != STATUS_CLEAN:
            return False
        for patch_path in self.patches:
            patchset = patch.fromfile(patch_path)
            if patchset.apply(root=self.skin_path):
                # Set patch status
                self.status = STATUS_PATCHED
                self.patch = os.path.basename(patch_path)
                self.files = [(item.target, hash_file(os.path.join(self.skin_path, item.target)))
                              for item in patchset.items]
                self.version = xbmcaddon.Addon().getAddonInfo("version")
                self.save_status()
                # Copy patch file to allow removal later
                copy_path = os.path.join(data_path, "skins", self.patch)
                if not os.path.isdir(os.path.dirname(copy_path)):
                    os.makedirs(os.path.dirname(copy_path))
                shutil.copy(patch_path, copy_path)
                return True

    # Remove the patch using python-patch
    def revert(self):
        if self.status == STATUS_CLEAN:
            return False
        patch_path = os.path.join(data_path, "skins", self.patch)
        patchset = patch.fromfile(patch_path)
        if patchset.revert(root=self.skin_path):
            self.status = STATUS_CLEAN
            self.save_status()
            os.remove(patch_path)
            window.clearProperty(property_name)
            return True

    # Apply patch if required and re-apply if patch file changes
    def autopatch(self):
        if self.status == STATUS_UPDATED:
            self.revert()
        if self.status == STATUS_CLEAN:
            if self.apply():
                xbmc.executebuiltin("ReloadSkin()")
                xbmc.sleep(1000)
            else:
                return
        window.setProperty(property_name, self.version)

    # Load and verify skin patch info
    def get_status(self):
        self.status = STATUS_CLEAN
        self.patch = None
        self.files = None
        self.version = None

        # Retrieve last-patch information from XML file
        xml_path = os.path.join(data_path, "skinpatch.xml")
        if os.path.isfile(xml_path):
            xml = et.parse(xml_path).getroot().find("skin[@id='{0}']".format(self.skin_id))
            if xml is not None:
                self.files = [(file.text, file.attrib["check"]) for file in xml.findall("file")]
                self.patch = xml.find("patch").text
                self.version = xml.find("patch").attrib["version"]

        # Check if status has already been verified this session
        # If the addon or skin are updated, the property value won't match
        version = xbmcaddon.Addon().getAddonInfo("version")
        if window.getProperty(property_name) == version:
            self.status = STATUS_PATCHED
        elif self.patch is not None:
            # Check if addon has been updated since patching
            if self.version != version:
                self.status = STATUS_UPDATED
            else:
                # Verify patch integrity by checking all modified files
                for path, check in self.files:
                    if hash_file(os.path.join(self.skin_path, path)) != check:
                        break
                else:
                    self.status = STATUS_PATCHED

    # Save skin patch status to XML file
    def save_status(self):
        xml_path = os.path.join(data_path, "skinpatch.xml")
        if os.path.isfile(xml_path):
            xml = et.parse(xml_path).getroot()
            old = xml.find("skin[@id='{0}']".format(self.skin_id))
            if old is not None:
                xml.remove(old)
        else:
            xml = et.Element("skinpatch")
        if self.status != STATUS_CLEAN:
            skin = et.Element("skin", attrib={"id": self.skin_id})
            patch = et.Element("patch", attrib={"version": self.version})
            patch.text = self.patch
            skin.append(patch)
            for path, check in self.files:
                file = et.Element("file", attrib={"check": check})
                file.text = path
                skin.append(file)
            xml.append(skin)
        et.ElementTree(xml).write(xml_path, encoding="utf-8")


def autoremove():
    xml_path = os.path.join(data_path, "skinpatch.xml")
    if os.path.isfile(xml_path):
        xml = et.parse(xml_path).getroot()
        for skin in xml.findall("skin"):
            SkinPatch(skin.attrib["id"]).revert()
        xbmc.executebuiltin("ReloadSkin()")
        xbmc.sleep(1000)


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
