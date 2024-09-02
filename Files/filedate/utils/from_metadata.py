#!/usr/bin/env python

import re
from datetime import datetime
from zipfile import ZipFile
import xml.etree.ElementTree as ET # for .docx, .xlsx, .pptx,   .odt, .ods, .odp
from PyPDF2 import PdfReader
from hachoir.parser import createParser # pip install PyPDF2 hachoir
from hachoir.core import config as HachoirConfig
HachoirConfig.quiet = True
from hachoir.metadata import extractMetadata # creation_date, last_modification as datetime
# also from EXIF (OffsetTime - EXIF v.2.31 - I don't know if it's taken into account)
# Many formats
# MP3, WAV, OGG, MIDI, AIFF, AIFC, RA
# GIF, JPEG, PCX, PNG, TGA, TIFF, WMF, XCF
# WMV, AVI, MKV, MOV, RM  
# EXE, DOC, XLS, PPT

import sys; sys.path.insert(1, sys.path[0]+'/..') # if `filedate` not installed
from filedate import FileDate


from dateutil.parser import parse #used if FromMetadata.VERBOSE

#-=-=-=-#

class FromMetadata:
	"""Utility for setting file date based on its metadata.
Poorly tested, but can be useful, 
for example, for saved attachments from e-mail.
"""
	VERBOSE = True
	LIST_ONLY = False # List only (in combination with VERBOSE) - don’t modify timestamp

	def __init__(self, file_path: str):
		self.file_path = file_path
		self._metadata = {} # as timestamp or str: {'created': dt_tm0, 'modified': dt_tm1, ...}

#-=-=-=-#

