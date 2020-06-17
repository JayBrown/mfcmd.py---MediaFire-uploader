#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mfcmd.py
# MediaFire uploader
# v0.2

# EXECUTE
# mfcmd.py -e <MediaFireEMail> -p <MediaFirePassword> [-u <RemoteUploadFolder>] [-h <FileSHA256Checksum>] -f <Filepath>
# note: use double quotes if e.g. your password contains special characters

# MORE INFO
# https://www.mediafire.com/developers/core_api/1.5
# https://pypi.org/project/mediafire/
# https://github.com/MediaFire/mediafire-python-open-sdk

import getopt, hashlib, os, sys, time
from mediafire import MediaFireApi
from mediafire.client import (File, Folder, MediaFireClient)

def main(argv):

	vnumber = "0.2"
	print('mfcmd.py v' + vnumber, file=sys.stderr)

	account = ''
	passphrase = ''
	filepath = ''
	filepathbase = ''
	filesize = ''
	localhash = ''
	uldir = ''

	try:
		opts, args = getopt.getopt(argv,"e:p:u:h:f:",["email=","password=","upload-folder=","hash=","file="])
	except getopt.GetoptError:
		print('Error!', file=sys.stderr)
		return

	for opt, arg in opts:
		if opt in ("-e", "--email"):
			account = arg
		elif opt in ("-p", "--password"):
			passphrase = arg
		elif opt in ("-u", "--upload-folder"):
			uldir = arg
		elif opt in ("-s", "--size"):
			filesize = arg
		elif opt in ("-h", "--hash"):
			localhash = arg
		elif opt in ("-f", "--file"):
			filepath = arg

	if account == '':
		print('Error:credentials')
		return
	else:
		print('Email: ' + account, file=sys.stderr)

	if passphrase == '':
		print('Error:credentials')
		return
	else:
		print('Password: ' + passphrase, file=sys.stderr)

	if filepath == '':
		print('Error:filepath')
		return
	else:
		if os.path.exists(filepath):
			if os.path.isfile(filepath):
				print('Filepath: ' + filepath, file=sys.stderr)
				filepathbase = os.path.basename(filepath)
				print('Filename: ' + filepathbase, file=sys.stderr)
			else:
				print('Error:noregularfile')
				return
		else:
			print('Error:nofile')
			return

	if uldir == '':
		uldir = 'mfcmd'
	print('Upload folder: ' + uldir, file=sys.stderr)

	if localhash == '':
		print('No SHA-256 specified: calculating...', file=sys.stderr)
		sha256_hash = hashlib.sha256()
		with open(filepath,"rb") as f:
			for byte_block in iter(lambda: f.read(4096),b""):
				sha256_hash.update(byte_block)
			localhash = sha256_hash.hexdigest()
	print('Checksum: ' + localhash, file=sys.stderr)

	api = MediaFireApi()

	try:
		session = api.user_get_session_token(
			email=account,
			password=passphrase,
			app_id='42511')
		print('MediaFire API: connected', file=sys.stderr)
	except:
		print('Error:login')
	api.session = session

	try:
		userinfo = api.user_get_info()
		print("Account holder: " + userinfo['user_info']['display_name'], file=sys.stderr)
		maxstore = userinfo['user_info']['storage_limit']
		usedstore = userinfo['user_info']['used_storage_size']
		freestore = int(maxstore)-int(usedstore)
		freestore_str = str(freestore)
		print("Maximum storage: " + maxstore, file=sys.stderr)
		print("Used storage: " + usedstore, file=sys.stderr)
		print("Free storage: " + freestore_str, file=sys.stderr)
		localsize = os.path.getsize(filepath)
		localsize_str = str(localsize)
		print("Local file size: " + localsize_str, file=sys.stderr)
		if freestore <= localsize:
			print("Error: available space will not suffice!", file=sys.stderr)
			print("Error:space")
			return
		else:
			print("Available filespace will suffice", file=sys.stderr)
	except:
		print('Error getting or parsing user info', file=sys.stderr)

	client = MediaFireClient()

	try:
		client.login(email=account,
			password=passphrase,
			app_id='42511')
		print('MediaFire Client: logged in', file=sys.stderr)
	except:
		print('Error:login')
		return

	try:
		client.get_resource_by_path("/" + uldir + "/")
		print('Detected upload folder ./' + uldir, file=sys.stderr)
	except:
		print('Error: upload folder ./' + uldir, 'does not exist!', file=sys.stderr)
		try:
			client.create_folder("mf:/" + uldir)
		except:
			print('Could not create upload folder: defaulting to root', file=sys.stderr)
			uldir = ''

	try:
		if uldir == '':
			fileinfo = client.get_resource_by_path("/" + filepathbase)
			remotehash = fileinfo['hash']
			if localhash == remotehash:
				print('Same file already exists: no upload necessary!', file=sys.stderr)
				try:
					dlurl = fileinfo['links']['normal_download']
					dlurl = dlurl.replace('http://www.', 'https://')
					print(dlurl)
				except:
					print('Error:link')
				return
			else:
				print('Error: filename already exists in upload folder', file=sys.stderr)
				posixtime = int(time.time())
				posixtext = str(posixtime)
				uldir = posixtext
				print('Creating root subfolder: /' + uldir, file=sys.stderr)
				try:
					client.create_folder("mf:/" + uldir)
				except:
					print('Error:folder')
					return
		else:
			fileinfo = client.get_resource_by_path("/" + uldir + "/" + filepathbase)
			remotehash = fileinfo['hash']
			if localhash == remotehash:
				print('Same file already exists: no upload necessary!', file=sys.stderr)
				try:
					dlurl = fileinfo['links']['normal_download']
					dlurl = dlurl.replace('http://www.', 'https://')
					print(dlurl)
				except:
					print('Error:link')
				return
			else:
				print('Error: filename already exists in upload folder', file=sys.stderr)
				posixtime = int(time.time())
				posixtext = str(posixtime)
				uldir = uldir + '/' + posixtext
				print('Creating subfolder: ./' + uldir, file=sys.stderr)
				try:
					client.create_folder("mf:/" + uldir)
				except:
					print('Could not create upload folder: defaulting to root', file=sys.stderr)
					uldir = ''
	except:
		print('File does not exist in upload folder', file=sys.stderr)

	try:
		if uldir == '':
			client.upload_file(filepath, "mf:/")
		else:
			client.upload_file(filepath, "mf:/" + uldir + "/")
	except:
		print('Error: upload function', file=sys.stderr)

	try:
		if uldir == '':
			fileinfo = client.get_resource_by_path("/" + filepathbase)
		else:
			fileinfo = client.get_resource_by_path("/" + uldir + "/" + filepathbase)
		dlurl = fileinfo['links']['normal_download']
		dlurl = dlurl.replace('http://www.', 'https://')
		print(dlurl)
	except:
		print('Error:upload')
		return

if __name__ == "__main__":
	main(sys.argv[1:])

print("Done.", file=sys.stderr)
sys.exit(1)
