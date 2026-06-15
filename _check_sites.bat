@echo off
curl.exe -s -L -m 8 -o nul -w "discogs.com: %%{http_code}\n" "https://discogs.com"
curl.exe -s -L -m 8 -o nul -w "bandcamp.com: %%{http_code}\n" "https://bandcamp.com"
curl.exe -s -L -m 8 -o nul -w "musicbrainz.org: %%{http_code}\n" "https://musicbrainz.org"
curl.exe -s -L -m 8 -o nul -w "en.wikipedia.org: %%{http_code}\n" "https://en.wikipedia.org"
curl.exe -s -L -m 8 -o nul -w "api.discogs.com: %%{http_code}\n" "https://api.discogs.com"
