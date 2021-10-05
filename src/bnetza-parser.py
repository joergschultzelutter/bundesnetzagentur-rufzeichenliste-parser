#!/opt/local/bin/python3
#
# Bundesnetzagentur Rufzeichenliste (PDF) Parser
# Author: Joerg Schultze-Lutter, 2021
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


def get_rufzeichen_file(request_url: str = "https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/Amateurfunk/Rufzeichenliste/Rufzeichenliste_AFU.pdf?__blob=publicationFile"):
	
	request_headers = {"User-Agent": "Mozilla"}
	file_blob = None

	try:
		 resp = requests.get(url=request_url,headers=request_headers)
	except:
		resp = None
	
	if resp:
		if resp.status_code == 200:
			file_blob = resp.content
	else:
		logger.info(msg="Cannot download Rufzeichen file")
	
	return file_blob

if __name__ == "__main__":
	print ("Downloading file")
	file_content= get_rufzeichen_file()
	if file_content:


		output_string = StringIO()


		print ("Parsing")
		# Create the parser
		parser = PDFParser(BytesIO(file_content))

		print ("Create doc")
		# Create the document
		document = PDFDocument(parser)

		# Check if the file is password protected and abort, if necessary
		if not document.is_extractable:
			raise PDFDocument.PDFTextExtractionNotAllowed

		rsrcmgr = PDFResourceManager()
		device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
		interpreter = PDFPageInterpreter(rsrcmgr, device)

		print ("Loop doc")
		# loop over all pages in the document
		for page in PDFPage.create_pages(document):
			interpreter.process_page(page)
			lines = output_string.getvalue().split("\n") 

			parser_value = ""
			attach_value = False

			for line in lines:
				matches = re.search(r"^(D[A-D|F-R][0-9][A-Z]{1,3}),\s(A|E),",line)
				if matches:
					if parser_value != "":
						matches = re.search(r"^(D[A-D|F-R][0-9][A-Z]{1,3}),\s(A|E),",parser_value)
						if matches:
							print (parser_value)
					parser_value = line
				else:
					if "Liste der" in line:
						attach_value = False
						if parser_value != "":
							matches = re.search(r"^(D[A-D|F-R][0-9][A-Z]{1,3}),\s(A|E),",parser_value)
							if matches:
								print (parser_value)
						parser_value = ""
					elif "Seite" in line:
						attach_value = True
					else:
						if attach_value and line.strip() != "":
							parser_value = parser_value + line
			if parser_value != "":
				matches = re.search(r"^(D[A-D|F-R][0-9][A-Z]{1,3}),\s(A|E),",parser_value)
				if matches:
					print (parser_value)
			output_string.seek(0)
			output_string.truncate(0)
