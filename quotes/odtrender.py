import subprocess
import uno
import os
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.awt import Size

#For table:
#Item, Cost (excl vat) in 'currency' as headers
#line items, total
#subtotal, total so far
#project management fee, % of subtotal
#Vat (will say 'not applicable' if vat is not ticked), vat amount
#total, total


# V2 - make it optional whether days or hoursin amount
# download odt button
# save to pdf button

class QuoteRenderer:

    def __init__(self, quote):
        p2 = subprocess.Popen(("soffice", "--writer", '--accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"', "--headless"))
        self.quote = quote

    def render(self):
        self.connect()

        client = 'stop not working'
        print ('stop not working')
        self.find_replace("{{client}}", client) #self.quote.client
        self.find_replace("{{title}}", self.quote.title)
        subtotal = self.object.lineitem_set.aggregate(Sum('amount'))['amount__sum']

        insert_quote_table(self, self.quote.lineitem_set, self.quote.title, subtotal) #TODO: add line items and total amount as proper args

        if self.quote.conditions == 'Catalyst Standard Terms':
            text = "This quote is proposed under the assumption that both parties accept and agree that the scope, services and standards of quality for the project are accepted. Parties acknowledge and accept Catalyst's standard Terms and Conditions[1] (http://catalyst-eu.net/terms), notes, obligations and assumptions."
        else:
            text = "This quote is proposed under the assumption that parties accept and agree the scope, services and standards of quality outlined here. Parties acknowledge and accept Catalyst's Digital Marketplace standard Terms and Conditions (https://assets.digitalmarketplace.service.gov.uk/g-cloud-9/documents/579028/520395179658286-terms-and-conditions-2017-04-07-1042.pdf), notes, obligations and assumptions."
            insert_text(self, text)

            self.save()

    def insert_quote_table(self, line_items, title, total_amount):
        grey = 0xCCCCCC

        if quote.currency == 'GBP':
            symbol = '£'
        elif quote.currency == 'EUR':
            symbol = '€'
        elif quote.currency == 'USD':
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
        self.set_table_cell(table, "B1", 'Cost ({}) (exc VAT)'.format(self.quote.currency), {"ParaStyleName": "Catalyst - Table header"})

        #line items for table
        row = 2
        for item in item_list:
            self.set_table_cell(table, "A{}".format(row), self.line.description, {"ParaStyleName": "Catalyst - Table contents"})
            self.set_table_cell(table, "B{}".format(row), "{}{}".format(symbol, self.line.amount), {"ParaStyleName": "Catalyst - Table contents"})
            row += 1

        #subtotal
        new_row = table_rows.getByIndex(row - 1)
        new_row.setPropertyValue("BackColor", grey)
        self.set_table_cell(table, "A{}".format(row), 'Subtotal (exc VAT)', {"ParaStyleName": "Catalyst - Table header"})
        self.set_table_cell(table, "B{}".format(row), "{}{}".format (symbol, total_amount), {"ParaStyleName": "Catalyst - Table header"})

        percent = self.quote.pm*100
        project_management = self.line.amount*percent

        #project management line
        new_row = table_rows.getByIndex(row - 1)
        self.set_table_cell(table, "A{}".format(row), 'Project Management Fee {}%'.format(self.quote.pm), {"ParaStyleName": "Catalyst - Table contents"})
        self.set_table_cell(table, "B{}".format(row), project_management, {"ParaStyleName": "Catalyst - Table contents"})

        #VAT line
        if self.line.vat:
            vat_line = 'VAT (20%)'
            VAT = line.amount + project_management
        else:
            vat_line = 'VAT (not applicable)'
            VAT = 0

        new_row = table_rows.getByIndex(row - 1)
        self.set_table_cell(table, "A{}".format(row), vat_line, {"ParaStyleName": "Catalyst - Table contents"})
        self.set_table_cell(table, "B{}".format(row), VAT, {"ParaStyleName": "Catalyst - Table contents"})

        total = subtotal + project_management + VAT

        #total line
        new_row = table_rows.getByIndex(row - 1)
        new_row.setPropertyValue("BackColor", grey)
        self.set_table_cell(table, "A{}".format(row), 'Total', {"ParaStyleName": "Catalyst - Table header"})
        self.set_table_cell(table, "B{}".format(row), total, {"ParaStyleName": "Catalyst - Table header"})


    def find_replace(self, search_string, replace_string):
        replace_desc = self.document.createReplaceDescriptor()
        replace_desc.setSearchString(search_string)

        find_iter = self.document.findFirst(replace_desc)
        while find_iter:
            find_iter.String = replace_string
            find_iter = self.document.findNext(find_iter.End, replace_desc)


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
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, 0)

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
        self.document = self.desktop.loadComponentFromURL("file:///" + os.getcwd() + "/reporttemplate.odt", "_blank", 0, ())

    def save(self):
        """ Saves the file as a .odt file to the current directory"""
        #filename = "file:///" + os.getcwd() + "/clients/" + self.client.name + "/" + \
        #           self.client.name + "_" + self.client.month_config['config_date'] + ".odt"
        self.document.storeToURL("file:///tmp/filename.odt", ())
        self.document.close(True)

        return "/tmp/filename.odt"
