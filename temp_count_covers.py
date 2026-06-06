import sqlite3, os

db_file = r'G:\原创计划\music\database.sqlite'

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM albums')
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
with_cover = cursor.fetchone()[0]

remaining = total - with_cover
print('total: ' + str(total))
print('with_cover: ' + str(with_cover))
print('remaining: ' + str(remaining))

conn.close()