# MIT - based on https://github.com/JMousqueton/MetaLookup/ ver "0.3.1"

	def extract_metadata(self, add_modified_if_missing = True):
		"""add_modified_if_missing - and if created exists
		Mainly 'modified' will be used to correct the timestamp of the file"""

		def extract_pdf_metadata(pdf_path): #.pdf
			with open(pdf_path, 'rb') as file:
				pdf = PdfReader(file)
				try:
					info = pdf.trailer["/Info"]
					metadata = {key[1:]: info[key] for key in info if key != '/ID'}
					# CreationDate: D:20240528193019+00'00' # ModDate: D:20240528193019+00'00'
					# CreationDate: D:20210316065455Z00'00'
					metadata_ = {}
					for (k0, k1) in (('CreationDate', 'created'), ('ModDate', 'modified')):
						k0_ = metadata.get(k0)
						if k0_:
							metadata_[k1] = re.sub(r"Z.+$",r"Z",re.sub(r"'.+$", "", re.sub(r"^.+:","",k0_)))
							# created: 20240528193019+00, modified: 20240528193019+00
					for (k, v) in metadata_.items():
						v_ = None
						try:
							v_ = parse(v) #$#; print(f'{v_=}') #$#
							if v_.year < 1970: # eq. CreationDate: D:16010101000000Z
								v_ = None
						except:
							v_d = re.sub(r'^.*?(\d{8,}).*$',r'\1',v)[:14] # 20210316065455
							if FromMetadata.VERBOSE: print(f'    {v} -> {v_d}')
							try: 
								v_ = parse(v_d)
							except Exception as error:
								if FromMetadata.VERBOSE: print(f'{error}')
								v_ = None
						metadata_[k] = v_
					#
					metadata.update(metadata_)
					return add_missing_modified(metadata)
				except KeyError:
					return {}
		#
		def zipxml_to_dict(zip_file_path, inner_xml):
			"""Get data from zip->'xml' recus. (depth first order) to flat dict. 
			Keys without prefixes"""
			metadata = {}
			try:
				zipf = ZipFile(zip_file_path)
				root = ET.fromstring(zipf.read(inner_xml))
				#$# print(root.find('.//{*}created')) #$# case of a single, specific element
				for el in root.iter(): #recus., all data
					metadata[re.sub(r'.*\}','',el.tag)] = el.text #sub(): remove prefix '{...}'
					#$# print(f'{el.tag=}') #$# eq. el.tag='{http://purl.org/dc/terms/}created'
				return metadata
			except Exception as error:
				print(error)
				return metadata
		#
		def extract_ms_office_metadata(doc_path): # .docx, .xlsx, .pptx - zip - docProps/core.xml
			#  title, description, creator, lastModifiedBy, created, modified
			return add_missing_modified(zipxml_to_dict(self.file_path, 'docProps/core.xml'))
		#
		def extract_oo_office_metadata(doc_path): # .odt, .ods, .odp - zip - meta.xml
			#  creation-date, date, editing-duration, editing-cycles, generator, document-statistic
			metadata = zipxml_to_dict(self.file_path, 'meta.xml')
			for (k0, k1) in {'creation-date': 'created', 'date': 'modified'}.items():
				v_ = metadata.get(k0)
				if v_:
					metadata[k1] = v_
			return add_missing_modified(metadata)
		#
		def extract_multimedia_metadata(video_path): # and all other
			parser = createParser(video_path)
			if not parser:
				if FromMetadata.VERBOSE: print(f'    (hachoir:) Unable to parse file: "{video_path}"')
				return {}
			with parser:
				try:
					metadata_ = extractMetadata(parser)
				except Exception as e:
					if FromMetadata.VERBOSE: print(f'    Metadata extraction error: "{e}"')
					return {}
			if not metadata_:
				return {}
			#
			# Iterate over metadata_ attributes and fetch their values
			metadata = {} # metadata_ -> dict
			for item in metadata_:
				k_ = item.key.lower() #$#;print(f'{item.key=}') #$#
				for s in ('time', 'date', 'modifi', 'create', 'creati'):
					if s in k_ and item.values:
						metadata[item.key] = item.values[0].value
						break # for s in >>>>>>>>>>>>>>>>>
			#
			#offs_ = metadata.get('offset_time_original','') # this is missing in Hachoir?; was introduced in Exif v.2.31(2016)
			#eq. OffsetTimeOriginal: '+02:00' 
			for (k0, k1) in {'creation_date': 'created', 'date_time_digitized': 'modified', 'last_modification': 'modified'}.items():
				v_ = metadata.get(k0)
				if v_:
					metadata[k1] = v_
			return add_missing_modified(metadata)

		def add_missing_modified(metadata):
			if add_modified_if_missing: # mainly 'modified' will be used to correct the timestamp of the file
				if not metadata.get('modified', None):
					v_ = metadata.get('created', None)
					if v_:
						metadata['modified'] = v_ 
						if FromMetadata.VERBOSE: print('    c --> m')
			return metadata

		### 
		f_path = f'{self.file_path}'
		path_end = f_path[-8:].lower()
		try:
			if path_end.endswith('.pdf'):
				return extract_pdf_metadata(f_path)
			elif path_end.endswith(('.docx', '.xlsx', '.pptx')):
				return extract_ms_office_metadata(f_path)
			elif path_end.endswith(('.odt', '.ods', '.odp')):
				return extract_oo_office_metadata(f_path)
			else: # all other: hachoir
				return extract_multimedia_metadata(f_path)
		except Exception as error:
			if FromMetadata.VERBOSE: print(f'{error}')
			return {}

#-=-=-=-#

	def set_date(self, cm_='cm'):
		"""
		Sets the date based on file metadata
		"""
		self._metadata = self.extract_metadata()	#$# ;print(f'\t#$# {self._metadata=}') #$#
		if not self._metadata:
			return None
		
		if FromMetadata.VERBOSE:
			for k,v in self._metadata.items():
				k_ = k.lower()
				for s in ('time', 'date', 'modifi', 'create', 'creati'):
					if s in k_:
						if k_ in ('modified', 'created'):
							if isinstance(v, datetime) and (v.year >= 1970): # .astimezone() problem with 1601-01-01 00:00+02:00
								print(f'    {k}: {v} ({v.astimezone()}, tzinfo: {v.tzinfo})')
							elif isinstance(v, str):
								print(f'    {k}: {v} ({parse(v).astimezone()})')
						else:
							print(f'    {k}: {v}')
						break # for s in >>>>>>>>>
			
		dt_tm_param = {'created': None, 'modified': None}
		for k in dt_tm_param.keys():
			if k[0] in cm_:
				dt_tm_param[k] = self._metadata.get(k)
		
		# return str(FileDate.self) if not FileDate.SET_SILENT
		return FileDate(self.file_path).set(**dt_tm_param) if not FromMetadata.LIST_ONLY else None

