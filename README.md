SciScrape: Tools for identifying, downloading, and parsing scientific articles.

Examples:
To run the example processing stream, run:

```python
from sciscrape.examples import examples
tables = examples.example_full_stream(out_dir='.')
```

To download a batch of articles from NeuroImage, run:

```python
from sciscrape.examples import examples
examples.example_scrape_nimg()
```

To run PDF extraction tests, run:

```python
from sciscrape.tests import pdftest
results = pdftest.test('jocn')
print results.mean()
```
