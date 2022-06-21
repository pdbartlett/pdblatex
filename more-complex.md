# Example Document
[Author: Paul D. Bartlett]
[Date: April 1, 2020]
[DocType: minimart]
[Package: draftwatermark(text=TEST,scale=6)]

```bibTeX
@book{Jones2000,
	Author = {Jones, J.},
	Publisher = {E.G. Books},
	Title = {An Example Citation},
	Year = {2000}}
@book{Smith2001,
	Author = {Smith, Winston},
	Publisher = {A.N. Other},
	Title = {Another Quotable Source},
	Year = {2001}}
```

```preambleLaTex
\def\BibTeX{{\textsc{Bib}\TeX}}
```

[TOC]

## Introduction

Once upon a time there was a document, which was written in Markdown.

## Features

It contained **bold** text,  some *italics*, but this was just the start of what
was possible. For example, it could also do lists, tables, quotes, and many more
things besides.

For example, you can also do lists with bullet points (I'm waffling a bit here,
because if the first paragraph is too short then the indentation looks really
odd!):

* item 1
* item 2
* item 3

Or numbered ones (more waffle, a bit more waffle, even more waffle, and---you
guessed it---some more waffle!):

1. !foo
1. !bar
1. !baz

It also allowed footnotes, but they don't convert to [[\LaTeX{}]] with the default
renderer. I'll try to make them work, but will definitely add custom syntax for
full citation/reference support, both `parenthetical citations' (Jones2000), and
"inline ones" as used by Smith2001.

There is also support for [[\LaTeX{}]] mathematical formatting, e.g. $y=mx+c$, though
that is probably not of much use for history essays! Even less useful would be
full equations:

$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$

Another less than obvious feature is `code fences`, which we (ab)use them to allow
the inclusion of literal [[\LaTeX{}]] code:

```inlineLaTeX
\begin{align}
\nabla \cdot \mathbf{D} &= \rho\\
\nabla \cdot \mathbf{B} &= 0\\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}} {\partial t}\\
\nabla \times \mathbf{H} &= \mathbf{J} + \frac{\partial \mathbf{D}} {\partial t}
\end{align}
```

Or [[\BibTeX{}]] for references; see below.

[BIBLIO]

---

# Appendices

## First appendix

Foo bar baz.

## Second appendix

Quux.

[INDEX]
