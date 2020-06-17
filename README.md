# mfcmd.py - MediaFire uploader

**Quick python3 script to upload files to MediaFire**

```
mfcmd.py -e <MediaFireEMail> -p <MediaFirePassword> [-u <RemoteUploadFolder>] [-h <FileSHA256Checksum>] -f <Filepath>
```

## Notes
* use double quotes if e.g. your password contains special characters
* redirect `stderr` to `null` to only print the final download URL
* the MediaFire API is pretty buggy, and you might receive an error, because the server hasn't finished calculating the file's checksum yet; in that case, wait a couple of seconds (depending on the filesize) and repeat the command: it will not upload, but instead detect the already uploaded file and return the download URL

## Requisites
* **python3** (might also work with python@2)
* **pymediafire** (REST API)
* **mediafire** (SDK)

## More information
https://www.mediafire.com/developers/core_api/1.5

https://pypi.org/project/mediafire/

https://github.com/MediaFire/mediafire-python-open-sdk

