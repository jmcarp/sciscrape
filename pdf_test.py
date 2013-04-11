
import os

def test():

    pdf_dir = '/Users/jmcarp/Desktop/pdf-parse-sample/jocn/'
    pdf_files = os.listdir(pdf_dir)

    extractor = MRITableExtractor()

    tables = {}

    for pdf in pdf_files:
        
        print 'Working on file %s...' % (pdf)

        full_file = os.path.join(pdf_dir, pdf)
        print full_file
        table = extractor.pdf_to_mri_tables(pdf_name=full_file)
        tables[pdf] = table

    # Return completed tables
    return tables