#-=-=-=-#

def more_tests():
	"""
	My test files in development...
	>>> def do(fp):
	...   print('~'); print(f'''{fp!r} =================''')
	...   FileDate.SET_SILENT = 1; FileDate(fp).set(created= '2000-01-02 12:00:00', modified= '2021-03-04 14:00:00')
	...   FileDate.SET_SILENT = 0; print(f'''{FromMetadata(fp).set_date('cm')}''')
	...   return
	>>> FromMetadata.VERBOSE = 1; FromMetadata.LIST_ONLY = 0
	>>> 							######### (PyPDF2) #########
	>>> for file_path in ("ab c.pdf", "ab cc.pdf", "ab ccc.pdf"): do("tmp/"+file_path)
	~
	'tmp/ab c.pdf' =================
	    CreationDate: D:20240528193019+00'00'
	    ModDate: D:20240528193019+00'00'
	    created: 2024-05-28 19:30:19+00:00 (2024-05-28 21:30:19+02:00, tzinfo: tzutc())
	    modified: 2024-05-28 19:30:19+00:00 (2024-05-28 21:30:19+02:00, tzinfo: tzutc())
	{'created': '2024-05-28 21:30:19', 'modified': '2024-05-28 21:30:19', 'accessed': '...'}
	~
	'tmp/ab cc.pdf' =================
	    c --> m
	    CreationDate: D:20230914214404Z
	    created: 2023-09-14 21:44:04+00:00 (2023-09-14 23:44:04+02:00, tzinfo: tzutc())
	    modified: 2023-09-14 21:44:04+00:00 (2023-09-14 23:44:04+02:00, tzinfo: tzutc())
	{'created': '2023-09-14 23:44:04', 'modified': '2023-09-14 23:44:04', 'accessed': '...'}
	~
	'tmp/ab ccc.pdf' =================
	    c --> m
	    CreationDate: D:20210316065455Z00'00'
	    created: 2021-03-16 06:54:55+00:00 (2021-03-16 07:54:55+01:00, tzinfo: tzutc())
	    modified: 2021-03-16 06:54:55+00:00 (2021-03-16 07:54:55+01:00, tzinfo: tzutc())
	{'created': '2021-03-16 07:54:55', 'modified': '2021-03-16 07:54:55', 'accessed': '...'}
	>>> 							######### (zipfile, xml.etree.ElementTree) #########
	>>> for file_path in ("ab c.docx", "ab c.xlsx", "ab c.pptx"): do("tmp/"+file_path)
	~
	'tmp/ab c.docx' =================
	    lastModifiedBy: ...
	    created: 2021-04-07T06:21:00Z (2021-04-07 08:21:00+02:00)
	    modified: 2023-10-03T05:14:00Z (2023-10-03 07:14:00+02:00)
	{'created': '2021-04-07 08:21:00', 'modified': '2023-10-03 07:14:00', 'accessed': '...'}
	~
	'tmp/ab c.xlsx' =================
	    lastModifiedBy: ...
	    created: 2009-10-27T10:23:20Z (2009-10-27 11:23:20+01:00)
	    modified: 2023-02-02T10:00:06Z (2023-02-02 11:00:06+01:00)
	{'created': '2009-10-27 11:23:20', 'modified': '2023-02-02 11:00:06', 'accessed': '...'}
	~
	'tmp/ab c.pptx' =================
	    lastModifiedBy: ...
	    created: 2013-01-27T09:14:16Z (2013-01-27 10:14:16+01:00)
	    modified: 2013-01-27T09:15:58Z (2013-01-27 10:15:58+01:00)
	{'created': '2013-01-27 10:14:16', 'modified': '2013-01-27 10:15:58', 'accessed': '...'}
	>>> #
	>>> for file_path in ("ab c.odt", "ab c.ods", "ab c.odp"): do("tmp/"+file_path)
	~
	'tmp/ab c.odt' =================
	    creation-date: 2024-08-29T08:59:12.527000000
	    date: 2024-08-29T09:09:33.534000000
	    created: 2024-08-29T08:59:12.527000000 (2024-08-29 08:59:12.527000+02:00)
	    modified: 2024-08-29T09:09:33.534000000 (2024-08-29 09:09:33.534000+02:00)
	{'created': '2024-08-29 08:59:12', 'modified': '2024-08-29 09:09:33', 'accessed': '...'}
	~
	'tmp/ab c.ods' =================
	    creation-date: 2024-08-29T09:03:44.592000000
	    date: 2024-08-29T09:10:05.701000000
	    created: 2024-08-29T09:03:44.592000000 (2024-08-29 09:03:44.592000+02:00)
	    modified: 2024-08-29T09:10:05.701000000 (2024-08-29 09:10:05.701000+02:00)
	{'created': '2024-08-29 09:03:44', 'modified': '2024-08-29 09:10:05', 'accessed': '...'}
	~
	'tmp/ab c.odp' =================
	    creation-date: 2024-08-29T09:04:17.977000000
	    date: 2024-08-29T09:09:51.367000000
	    created: 2024-08-29T09:04:17.977000000 (2024-08-29 09:04:17.977000+02:00)
	    modified: 2024-08-29T09:09:51.367000000 (2024-08-29 09:09:51.367000+02:00)
	{'created': '2024-08-29 09:04:17', 'modified': '2024-08-29 09:09:51', 'accessed': '...'}
	>>> 							######### (hachoir.parser) #########
	>>> for file_path in ("ab c.doc", "ab c.jpg", "ab c.exe", "ab cc.exe" ): do("tmp/"+file_path)
	~
	'tmp/ab c.doc' =================
	    creation_date: 2013-12-16 15:31:00
	    last_modification: 2013-12-18 09:50:00
	    created: 2013-12-16 15:31:00 (2013-12-16 15:31:00+01:00, tzinfo: None)
	    modified: 2013-12-18 09:50:00 (2013-12-18 09:50:00+01:00, tzinfo: None)
	{'created': '2013-12-16 15:31:00', 'modified': '2013-12-18 09:50:00', 'accessed': '...'}
	~
	'tmp/ab c.jpg' =================
	    creation_date: 2024-05-21 13:49:27
	    date_time_original: 2024-05-21 13:49:27
	    date_time_digitized: 2024-05-21 13:49:27
	    created: 2024-05-21 13:49:27 (2024-05-21 13:49:27+02:00, tzinfo: None)
	    modified: 2024-05-21 13:49:27 (2024-05-21 13:49:27+02:00, tzinfo: None)
	{'created': '2024-05-21 13:49:27', 'modified': '2024-05-21 13:49:27', 'accessed': '...'}
	~
	'tmp/ab c.exe' =================
	    c --> m
	    creation_date: 2017-05-03 08:30:12
	    created: 2017-05-03 08:30:12 (2017-05-03 08:30:12+02:00, tzinfo: None)
	    modified: 2017-05-03 08:30:12 (2017-05-03 08:30:12+02:00, tzinfo: None)
	{'created': '2017-05-03 08:30:12', 'modified': '2017-05-03 08:30:12', 'accessed': '...'}
	~
	'tmp/ab cc.exe' =================
	None
"""


#=========================================

if __name__ == '__main__':
	import doctest
	#doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS)
	doctest.testmod(optionflags=doctest.ELLIPSIS)
