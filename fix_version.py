path = r'C:\Users\frank\.openclaw\workspace\jrebel-license-server\app\main.py'
data = open(path, encoding='utf-8', errors='ignore').read()
count = data.count('"serverVersion": "2024.3.0"')
data = data.replace('"serverVersion": "2024.3.0"', '"serverVersion": "3.2.4"')
open(path, 'w', encoding='utf-8').write(data)
print(f'Replaced {count} occurrences')
