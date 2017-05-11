# A numerical study of fixation probabilities for strategies in the Iterated Prisoner's Dilemma

This is a paper giving an extensive numerical analysis of fixation probabilities
of the Moran processes where the fitness landscape is determined by the Iterated
Prisoner's Dilemma.

This directory is structured as follows:

```
|--- main.tex  # The main article file
|---tex  # Further tex files
     |--- bibliography.bib
     |--- moran_process.tex
|---src  # All python source files used to generate the data
     |--- generate_cache.py
     |--- ...?
|---nbs  # All jupyter notebooks for the analysis of data
     |--- main.ipynb
|---data  # All data files
|---img  # All image files
environment.yml  # a conda environment file
```

# Building the article:

The following compiles the article using `Latexmk` version 4.41:

```
$ latexmk --xelatex main.tex
```

# Contributions

- Conceived of the study: MH VK
- Conducted experiments and trained strategies: VK MH NG
- Analyzed the data and analytical methods: VK MH
- Wrote the paper: VK MH NG
- Created software: MH VK
- Axelrod Library Core Team: VK OC MH
