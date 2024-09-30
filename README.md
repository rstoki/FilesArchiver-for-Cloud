# FilesArchiver for Cloud

This is a small tool that is able to look for directories with many (possibly small) files and archive them into ZIP archive, such that it is more suitable to synchronize using cloud services, e.g., Synology Drive, OwnCloud, OneDrive, Dropbox, etc.

## Motivation

When synchronizing my work between computers using some cloud services like Synology Drive, CERNbox, OwnCloud, Dropbox, OneDrive, etc., storing and synchronizing thousands of small files individually is very inefficient. 
This overhead and performance penalty is especially not needed when these small files are kept only for "archiving purposes" (for example, as some results of an experiment or some generated results from the past). 

This tool tries to help with this problem in the following way:
 - it localizes directories with a lot of files
 - it can move those files into a single ZIP file, which is easy to synchronize


