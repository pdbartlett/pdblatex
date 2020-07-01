# Example Document
[Author: Paul D. Bartlett]
[Date: April 1, 2020]
[Package: amsmath, fancyhdr, float]
[Package: circ(basic)]

```preambleLaTeX
\pagestyle{fancy}
\fancyhf{}
\lhead{TEST}
\rhead{DOCUMENT}
\cfoot{\thepage}
\addtolength{\headheight}{2pt} % space for the rule
```

[TOC]
[FIGURES]

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

1. foo
1. bar
1. baz

It also allowed footnotes, but they don't convert to LaTeX with the default
renderer. I'll try to make them work, but will definitely add custom syntax for
full citation/reference support, both `parenthetical citations' (Jones2000), and
"inline ones" as used by Smith2001.

There is also support for LaTeX mathematical formatting, e.g. $y=mx+c$, though
that is probably not of much use for history essays! Even less useful would be
full equations:

$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$

Another less than obvious feature is `code fences`, but we (ab)use them to allow
the inclusion of literal [[\LaTeX{}]] code:

```inlineLaTeX
\begin{align}
\nabla \cdot \mathbf{D} &= \rho\\
\nabla \cdot \mathbf{B} &= 0\\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}} {\partial t}\\
\nabla \times \mathbf{H} &= \mathbf{J} + \frac{\partial \mathbf{D}} {\partial t}
\end{align}
```

```inlineLaTeX
\begin{figure}[H]
\centering
\begin{circuit}0
\npn1 {?} B l               % transistor
\frompin npn1C              % draw from collector
\- 1 u                      % some wire
\nl\A1 {$I_C$} u            % ammeter for current of collector
\atpin npn1B                % continue drawing from base
\- 1 l                      % some wire
\R1 {510k} l                % resistor
\- 1 l                      % some wire to the edge
\centerto A1                % draw centered to ammeter 1
\nl\A2 {$I_B$} u            % ammeter 2
\frompin A2b                % link ammeter 2 with resistor
\vtopin R1l
\frompin A1t
\- 1 u
\.1                         % junction
\frompin A2t                % wire to ammeter 2
\vtopin .1
\htopin .1
\- 1 u
\cc\connection1 {$U_b$} c u % driving voltage
\frompin npn1E
\- 1 d
\GND1                       % ground
\end{circuit}
\caption{Simple circuit}
\label{circuit}
\end{figure}
```

[BIBLIO]

---

# Appendices

## First appendix

Foo bar baz.

## Second appendix

Quux.
