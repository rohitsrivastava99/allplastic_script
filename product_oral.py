import csv
# import xlrd

import psycopg2
import re

conn = psycopg2.connect("dbname='ajuly' user='postgres' host='localhost' password='123'")
cursor = conn.cursor()
reader = csv.reader(open('/home/rohit/allplastic_script/oral.csv', 'rb'))
reader.next()
values = {}
field = cursor.execute("""select id from ir_model_fields where model='product.product' and name='standard_price'""")
field = cursor.fetchone()[0]
product_category_id = 1
color_code = 1
ap_discount = 0.0
for row in reader:
    if row:
        if row[3]:
            row[3] = str(row[3])
            category = cursor.execute("""select id from product_category where name='%s'""" % row[3])
            category = cursor.fetchone()
            # conn.commit()
            # if category:
            #     product_category_id = category
            # else:
            if category is None:
                vals = {'name': row[3], 'parent_id': 1}
                cursor.execute("""insert into product_category(name)values(%(name)s) RETURNING id""", (vals))
                conn.commit()
                id = cursor.fetchone()[0]
                product_category_id = id
                print "Product Category : ", product_category_id
            else:
                product_category_id = category
            # Cost inc/exc GST
        if row[13]:
            cost = str(row[13]).replace(',', '')
        # Discount
        if row[7]:
            ap_discount = str(row[7]).replace(',', '')
            if ap_discount in ['- ']:
                ap_discount = 0.0
            else:
                ap_discount = 0.0
        # UOM
        if row[16]:
            row[16] = str(row[16])
            cursor.execute("""select id from product_uom where name='%s'""" % row[16])
            puom_id = cursor.fetchone()
        if row[17]:
            row[17] = str(row[17])
            cursor.execute("""select id from product_uom where name='%s'""" % row[17])
            uom_id = cursor.fetchone()
        if row[25]:
            row[25] = str(row[25])
            if row[25] in ['Roll', 'Rod', 'Acrylic', 'Ball', 'Cylinder', 'Each', 'Extrusion', 'Natural', 'Sheet', 'Form', 'Tube','Cartridge']:
                form = row[25].lower()
            elif row[25] in ['Rod Cast', 'Tube Extruded', 'Rod Extruded']:
                form = row[25].replace(' ', '_').lower()
            else:
                form = 'sheet_roll'
        if row[26]:
            row[26] = str(row[26])
            try:
                row[26] = str(row[26])
                colors = cursor.execute("""select id from color_master where name='%s'""" % row[26])
                colors = cursor.fetchone()
                if colors is None:
                    vals = {'name': row[26]}
                    cursor.execute("""insert into color_master(name)values(%(name)s) RETURNING id""", (vals))
                    conn.commit()
                    id = cursor.fetchone()[0]
                    color_code = id
                    print "New Color Created : ", color_code
                else:
                    color_code = colors
                    print "Color exist : ", color_code
            except ValueError:
                pass
        row_thick = 0.0
        if row[24]:
            row_thick = float(row[24].split('m')[0])
        barcode = ''
        if row[1]:
            barcode = row[1]
        if row[4]:
            if row[4] == '1.00':
                row[4] = True
        if row[5]:
            if row[5] == '1.00':
                row[5] = True
        values = {
            'name': str(row[2]),                     # template
            'active': True,                     # variant
            'uom_po_id': puom_id or 20,         # template
            'uom_id': uom_id or 20,             # template
            'categ_id': product_category_id,    # template row[3]
            'type': 'product',                  # template
            'sale_line_warn': 'no-message',     # template
            'purchase_line_warn': 'no-message',  # template
            'tracking': 'none',                 # template
            'sale_ok': str(row[4]),                  # template
            'purchase_ok': str(row[5]),              # template
            'list_price': str(row[20]) or 0.0,
            'description': str(row[9]) or None,      # template
            'default_code': str(row[0]) or '',       # variant
            # 'barcode': row[1],                # variant
            # 'standard_price': row[6],
            'ap_discount': ap_discount,         # template
            'prod_height': str(row[21]) or None,     # variant
            'prod_width': str(row[22]) or None,      # variant
            'thickness': str(row[23]) or None,       # variant
            'wall_thickness': row_thick,        # variant
            'form': form,                       # variant
            'colour_code': color_code,          # variant
        }
        cursor.execute("""INSERT INTO product_template(
            name, active, uom_id, uom_po_id,
            categ_id, type, sale_line_warn,
            purchase_line_warn, tracking,
            sale_ok, purchase_ok, list_price,
            description, default_code, ap_discount,
            prod_height, prod_width, thickness,
            wall_thickness, form, colour_code
        ) values(
            %(name)s, %(active)s, %(uom_id)s, %(uom_po_id)s,
            %(categ_id)s, %(type)s, %(sale_line_warn)s,
            %(purchase_line_warn)s, %(tracking)s, %(sale_ok)s,
            %(purchase_ok)s, %(list_price)s, %(description)s,
            %(default_code)s, %(ap_discount)s,
            %(prod_height)s, %(prod_width)s,
            %(thickness)s, %(wall_thickness)s,
            %(form)s, %(colour_code)s
        ) RETURNING id;""" , (values))
        product_template = cursor.fetchone()[0]
        conn.commit()
        print "Product Template : ", product_template
        product_values = {
            'product_tmpl_id': str(product_template),
            'barcode': str(barcode),
            'active': 'True',
        }
        if barcode == '':
            cursor.execute("""INSERT INTO product_product(product_tmpl_id, active) VALUES (%(product_tmpl_id)s, %(active)s) RETURNING id""", (product_values))
        else:
            cursor.execute("""select id from product_product where barcode='%s'""" % barcode)
            cursor_fetchone = cursor.fetchone()
            if cursor_fetchone is None:
                cursor.execute("""INSERT INTO product_product(product_tmpl_id, barcode, active) VALUES (%(product_tmpl_id)s, %(barcode)s, %(active)s) RETURNING id""", (product_values))
            else:
                product_values = {
                    'product_tmpl_id': str(product_template),
                    'barcode': str(barcode) + '1',
                    'active': 'True',
                 }
                cursor.execute("""INSERT INTO product_product(product_tmpl_id, barcode, active) VALUES (%(product_tmpl_id)s, %(barcode)s, %(active)s) RETURNING id""", (product_values))
        # cursor.execute(statement)
        product_product = cursor.fetchone()[0]
        conn.commit()
        print "Product : ", product_product
        if product_template and row[12]:
            row[12] = str(row[12])
            cursor.execute("""select id from res_partner where linking=%s""" % row[12])
            cursor_fetchone = cursor.fetchone()
            if cursor_fetchone is not None:
                partner_id = cursor_fetchone[0]
                if row[13]:
                    price = row[13]
                else:
                    price = 0.0
                supplier_values = {
                    'name': partner_id,
                    'product_tmpl_id': product_template,
                    'delay': 0,
                    'currency_id': 22,
                    'min_qty': 0,
                    'price': price,
                }
                cursor.execute("""insert into product_supplierinfo(
                    name, product_tmpl_id, delay, currency_id, min_qty, price)
                    values(
                    %(name)s, %(product_tmpl_id)s, %(delay)s, %(currency_id)s, %(min_qty)s, %(price)s) RETURNING id""", (supplier_values))
                conn.commit()
                print "Suppler Set on Product"

        if product_template and product_category_id:
            product_categ_rel_values = {
                'product_id': product_template,
                'categ_id': product_category_id,
            }
            cursor.execute("""insert into product_categ_rel(
                product_id, categ_id)
                values(
                %(product_id)s, %(categ_id)s) RETURNING *""", (product_categ_rel_values))
            conn.commit()
            print "Extra category Set on Product"

        if cost in ['- ']:
            pass
        else:
            values_2 = {
                'name': 'standard_price',
                'res_id': 'product.product,%s' % product_product,
                'fields_id': field,
                'type': 'float',
                'value_float': cost,
            }
            cursor.execute("""insert into ir_property(name, res_id, fields_id, type, value_float)
                values(%(name)s, %(res_id)s, %(fields_id)s, %(type)s, %(value_float)s)""", (values_2))
            conn.commit()
            print "Standard Price Set."
        cursor.execute("""select id from stock_location_route where name='Buy'""") 
        buy_route_id = cursor.fetchone()[0]
        buy_route = {
                'product_id': product_template,
                'route_id': buy_route_id,
            }
        cursor.execute("""insert into stock_route_product(
            product_id, route_id)
            values(
            %(product_id)s, %(route_id)s) RETURNING *""", (buy_route))
        conn.commit()
        cursor.execute("""select id from stock_location_route where name='Make To Order'""") 
        mto_id =  cursor.fetchone()[0]
        mto_route = {
                'product_id': product_template,
                'route_id': mto_id,
            }
        cursor.execute("""insert into stock_route_product(
            product_id, route_id)
            values(
            %(product_id)s, %(route_id)s) RETURNING *""", (mto_route))
        conn.commit()
