# ntfsafe.py

A little script for creating a symlink tree for copying files to NTFS that deals with names that collide due to comparing equal in case-insensitive NTFS. Permissions and ownership are also added to the filename, and a '.LONG' file containing the original filename is created when the resulting filename would exceed the NTFS 255 character limit.