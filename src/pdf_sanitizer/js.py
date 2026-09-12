from pypdf import PdfReader, PdfWriter


def js_sanitize(reader: PdfReader, writer: PdfWriter, verbose: bool=True) -> PdfWriter:
    for i in range(len(reader.pages)):
        page = reader.pages[i]

        if '/Annots' in page:
            for annot in page['/Annots']:
                annot_obj = annot.get_object()
                if '/A' in annot_obj and annot_obj['/A']['/S'] == '/JavaScript':
                    if verbose:
                        print('Found embedded JS in annot at page {i}')
                    del annot_obj['/A']
        if '/AA' in page:
            if verbose:
                print('Found embedded JS in additional actions at page {i}')
            del page['/AA']

        writer.add_page(page)

    root = reader.trailer['/Root']
    if '/JavaScript' in root:
        if verbose:
            print('Found embedded JS in document /Root')
        del root['/JavaScript']
    if '/Names' in root:
        names = root['/Names']
        if '/JavaScript' in names:
            if verbose:
                print('Found embedded JS in document /Names')
            del names['/JavaScript']

    return writer

