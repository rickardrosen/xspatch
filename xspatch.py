#!/usr/bin/python

import xml.dom.minidom as md
import urllib
from subprocess import call
import os

UPDATES_URL = 'http://updates.xensource.com/XenServer/updates.xml'
PATCH_DOWNLOAD_DIR = '/tmp/xspatch.py/'
PATCHES_TO_DOWNLOAD_FILE = PATCH_DOWNLOAD_DIR + 'urllist'
PATCHES_TO_APPLY = []

def create_patchdir():
        d = os.path.dirname(PATCH_DOWNLOAD_DIR)
        if not os.path.exists(d):
                os.makedirs(d)

#def updates for xsversion(version):

def create_patch_list():
        file = open(PATCHES_TO_DOWNLOAD_FILE, 'w')
        dom = md.parse(urllib.urlopen(UPDATES_URL))
        availableVersions = dom.getElementsByTagName('version')
        availablePatches = dom.getElementsByTagName('patches')
	patchUrlDict = {}
        for patch in availablePatches:
                allPatches = patch.getElementsByTagName('patch')
                for ap in allPatches:
                        patchUrlDict.update({ap.getAttribute('uuid'):ap.getAttribute('patch-url')})

        for version in availableVersions:
                if version.getAttribute('value')=='6.1':
                        versionSpecificPatches = version.getElementsByTagName('patch')
                        for patch in versionSpecificPatches:
                                patchToDownload = patchUrlDict.get(patch.getAttribute('uuid'))
                                file.write(patchToDownload + '\n')
				PATCHES_TO_APPLY.append(patch.getAttribute('uuid'))
        file.close()

def download_patches():
        call(["wget", "-nc", "-i", PATCHES_TO_DOWNLOAD_FILE, "-P", PATCH_DOWNLOAD_DIR])

def prepare_patches():
        os.chdir(PATCH_DOWNLOAD_DIR)
        call(["unzip", PATCH_DOWNLOAD_DIR + "*.zip"])
        for file in os.listdir(PATCH_DOWNLOAD_DIR):
                if file.endswith(".xsupdate"):
			print file
                        call(["xe", "patch-upload", "file-name=" + file])

def apply_patches():
        for uuid in PATCHES_TO_APPLY:
                call(["xe", "patch-pool-apply", "uuid=" + uuid])



create_patchdir()
create_patch_list()
download_patches()
prepare_patches()
apply_patches()
