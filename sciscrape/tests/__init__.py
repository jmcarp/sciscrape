# Get data directory

#import sciscrape
#module_init = sciscrape.__file__
#module_dir = os.path.split(module_init)[0]
#data_dir = '%s/tests/data' % (module_dir)

import os
tests_dir = os.path.dirname(__file__)
data_dir = '%s/data' % (tests_dir)
