# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import urllib2
import sys
from PIL import Image

if len(sys.argv) == 3:
    from_code = sys.arv[1]
    to_code = sys.arv[2]
elif len(sys.argv) == 2:
    from_code = sys.arv[1]
    to_code = sys.arv[1] + 1
else:
    sys.exit()

def _sscc_check_digit(fixed):
    ''' Generate check digit and return
    '''
    tot = 0
    pos = 0    
    for c in fixed:
        pos+=1
        number = int(c)
        if pos % 2 == 0 :
            tot += number
        else:
            tot += number*3
    
    remain = tot % 10
    if remain:
        return 10 - remain 
    else: 
        return 0

for i in range(from_code, to_code):#(1000000000)
    sscc = '38004766%09d' % i
    sscc = '%s%s' % (sscc, _sscc_check_digit(sscc))
    
    url = 'http://barcode.tec-it.com/barcode.ashx?translate-esc=on&data=(00)%s&code=GS1_128CCA&unit=Fit&dpi=96&imagetype=Gif&rotation=0&color=000000&bgcolor=FFFFFF&qunit=Mm&quiet=0' % sscc
    file_name = '%s.gif' % sscc
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders('Content-Length')[0])
    print 'Downloading: %s Bytes: %s' % (file_name, file_size)
    
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
            
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (
            file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,
    f.close()
    
    # Crop image:
    img = Image.open(file_name)
    width = img.size[0]
    height = img.size[1]
    img2 = img.crop((0, 0, width, 127))
    img2.save(file_name)

'''
import barpy
a = barpy.GS1128('(00)380047660000000017', 'B', 'gs1')
f = open('gs1.png', 'w')
f = open('gs1.png', 'w')
f.write(a.to_png())
f.close()

'''    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
