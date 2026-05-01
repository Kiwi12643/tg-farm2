[app]
title = TG Multi-Tool
package.name = tgfarm
package.domain = org.tgfarm
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
version = 1.0
requirements = python3,kivy==2.3.0,kivymd==2.0.1,telethon==1.36.0,requests,pysocks,cryptg
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,VIBRATE
android.api = 34
android.minapi = 24
android.ndk = 25c
android.sdk = 34
android.gradle_dependencies = 
android.add_src = 
android.arch = arm64-v8a
android.allow_backup = True
android.logcat_filters = *:S python:D
ios.kivy_version = 2.3.0

[buildozer]
log_level = 2
warn_on_root = 1