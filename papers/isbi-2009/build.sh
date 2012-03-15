texfile=report
t=.$texfile.tex_files
test -d $t || mkdir $t
cd $t
TEXINPUTS=:..:.: pdflatex $texfile
BSTINPUTS=:..: BIBINPUTS=:..:.: bibtex $texfile
cp $texfile.pdf ..
