import csv
import psycopg2
import re

conn = psycopg2.connect("dbname='ajuly' user='postgres' host='localhost' password='123'")
cursor = conn.cursor()
reader = csv.reader(open('/home/rohit/allplastic_script/supplier.csv','rb'))
reader.next()
values = {}
list = []
for row in reader:
    # import pdb;pdb.set_trace();
    name = str(row[0])
    if row[0]:
        cursor_fetchone = cursor.execute("""select * from res_partner where name='%s'"""%row[0])
        if cursor_fetchone is None:
            vals = {
                    'name': str(row[0]),
                    'notify_email':'no-message', 
                    'invoice_warn': 'no-message',
                    'sale_warn': 'no-message', 
                    'picking_warn': 'no-message',
                    'purchase_warn':'no-message',
                    'active':True,
                    'supplier':True,
                    'display_name':str(row[0]),
                    'linking': row[1]
                    }
            cursor.execute("""insert into res_partner (name, 
                notify_email,
                invoice_warn,
                sale_warn,
                picking_warn,
                purchase_warn,
                active,
                supplier,
                display_name,
                linking
                )values(%(name)s,
                 %(notify_email)s,
                 %(invoice_warn)s,
                 %(sale_warn)s,
                 %(picking_warn)s,
                 %(purchase_warn)s,
                 %(active)s,
                 %(supplier)s,
                 %(display_name)s,
                 %(linking)s
                 ) RETURNING id""",(vals))
            partner_id = cursor.fetchone()[0]
            conn.commit()
        else:
            print "================cr=",cursor.fetchone()[0]