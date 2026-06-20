#!/usr/bin/env python3
"""只写入 19 条候选 MBID（不搜索）"""
import sqlite3

DB_PATH = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'

CANDIDATES = [
    (2,   'b32a3330-dcdf-4b3e-966b-32bd5b87ca28'),
    (550, '81d44b2f-edd1-447e-bcd3-633aba22afab'),
    (303, 'bd025f4b-ef9c-38a9-8beb-db8bd69d35bc'),
    (168, '90782b04-4e9b-4c22-880d-84a2a56b72fd'),
    (6,   'd05e9340-e542-486f-af69-48ffc8e4caa2'),
    (95,  'e0135bcb-268f-48f8-80f5-fb5eaf98d654'),
    (10,  '87ef0dea-df13-49ef-98e7-b2a9ddbdd005'),
    (333, 'ec3ac7bc-8500-3b0f-a6a4-fbb868c5ea3d'),
    (159, 'af8f3eb8-3fdb-3215-8fb7-c7545fe2cd70'),
    (185, 'cc2c1881-2fd1-4c4d-a59f-9a99881a03b1'),
    (337, '5a5f75ff-0a46-4c90-91a0-ba2ca7f969c9'),
    (368, 'b08f795d-5604-4ab8-b260-a5e61d5d416a'),
    (246, 'b227b6b5-ef55-427b-b851-3bc9fdfefeda'),
    (38,  '6e3e6f3c-4d19-4022-ba6b-5d4095bd911f'),
    (276, 'aeaecbec-556d-3b72-bfdf-dda0637db940'),
    (279, 'c6af3dfb-e48a-4d3f-b184-dbfc1863f384'),
    (142, 'b051325c-9031-3914-8965-aefbd2bff919'),
    (410, '2ce80082-c8f0-36ba-bd30-d6a3021a2bc9'),
    (275, '59f8c580-f50a-4c2c-b810-dec0d6c4b864'),
]

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA journal_mode=WAL')
c = conn.cursor()

updated = 0
for aid, mbid in CANDIDATES:
    c.execute("UPDATE albums SET release_mbid = ? WHERE album_id = ?", (mbid, aid))
    if c.rowcount > 0:
        updated += 1

conn.commit()

# 验证
c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NOT NULL AND release_mbid != ''")
has_mbid = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM albums")
total = c.fetchone()[0]

print(f"已写入: {updated} 条")
print(f"当前覆盖率: {has_mbid}/{total} = {has_mbid/total*100:.1f}%")

conn.close()
