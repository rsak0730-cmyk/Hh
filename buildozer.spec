[app]

# (str) Title of your application
title = Mira Astra

# (str) Package name
package.name = miraastra

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mira

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
# Using pure-python requests stack to prevent pydantic_core compilation errors
requirements = python3,kivy,pillow,requests,urllib3,chardet,idna

# (str) Application versioning
version = 1.0.0

# (list) Permissions
android.permissions = INTERNET,WRITE_SECURE_SETTINGS,SYSTEM_ALERT_WINDOW,RECORD_AUDIO

# ------------------------------------------------------
# Android 15 (API Level 35) Target Configuration
# ------------------------------------------------------
# (int) Target Android API, set to 35 for Android 15 support
android.api = 35

# (int) Minimum API your APK will support (Android 8.0 Oreo)
android.minapi = 26

# (int) Android SDK version to use
android.sdk = 35

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android SDK
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a

# (bool) Allow full backup
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
