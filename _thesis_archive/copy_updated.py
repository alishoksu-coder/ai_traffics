# -*- coding: utf-8 -*-
import shutil, os

src = 'Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted_UPDATED.docx'
dst = 'Suleimenov_Alisher_VTIPO-45_REPORT_GOST_formatted.docx'

try:
    shutil.copy2(src, dst)
    print('SUCCESS: Updated file copied to original name.')
except Exception as e:
    print(f'File is locked (probably open in Word).')
    print(f'Please CLOSE "{dst}" in Word, then rerun this script.')
    print(f'Or simply open the updated file directly:')
    print(f'  {os.path.abspath(src)}')
