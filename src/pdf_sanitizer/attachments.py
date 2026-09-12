from pypdf import PdfReader, PdfWriter
from pypdf.generic import *


def extract_attachments(reader: PdfReader) -> list:
    attachments = []
    if '/Root' in reader.trailer and '/Names' in reader.trailer['/Root']:
        names = reader.trailer['/Root']['/Names']
        if '/EmbeddedFiles' in names:
            embedded_files = names['/EmbeddedFiles']
            files = embedded_files.get_object()
            for name_tree in files.get('/Names', []):
                if isinstance(name_tree, ArrayObject):
                    for i in range(0, len(name_tree), 2):
                        file_spec = name_tree[i+1].get_object()
                        if '/EF' in file_spec:
                            file_dict = file_spec['/EF'].get_object()
                            file_stream = file_dict['/F']
                            file_data = file_stream.get_data()
                            file_name = file_spec['/F']
                            attachments.append((file_name, file_data))
    return attachments


def add_attachments(writer: PdfWriter, attachments: list) -> PdfWriter:
    if not attachments:
        return writer
    embedded_files_dict = DictionaryObject()
    embedded_files_array = ArrayObject()
    for file_name, file_data in attachments:
        file_stream = EncodedStreamObject()
        file_stream.set_data(file_data)
        file_dict = DictionaryObject()
        file_dict.update({
            NameObject('/F'): create_string_object(file_name),
            NameObject('/EF'): DictionaryObject({
                NameObject('/F'): file_stream
            })
        })
        embedded_files_array.append(create_string_object(file_name))
        embedded_files_array.append(file_dict)
    embedded_files_dict.update({
        NameObject('/Names'): embedded_files_array
    })
    writer._root_object.update({
        NameObject('/Names'): DictionaryObject({
            NameObject('/EmbeddedFiles'): embedded_files_dict
        })
    })

    return writer


def attachments_preview(src: str) -> bool:
    reader = PdfReader(src)
    att = reader.attachments
    if len(att) == 0:
        print('No attachments')
        return False

    for name, contentl in att.items():
        for i, content in enumerate(contentl):
            print(f'Attachment {name}-{i}: {len(content)} bytes')

    return True


def attachments_restore(reader: PdfReader, writer: PdfWriter) -> PdfWriter:
    return add_attachments(writer, extract_attachments(reader))
