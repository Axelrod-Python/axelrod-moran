# Evolution Reinforces Cooperation with the Emergence of Self-Recognition Mechanisms: an empirical study of the Moran process for the iterated Prisoner's dilemma using reinforcement learning

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

The bibliography is being built using `biblatex` which requires `biber`, that
comes bundled with some installs of `latex` but if you are having problems you
might need to run (on ubuntu, similarly for other systems):

```
$ sudo apt-get install biber
```

# Contributions

- Conceived of the study: MH VK
- Conducted experiments and trained strategies: VK MH NG
- Analyzed the data and analytical methods: VK MH
- Wrote the paper: VK MH NG
- Created software: MH VK
- Axelrod Library Core Team: VK OC MH
