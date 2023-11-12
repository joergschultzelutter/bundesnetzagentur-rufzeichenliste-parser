#!/opt/local/bin/python3
#
# Bundesnetzagentur Rufzeichenliste (PDF) Parser
# Author: Joerg Schultze-Lutter, 2021
#
# Herunterladen der jeweils aktuellen Bundesnetzagentur-Rufzeichenliste.
# Anschließend werden alle Rufzeichen extrahiert und in einem
# CSV-Format aufbereitet. Der Output erfolgt nach stdout.
# Das Programm nimmt keine Kategorisierung vor; d.h. auch Klubstationen
# usw. sind in der Ausgabedatei mit enthalten.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import requests
import logging
from io import StringIO, BytesIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re

# Set up the global logger variable
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s %(module)s -%(levelname)s- %(message)s"
)
logger = logging.getLogger(__name__)


def get_rufzeichen_file(
    request_url: str = "https://data.bundesnetzagentur.de/Bundesnetzagentur/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/Amateurfunk/Rufzeichenliste/rufzeichenliste_afu.pdf",
):
    """
    Downloads the Bundesnetzagentur Rufzeichenliste pdf and returns the binary blob.
    Blob is 'None' if the function was unable to download the file
    Parameters
    ==========
    url : 'str'
        Default value always points to the latest Bundesnetzagentur
        publication file
    Returns
    =======
    file_blob: 'bytes'
        File content or 'None' if the file could not get downloaded
    """

    # http request header
    request_headers = {"User-Agent": "Mozilla"}

    # our target variable
    file_blob = None

    # try to download the file

    logger.debug(msg=f"Trying to download file from {request_url}")
    try:
        resp = requests.get(url=request_url, headers=request_headers)
    except:
        logger.error(msg="Unable to download file; cannot continue")
        resp = None

    if resp:
        if resp.status_code == 200:
            file_blob = resp.content
            logger.info(msg="File successfully acquired")
    else:
        logger.error(
            msg=f"Unable to download file; cannot continue. HTTP error {resp.status_code}"
        )

    return file_blob


if __name__ == "__main__":
    # start the process by downloading the file
    file_content = get_rufzeichen_file()

    # did we get a file? Then process it
    if file_content:
        # This variable will later contain the text per pdf page
        output_string = StringIO()

        # Create the parser
        parser = PDFParser(BytesIO(file_content))

        # Create the document
        document = PDFDocument(parser)

        # Check if the file is password protected and abort, if necessary
        if not document.is_extractable:
            raise PDFDocument.PDFTextExtractionNotAllowed

        # Init our PDF processor
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # regex for German call signs
        regex_string = r"^(D[A-D|F-R][0-9][A-Z]{1,3}),\s(A|E),"

        # loop over all pages in the document
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)

            # Split up the page by lines
            lines = output_string.getvalue().split("\n")

            # Target field which will contain the catenated contents
            parser_value = ""

            # Triggers whether values should be attached or not
            attach_value = False

            # loop over all lines on this page
            for line in lines:
                # Regex represents potential valid call sign
                matches = re.search(regex_string, line)
                if matches:
                    # Is the value not empty?
                    if parser_value != "":
                        # And does its value start with something that looks like a call sign?
                        matches = re.search(regex_string, parser_value)
                        if matches:
                            # transpose the value to a unified csv format
                            # fmt:off
                            parser_value = parser_value.replace(", ", ";").replace("; ", ";")
                            # fmt:on
                            # and print the value
                            print(parser_value)
                    # Accept the value and tell the parser that additional lines can be attached
                    parser_value = line
                    attach_value = True
                else:
                    # crude but simple header parser
                    if "Liste der" in line:
                        # don't attach anything from here on up until we encounter a "Seite" text
                        attach_value = False
                        # but ensure to dump the last value from the previous page
                        if parser_value != "":
                            matches = re.search(regex_string, parser_value)
                            if matches:
                                # fmt:off
                                # transpose the value to a unified csv format
                                parser_value = parser_value.replace(", ", ";").replace("; ", ";")
                                # fmt:on
                                print(parser_value)
                        parser_value = ""
                    # "Seite" --> end of page; we can start attaching again
                    elif "Seite" in line:
                        attach_value = True
                    # default handler; attach the string if we have retrieved something
                    else:
                        if attach_value and line.strip() != "":
                            parser_value = parser_value + line
            # and dump the last element from the page that we've just processed
            if parser_value != "":
                matches = re.search(regex_string, parser_value)
                if matches:
                    # transpose the value to a unified csv format
                    parser_value = parser_value.replace(", ", ";").replace("; ", ";")
                    print(parser_value)

            # truncate the output string to zero length and then loop to the next doc page
            output_string.seek(0)
            output_string.truncate(0)
