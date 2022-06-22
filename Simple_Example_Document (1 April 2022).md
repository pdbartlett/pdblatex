[TOC]
[FIGURES]
[TABLES]

## Abstract

This document is intended to demonstrate all the things that can be done with
"non-weird", Markdown-inspired syntax.

Other, more complex things are possible, but with some more tricky (but still
hopefully reasonable) syntax.

## Features

### Basic

These are some very basic features that can be used:

1. title and date taken from name of `.md` one, or uses today's date if none specified
1. author defaults to Sophie Bartlett
1. `.bib` file with same name as `.md` loaded automatically
1. auto-conversion of double quotes (see _Introduction_ above)
1. **bold**, *italic* and `fixed-width` text
1. numbered lists (like this one)
1. table of contents, lists of figures/tables, bibliography and index placement
1. parenthetic citations (Jones2000) as well as direct ones, like Smith2001
1. simple !indexing of !terms using hopefully intuitive !syntax
1. inline mathematical expressions, like $y = f(x)$
1. sections and subsections

### Additional

Here are a few more features, broken out separately mainly to demonstrate
subsections, but it also gives a chance to show tables:

#### Table: Example of a captioned table (so it appears in list)

**Name** | **Description** | **Supported**
---------|-----------------|--------------
Table    | Tables of data  | Yes
Lists    | Lists of items  | Yes

Images, which like tables can be captioned. If so they can float to the most
convenient place in the document to aid formatting, and appear in their
respective lists. The first image example is uncaptioned so should appear
immediately:

![alt-text-not-used](cat.png)

#### Figure: Twas a cat

![alt-text-never-used](cat.png)

![](cat.png "And another one")

And blockquotes:

> Blockquotes, like this one, can be used when  you need to add a sizeable
> portion of text from a book, speech or other source, and format it so that it
> stands out more clearly.

It also provides an opportunity to see how subsequent paragraphs are formatted
(they are indented rather than "skipping space", though this can be changed at
a later date if it's preferable).

Finally it gives a chances to show a different type of list. This one is
bulleted---also known as unordered---as opposed to the numbered/ordered list
used in the previous section.

* bulleted lists (like this one)
* the different dashes: hyphens (e.g. side-effect), `en` dashes (e.g. 1--2 ideas),
  or `em` dashes as shown in the "parenthetical" example above
* addition of appendices (lettered instead of numbered as sections are)
* manual page breaks

---

# Appendices

## Extra information

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque vitae diam
nec libero ultrices placerat id et tellus. Proin vestibulum, sapien eget lobortis
fermentum, nisi leo malesuada nibh, tempor tincidunt leo nibh in elit. Mauris
fermentum nunc sed pellentesque eleifend. Nunc eget libero eu elit placerat
feugiat nec lacinia elit. Aenean ultrices lobortis ex eget gravida. Suspendisse
in erat viverra, aliquam nulla a, gravida diam. Vivamus at viverra mauris. Mauris
vitae mauris arcu. Proin eu erat odio.

---

[BIBLIO]

[INDEX]
