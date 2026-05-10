import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.test import Client

def main():
    c=Client()
    paths=['/productos/','/pedidos/','/ventas/','/reclamos/']
    for p in paths:
        r=c.get(p)
        print(p, r.status_code)

if __name__=='__main__':
    main()
