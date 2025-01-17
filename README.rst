This is the source code & data for the paper

    *Nuclear segmentation in microscope cell images: A hand-segmented dataset
    and comparison of algorithms* by Luis Pedro Coelho, Aabid Shariff, and
    Robert F.  Murphy.  DOI: `10.1109/ISBI.2009.5193098
    <http://dx.doi.org/10.1109/ISBI.2009.5193098>`__ `PubMed Central (open
    access) <http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2901896/>`__.

Data
----

Original data is in the ``data/`` directory. The two subfolders ``gnf`` and
``ic100`` contain the files that were manually generated. In the subfolder
``preprocessed-data``, you will a processed version which may be easier to use.

These are labeled integer images: the value 0 corresponds to the background, 1
is the first cell, 2 the second cell, &c.

Citation
--------

Full citation (use this if you use this code/dataset in a paper)::

    @inproceedings{Coelho2009,
        title = {Nuclear segmentation in microscope cell images: A hand-segmented dataset and comparison of algorithms},
        author = {Coelho, Luis Pedro and Shariff, Aabid and Murphy, Robert F.},
        booktitle = {2009 IEEE International Symposium on Biomedical Imaging: From Nano to Macro},
        doi = {10.1109/ISBI.2009.5193098},
        isbn = {978-1-4244-3931-7},
        keywords = {segmentation},
        pages = {518--521},
        year = {2009},
        publisher = {IEEE},
        url = {http://ieeexplore.ieee.org/lpdocs/epic03/wrapper.htm?arnumber=5193098}
    }

