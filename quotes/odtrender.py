import subprocess
import uno
import os
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.awt import Size
from django.db.models import Sum
from . import views
import decimal
import time

#2 decimal places for everything
#align right
#make left column bigger
#centre totals


# V2 - make it optional whether days or hoursin amount
# download odt button
# save to pdf button
#choose from existing customers or add new

class QuoteRenderer:

    def __init__(self, quote):
        print("About to open process")
        self.p2 = subprocess.Popen(("soffice", "--writer", '--accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"', "--headless"))
        print("process is open, zzz")
        time.sleep(20)
        print("Yawn")
        self.quote = quote

    def render(self):
        self.connect()

        self.find_replace("{{client}}", self.quote.client) #
        self.find_replace("{{title}}", self.quote.title)

        subtotal = self.quote.lineitem_set.aggregate(Sum('amount'))['amount__sum']

        #for item in self.quote.lineitem_set.all():
        #    print (item.description, item.amount, item.quote, item.quote_id)

        self.insert_quote_table(self.quote.lineitem_set.all(), self.quote.title, subtotal)

        print (self.quote.conditions)
        if self.quote.conditions == 'Catalyst Standard Terms':
            text1 = "This quote is proposed under the assumption that both parties accept and agree that the scope, services and standards of quality for the project are accepted. Parties acknowledge and accept "
            link = "http://catalyst-eu.net/terms"
            linkwords = "Catalyst's standard Terms and Conditions[1]"
            text2 = ", notes, obligations and assumptions."
        else:
            text1 = "This quote is proposed under the assumption that parties accept and agree the scope, services and standards of quality outlined here. Parties acknowledge and accept "
            link = "https://assets.digitalmarketplace.service.gov.uk/g-cloud-9/documents/579028/520395179658286-terms-and-conditions-2017-04-07-1042.pdf"
            linkwords = "Catalyst's Digital Marketplace standard Terms and Conditions"
            text2 = ", notes, obligations and assumptions."

        self.insert_hyperlink_text(text1, link, linkwords, text2)
        self.save()

    def insert_quote_table(self, line_items, title, total_amount):
        grey = 0xCCCCCC

        if self.quote.currency == 'GBP':
            symbol = '£'
        elif self.quote.currency == 'EUR':
            symbol = '€'
        elif self.quote.currency == 'USD':
            symbol = '$'
        else:
            symbol = 'currency symbol is broken'

        #header for table
        rows = len(line_items) + 5
        table = self.insert_table_at_end(rows, 2, title) #(rows, columns)
        table_rows = table.Rows
        header_row = table_rows.getByIndex(0)
        header_row.setPropertyValue( "BackColor", grey)

        self.set_table_cell(table, "A1", 'Item', {"ParaStyleName": "Catalyst - Table header"})
        self.set_table_cell(table, "B1", 'Cost exc VAT (in {})'.format(self.quote.currency), {"ParaStyleName": "Catalyst - Table header"})

        #for item in self.quote.lineitem_set.all():
        #    print (item.description, item.amount, item.quote, item.quote_id)

        #line items for table
        row = 2
        for item in line_items:
            amount = round(decimal.Decimal(item.amount), 2)
            self.set_table_cell(table, "A{}".format(row), item.description, {"ParaStyleName": "Catalyst - Table contents"})
            self.set_table_cell(table, "B{}".format(row), "{}{}".format(symbol, amount), {"ParaStyleName": "Catalyst - Table contents"})
            row += 1

        #subtotal
        new_row = table_rows.getByIndex(row - 1)
        new_row.setPropertyValue("BackColor", grey)
        self.set_table_cell(table, "A{}".format(row), 'Subtotal (exc VAT)', {"ParaStyleName": "Catalyst - Table header"})
        self.set_table_cell(table, "B{}".format(row), "{}{}".format (symbol, round(decimal.Decimal(total_amount), 2)), {"ParaStyleName": "Catalyst - Table header"}
        )
        row += 1

        print (self.quote.pm)
        percent = self.quote.pm/100
        print (percent)
        project_management = total_amount*percent

        #project management line
        new_row = table_rows.getByIndex(row - 1)
        self.set_table_cell(table, "A{}".format(row), 'Project Management Fee {}%'.format(self.quote.pm), {"ParaStyleName": "Catalyst - Table contents"})
        self.set_table_cell(table, "B{}".format(row), "{}{}".format(symbol, round(decimal.Decimal(project_management), 2)), {"ParaStyleName": "Catalyst - Table contents"})
        row += 1

        #VAT line
        if self.quote.vat:
            vat_line = 'VAT (20%)'
            print (total_amount, project_management)
            VAT = (total_amount + project_management)*0.20
        else:
            vat_line = 'VAT (not applicable)'
            VAT = 0

        new_row = table_rows.getByIndex(row - 1)
        self.set_table_cell(table, "A{}".format(row), vat_line, {"ParaStyleName": "Catalyst - Table contents"})
        self.set_table_cell(table, "B{}".format(row), "{}{}".format(symbol, round(decimal.Decimal(VAT), 2)), {"ParaStyleName": "Catalyst - Table contents"})
        row += 1

        total = total_amount + project_management + VAT

        #total line
        new_row = table_rows.getByIndex(row - 1)
        new_row.setPropertyValue("BackColor", grey)
        self.set_table_cell(table, "A{}".format(row), 'Total', {"ParaStyleName": "Catalyst - Table header"})
        self.set_table_cell(table, "B{}".format(row), "{}{}".format(symbol, round(decimal.Decimal(total), 2)), {"ParaStyleName": "Catalyst - Table header"})

        sep = table.TableColumnSeparators
        sep[0].Position = 6000
        table.TableColumnSeparators = sep

    def find_replace(self, search_string, replace_string):
        replace_desc = self.document.createReplaceDescriptor()
        replace_desc.setSearchString(search_string)

        find_iter = self.document.findFirst(replace_desc)
        while find_iter:
            find_iter.String = replace_string
            find_iter = self.document.findNext(find_iter.End, replace_desc)

    def set_table_cell(self, table, cell_name, text, properties = {}):
        table_text = table.getCellByName(cell_name)
        cursor = table_text.createTextCursor()
        for p, v in properties.items():
            cursor.setPropertyValue(p, v)
        table_text.setString(text)

    def insert_table_at_end(self, x, y, title=None):
        text = self.document.Text
        cursor = text.createTextCursor()
        cursor.gotoEnd(False)
        if title is not None:
            cursor.ParaStyleName = "Catalyst - Heading 2"
            text.insertString(cursor, title, 0)
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)
        cursor.ParaStyleName = "Catalyst - Text Body"
        table = self.document.createInstance("com.sun.star.text.TextTable")
        table.initialize(x, y)
        text.insertTextContent(cursor, table, True)
        table.Split = False
        return table

    def insert_text(self, text_content, style=None):
        text = self.document.Text
        cursor = text.createTextCursor()
        cursor.gotoEnd(False)
        if style is not None:
            cursor.ParaStyleName = style
        else:
            cursor.ParaStyleName = "Catalyst - Text Body"
        text.insertString(cursor, text_content, 0)
        #text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)

    def insert_hyperlink_text(self, text1, link, linkwords, text2, style=None):
        text = self.document.Text
        cursor = text.createTextCursor()
        cursor.gotoEnd(False)
        if style is not None:
            cursor.ParaStyleName = style
        else:
            cursor.ParaStyleName = "Catalyst - Text Body"

        new_cursor = text.createTextCursorByRange(cursor)
        self.insert_text(text1)
        new_cursor.setString(linkwords)
        new_cursor.HyperLinkURL = link
        self.insert_text(text2)

    def connect(self):
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext)
        try:
            ctx = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")

        except Exception as e:
            print(e)
            print('Failure to connect to soffice process.')
            print('In a new terminal, run soffice --writer --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"')
            import sys
            sys.exit(-1)
        smgr = ctx.ServiceManager
        self.desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
        self.document = self.desktop.loadComponentFromURL ("file:///home/monique/projects/quoterizer/template.odt", "_blank", 0, ())
        #("file:///" + os.getcwd() + "/quoteriser/templates/template.odt", "_blank", 0, ())

    def save(self):
        """ Saves the file as a .odt file to the current directory"""
        #filename = "file:///" + os.getcwd() + "/clients/" + self.client.name + "/" + \
        #           self.client.name + "_" + self.client.month_config['config_date'] + ".odt"
        self.document.storeToURL("file:///home/monique/projects/quoterizer/quote.odt", ())
        self.document.close(True)
        self.p2.terminate()
        return "/tmp/filename.odt"
