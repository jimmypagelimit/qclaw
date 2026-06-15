@echo off
curl.exe -s -L -m 15 -A "AlbumTracker/1.0" -w "\nHTTP: %%{http_code}\n" "https://musicbrainz.org/ws/2/artist/?query=artist:car+seat+headrest&fmt=json&limit=1"
