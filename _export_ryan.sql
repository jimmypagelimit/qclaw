-- Ryan Beatty - Sweet Fortune (album_id=598)
BEGIN;

-- 艺人
INSERT OR IGNORE INTO artists (artist_id, name, country, is_active)
VALUES (327, 'Ryan Beatty', 'US', 1);

-- 专辑
INSERT OR IGNORE INTO albums (album_id, artist, album_name, release_year, release_mbid, cover_image_url, status, artist_id)
VALUES (598, 'Ryan Beatty', 'Sweet Fortune', 2026, 'bab213e5-a0fe-42a2-b402-de1469203901', '/covers/598-Ryan Beatty-Sweet Fortune.jpg', 'active', 327);

-- 收听记录
INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source)
VALUES (598, date('now'), strftime('%Y', 'now'), '入库', 'manual');

-- 曲目（10首）
INSERT OR IGNORE INTO tracks (album_id, track_name, track_number, duration, source) VALUES
(598, 'Phantom', 1, 223000, 'musicbrainz'),
(598, 'White Lightning', 2, 265000, 'musicbrainz'),
(598, 'Virtuoso', 3, 222000, 'musicbrainz'),
(598, 'Secret Language', 4, 234000, 'musicbrainz'),
(598, 'Sweet Fortune', 5, 176000, 'musicbrainz'),
(598, 'Too Many Ways', 6, 234000, 'musicbrainz'),
(598, 'Delancey', 7, 222000, 'musicbrainz'),
(598, 'Annie, Anything', 8, 213000, 'musicbrainz'),
(598, 'Dust', 9, 189000, 'musicbrainz'),
(598, 'Fleur De Lis', 10, 293000, 'musicbrainz');

COMMIT;
