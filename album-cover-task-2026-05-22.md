# Album Cover Download Task - 2026-05-22

## Objective
Execute the daily album cover download heartbeat task (download 10 covers by ranking).

## Issue Encountered

### 1. PowerShell Syntax Error (Original Command)
- **Error**: Original async command used `&&` as command separator
- **Cause**: `&&` is bash/CMD syntax; PowerShell uses `;` or newlines
- **Fix**: Re-ran command with `;` separator: `cd "...\album-tracker"; node dist/download-covers.js --count 10`

### 2. Script Found 0 Covers to Download
- **Script output**: `找到 0 张需要封面的专辑（offset=0, count=10）`
- **Result**: 0 covers downloaded (0 success, 0 failed)
- **Discrepancy**: `heartbeat-state.json` shows `covers_remaining: 279`, indicating 279 albums still need covers

## Investigation Findings

### Script Query Logic
The script (`./dist/download-covers.js`) queries:
```sql
SELECT album_id, album_name, artist, total_listen_count, rating
FROM albums
WHERE cover_image_url IS NULL OR cover_image_url = ''
ORDER BY total_listen_count DESC, rating DESC
LIMIT ? OFFSET ?
```

### Database Status
- **Database path**: `G:\原创计划\music` (282KB sql.js format file)
- **G: drive status**: Mounted and accessible
- **File timestamp**: 2026/5/22 17:10:15 (recently modified)

### Possible Causes for Discrepancy
1. **Column mismatch**: The state file may be tracking `cover_path` field, - The script queries `cover_image_url` column
   - The state file mentions `cover_path` 
2. **All covers already downloaded**: The 279 "remaining" in state file may be outdated
3. **Database not properly loaded**: sql.js may be loading empty/in-memory database if file read fails
4. **Wrong table**: Script queries `albums` table; 

## Recommendations
1. **Verify database schema**: Check if `cover_image_url` column exists in `albums` table
2. **Check actual count**: Query database directly to count albums with/without cover_image_url
3. **Sync state file**: Update `heartbeat-state.json` if the 279 remaining is outdated
4. **Check script logic**: Verify the script is actually reading from `G:\原创计划\music` and not falling back to empty database

## Commands to Debug
```powershell
# Check database schema and counts
cd "C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"
# Need to write a debug script using sql.js to inspect the database
```

## Next Steps
- Investigate database schema to understand the discrepancy
- Update heartbeat task to properly track and download remaining covers
- Consider if covers_remaining: 279 in state file is accurate

## Technical Details
- **Shell**: PowerShell (not bash/CMD)
- **Database**: sql.js (client-side SQLite, not better-sqlite3)
- **Script**: TypeScript compiled to dist/download-covers.js
- **State file**: `C:\Users\qujt\.qclaw\workspace\heartbeat-state.json`
