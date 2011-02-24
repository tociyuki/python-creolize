import unittest
import re
import difflib
import creolize

# this test ported from Daniel Mendler's creole for ruby language.
# http://github.com/larsch/creole/blob/master/test/test_creole.rb

SPEC = r"""
.test Bold can be used inside paragraphs
.sect input
This **is** bold
.sect expected
<p>This <strong>is</strong> bold</p>

.test Bolds can be used inside paragraphs
.sect input
This **is** bold and **bold**ish
.sect expected
<p>This <strong>is</strong> bold and <strong>bold</strong>ish</p>

.test Bold can be used inside list item
.sect input
* This is **bold**
.sect expected
<ul>
<li>This is <strong>bold</strong></li>
</ul>

.test Bold can be used inside table cells
.sect input
|This is **bold**|
.sect expected
<table>
<tr><td>This is <strong>bold</strong></td></tr>
</table>

.test Links can appear inside bold text
.sect input
A bold link: **http://wikicreole.org/ nice!**
.sect expected
<p>A bold link: <strong><a href="http://wikicreole.org/">http://wikicreole.org/</a> nice!</strong></p>

.test Bold will end at the end of paragraph
.sect input
This **is bold
.sect expected
<p>This <strong>is bold</strong></p>

.test Bold will end at the end of list items
.sect input
* Item **bold
* Item normal
.sect expected
<ul>
<li>Item <strong>bold</strong></li>
<li>Item normal</li>
</ul>

.test Bold will end at the end of table cells
.sect input
|Item **bold|Another **bold
.sect expected
<table>
<tr><td>Item <strong>bold</strong></td><td>Another <strong>bold</strong></td></tr>
</table>

.test Bold should not cross paragraphs
.sect input
This **is

bold** maybe
.sect expected
<p>This <strong>is</strong></p>
<p>bold<strong>maybe</strong></p>

.test Bold should be able to cross lines
.sect input
This **is
bold**
.sect expected
<p>This <strong>is bold</strong></p>

.test Italic can be used inside paragraphs
.sect input
This //is// italic
.sect expected
<p>This <em>is</em> italic</p>

.test Italics can be used inside paragraphs
.sect input
This //is// italic and //italic//ish
.sect expected
<p>This <em>is</em> italic and <em>italic</em>ish</p>

.test Italic can be used inside list items
.sect input
* This is //italic//
.sect expected
<ul>
<li>This is <em>italic</em></li>
</ul>

.test Italic can be used inside table cells
.sect input
|This is //italic//|
.sect expected
<table>
<tr><td>This is <em>italic</em></td></tr>
</table>

.test Links can appear inside italic text
.sect input
A italic link: //http://wikicreole.org/ nice!//
.sect expected
<p>A italic link: <em><a href="http://wikicreole.org/">http://wikicreole.org/</a> nice!</em></p>

.test Italic will end at the end of paragraph
.sect input
This //is italic
.sect expected
<p>This <em>is italic</em></p>

.test Italic will end at the end of list items
.sect input
* Item //italic
* Item normal
.sect expected
<ul>
<li>Item <em>italic</em></li>
<li>Item normal</li>
</ul>

.test Italic will end at the end of table cells
.sect input
|Item //italic|Another //italic
.sect expected
<table>
<tr><td>Item <em>italic</em></td><td>Another <em>italic</em></td></tr>
</table>

.test Italic should not cross paragraphs
.sect input
This //is

italic// maybe
.sect expected
<p>This <em>is</em></p>
<p>italic<em>maybe</em></p>

.test Italic should be able to cross lines
.sect input
This //is
italic//
.sect expected
<p>This <em>is italic</em></p>

.test Bold italics
.sect input
**//bold italics//**
.sect expected
<p><strong><em>bold italics</em></strong></p>

.test Italics bold
.sect input
//**italics bold**//
.sect expected
<p><em><strong>italics bold</strong></em></p>

.test Italics and italics bold
.sect input
//This is **also** good.//
.sect expected
<p><em>This is <strong>also</strong> good.</em></p>

.test Only three differed sized levels of heading are required
.sect input
= Heading 1 =
== Heading 2 ==
=== Heading 3 ===
.sect expected
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>

.test Optional headings, not specified in creole 1.0
.sect input
==== Heading 4 ====
===== Heading 5 =====
====== Heading 6 ======
.sect expected
<h4>Heading 4</h4>
<h5>Heading 5</h5>
<h6>Heading 6</h6>

.test Right-side equal signs are optional
.sect input
=Heading 1
== Heading 2
=== Heading 3
.sect expected
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>

.test Right-side equal signs don't need to be balanced
.sect input
=Heading 1 ===
== Heading 2 =
=== Heading 3 ===========
.sect expected
<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>

.test Whitespace is allowed before the left-side equal signs
.sect input
                            = Heading 1 =
                           == Heading 2 ==
.sect expected
<h1>Heading 1</h1>
<h2>Heading 2</h2>

.test Only white-space characters are permitted after the closing equal signs
.sect input
 = Heading 1 =   
  == Heading 2 ==  
.sect expected
<h1>Heading 1</h1>
<h2>Heading 2</h2>

.test doesn't specify if text after closing equal signs
.sect input
 == Heading 2 == foo
.sect expected
<h2>Heading 2 == foo</h2>

.test Line must start with equal sign
.sect input
foo = Heading 1 =
.sect expected
<p>foo = Heading 1 =</p>

.test Links
.sect input
[[link]]
.sect expected
<p><a href="http://example.net/wiki/link">link</a></p>

.test Links can appear in paragraphs
.sect input
Hello, [[world]]
.sect expected
<p>Hello, <a href="http://example.net/wiki/world">world</a></p>

.test Named links
.sect input
[[MyBigPage|Go to my page]]
.sect expected
<p><a href="http://example.net/wiki/MyBigPage">Go to my page</a></p>

.test URLs
.sect input
[[http://www.wikicreole.org/]]
.sect expected
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a></p>

.test Free-standing URL's should be turned into links
.sect input
http://www.wikicreole.org/
.sect expected
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a></p>

.test Single punctuation characters at end should not be part of URLs
.sect input
http://www.wikicreole.org/,

http://www.wikicreole.org/.

http://www.wikicreole.org/?

http://www.wikicreole.org/!

http://www.wikicreole.org/:

http://www.wikicreole.org/;

http://www.wikicreole.org/'

http://www.wikicreole.org/"

.sect expected
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>,</p>
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>.</p>
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>?</p>
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>!</p>
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>:</p>
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>;</p>
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>&#39;</p>
<p><a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a>&quot;</p>

.test Nameds URLs
.sect input
[[http://www.wikicreole.org/|Visit the WikiCreole website]]
.sect expected
<p><a href="http://www.wikicreole.org/">Visit the WikiCreole website</a></p>

.test Parsing markup within a link is optional
.sect input
[[Weird Stuff|**Weird** //Stuff//]]
.sect expected
<p><a href="http://example.net/wiki/Weird%20Stuff">**Weird** //Stuff//</a></p>

.test Links in bold
.sect input
**[[link]]**
.sect expected
<p><strong><a href="http://example.net/wiki/link">link</a></strong></p>

.test Whitespace inside brackets should be ignored
.sect input
[[ link ]]

[[ link me ]]

[[  http://dot.com/ |  dot.com ]]

[[  http://dot.com/ |  dot com ]]

.sect expected
<p><a href="http://example.net/wiki/link">link</a></p>
<p><a href="http://example.net/wiki/link%20me">link me</a></p>
<p><a href="http://dot.com/">dot.com</a></p>
<p><a href="http://dot.com/">dot com</a></p>

.test One or more blank lines end paragraphs
.sect input
This is
my text.

This is
more text.


This is
more more text.



This is
more more more text.
.sect expected
<p>This is my text.</p>
<p>This is more text.</p>
<p>This is more more text.</p>
<p>This is more more more text.</p>

.test A list end paragraphs
.sect input
Hello
* Item
.sect expected
<p>Hello</p>
<ul>
<li>Item</li>
</ul>

.test A table end paragraphs
.sect input
Hello
|Cell|
.sect expected
<p>Hello</p>
<table>
<tr><td>Cell</td></tr>
</table>

.test A nowiki end paragraphs
.sect input
Hello
{{{
nowiki
}}}
.sect expected
<p>Hello</p>
<pre>nowiki</pre>

.test A heading ends a paragraph (not specced)
.sect input
Hello
= Heading 1 =
.sect expected
<p>Hello</p>
<h1>Heading 1</h1>

.test Wiki-style for line breaks
.sect input
This is the first line,\\and this is the second.
.sect expected
<p>This is the first line,<br />
and this is the second.</p>

.test List items begin with a * at the beginning of a line
.sect input
* Item 1
* Item 2
* Item 3
.sect expected
<ul>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ul>

.test Whitespace is optional before and after the *
.sect input
   *    Item 1
*Item 2
    *       Item 3
.sect expected
<ul>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ul>

.test A space is required if if the list element starts with bold text
.sect input
* **Item 1
.sect expected
<ul>
<li><strong>Item 1</strong></li>
</ul>

.test An item ends at blank line
.sect input
* Item

Par
.sect expected
<ul>
<li>Item</li>
</ul>
<p>Par</p>

.test An item ends at blank line
.sect input
* Item
= Heading 1 =
.sect expected
<ul>
<li>Item</li>
</ul>
<h1>Heading 1</h1>

.test An item ends at a table
.sect input
* Item
|Cell|
.sect expected
<ul>
<li>Item</li>
</ul>
<table>
<tr><td>Cell</td></tr>
</table>

.test An item ends at a nowiki block
.sect input
* Item
{{{
Code
}}}
.sect expected
<ul>
<li>Item</li>
</ul>
<pre>Code</pre>

.test An item can span multiple lines
.sect input
* The quick
brown fox
    jumps over
lazy dog.
*Humpty Dumpty
sat 
on a wall.
.sect expected
<ul>
<li>The quick brown fox jumps over lazy dog.</li>
<li>Humpty Dumpty sat on a wall.</li>
</ul>

.test An item can contain line breaks
.sect input
* The quick brown\\fox jumps over lazy dog.
.sect expected
<ul>
<li>The quick brown<br />
fox jumps over lazy dog.</li>
</ul>

.test Nested
.sect input
* Item 1
 **Item 2
 *  Item 3
.sect expected
<ul>
<li>Item 1
<ul>
<li>Item 2</li>
</ul>
</li>
<li>Item 3</li>
</ul>

.test Nested up to 5 levels
.sect input
*Item 1
**Item 2
***Item 3
****Item 4
*****Item 5
.sect expected
<ul>
<li>Item 1
<ul>
<li>Item 2
<ul>
<li>Item 3
<ul>
<li>Item 4
<ul>
<li>Item 5</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>

.test following a list element will be treated as a nested one
.sect input
*Hello,
World!
**Not bold
.sect expected
<ul>
<li>Hello, World!
<ul>
<li>Not bold</li>
</ul>
</li>
</ul>

.test following a list element will be treated as a nested unordered one
.sect input
#Hello,
World!
**Not bold
.sect expected
<ol>
<li>Hello, World!
<ul>
<li>Not bold</li>
</ul>
</li>
</ol>

.test otherwise it will be treated as the beginning of bold text
.sect input
*Hello,
World!

**Bold
.sect expected
<ul>
<li>Hello, World!</li>
</ul>
<p><strong>Bold</strong></p>

.test List items begin with a sharp sign at the beginning of a line
.sect input
# Item 1
# Item 2
# Item 3
.sect expected
<ol>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ol>

.test Whitespace is optional before and after the sharps
.sect input
   #    Item 1
#Item 2
        #               Item 3
.sect expected
<ol>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ol>

.test A space is required if if the list element starts with bold text
.sect input
# **Item 1
.sect expected
<ol>
<li><strong>Item 1</strong></li>
</ol>

.test An item ends at blank line
.sect input
# Item

Par
.sect expected
<ol>
<li>Item</li>
</ol>
<p>Par</p>

.test An item ends at a heading
.sect input
# Item
= Heading 1 =
.sect expected
<ol>
<li>Item</li>
</ol>
<h1>Heading 1</h1>

.test An item ends at a table
.sect input
# Item
|Cell|
.sect expected
<ol>
<li>Item</li>
</ol>
<table>
<tr><td>Cell</td></tr>
</table>

.test An item ends at a nowiki block
.sect input
# Item
{{{
Code
}}}
.sect expected
<ol>
<li>Item</li>
</ol>
<pre>Code</pre>

.test An item can span multiple lines
.sect input
# The quick
brown fox
    jumps over
lazy dog.
#Humpty Dumpty
sat 
on a wall.
.sect expected
<ol>
<li>The quick brown fox jumps over lazy dog.</li>
<li>Humpty Dumpty sat on a wall.</li>
</ol>

.test An item can contain line breaks
.sect input
# The quick brown\\fox jumps over lazy dog.
.sect expected
<ol>
<li>The quick brown<br />
fox jumps over lazy dog.</li>
</ol>

.test Nested
.sect input
# Item 1
 ##Item 2
 #  Item 3
.sect expected
<ol>
<li>Item 1
<ol>
<li>Item 2</li>
</ol>
</li>
<li>Item 3</li>
</ol>

.test Nested up to 5 levels
.sect input
#Item 1
##Item 2
###Item 3
####Item 4
#####Item 5
.sect expected
<ol>
<li>Item 1
<ol>
<li>Item 2
<ol>
<li>Item 3
<ol>
<li>Item 4
<ol>
<li>Item 5</li>
</ol>
</li>
</ol>
</li>
</ol>
</li>
</ol>
</li>
</ol>

.test following a list element will be treated as a nested one
.sect input
#Hello,
World!
##Not monospace
.sect expected
<ol>
<li>Hello, World!
<ol>
<li>Not monospace</li>
</ol>
</li>
</ol>

.test following a list element will be treated as a nested ordered one
.sect input
*Hello,
World!
##Not bold
.sect expected
<ul>
<li>Hello, World!
<ol>
<li>Not bold</li>
</ol>
</li>
</ul>

.test otherwise it will be treated as the beginning of monospaced text
.sect input
#Hello,
World!

##Monospace
.sect expected
<ol>
<li>Hello, World!</li>
</ol>
<p><tt>Monospace</tt></p>

.test Ambiguity ol following ul
.sect input
*uitem
#oitem
.sect expected
<ul>
<li>uitem</li>
</ul>
<ol>
<li>oitem</li>
</ol>

.test Ambiguity ul following ol
.sect input
#oitem
*uitem
.sect expected
<ol>
<li>oitem</li>
</ol>
<ul>
<li>uitem</li>
</ul>

.test Ambiguity 2ol following ul
.sect input
*uitem
##oitem
.sect expected
<ul>
<li>uitem
<ol>
<li>oitem</li>
</ol>
</li>
</ul>

.test Ambiguity 2ul following ol
.sect input
#uitem
**oitem
.sect expected
<ol>
<li>uitem
<ul>
<li>oitem</li>
</ul>
</li>
</ol>

.test Ambiguity 3ol following 3ul
.sect input
***uitem
###oitem
.sect expected
<ul>
<li>uitem</li>
</ul>
<ol>
<li>oitem</li>
</ol>

.test Ambiguity 3ul following 3ol
.sect input
###oitem
***uitem
.sect expected
<ol>
<li>oitem</li>
</ol>
<ul>
<li>uitem</li>
</ul>

.test Ambiguity ol following 3ol
.sect input
###oitem1
#oitem2
.sect expected
<ol>
<li>oitem1</li>
<li>oitem2</li>
</ol>

.test Ambiguity ul following 3ol
.sect input
###oitem
*uitem
.sect expected
<ol>
<li>oitem</li>
</ol>
<ul>
<li>uitem</li>
</ul>

.test Ambiguity uncommon URL schemes should not be parsed as URLs
.sect input
This is what can go wrong://this should be an italic text//.
.sect expected
<p>This is what can go wrong:<em>this should be an italic text</em>.</p>

.test Ambiguity a link inside italic text
.sect input
How about //a link, like http://example.org, in italic// text?
.sect expected
<p>How about <em>a link, like <a href="http://example.org">http://example.org</a>, in italic</em> text?</p>

.test Ambiguity another test from Creole Wiki
.sect input
Formatted fruits, for example://apples//, oranges, **pears** ...

Blablabala (http://blub.de)
.sect expected
<p>Formatted fruits, for example:<em>apples</em>, oranges, <strong>pears</strong> ...</p>
<p>Blablabala (<a href="http://blub.de">http://blub.de</a>)</p>

.test Ambiguity Bolds and Lists
.sect input
** bold text **

 ** bold text **
.sect expected
<p><strong>bold text</strong></p>
<p><strong>bold text</strong></p>

.test Verbatim block
.sect input
{{{
Hello
}}}
.sect expected
<pre>Hello</pre>

.test Nowiki inline
.sect input
Hello {{{world}}}.
.sect expected
<p>Hello <code>world</code>.</p>

.test No wiki markup is interpreted inbetween
.sect input
{{{
**Hello**
}}}
.sect expected
<pre>**Hello**</pre>

.test Leading whitespaces are not permitted
.sect input
 {{{
Hello
}}}
.sect expected
<p><code>
Hello
</code></p>

.test Leading whitespaces are not permitted 2
.sect input
{{{
Hello
 }}}
.sect expected
<p><code>
Hello
</code></p>

.test Assumed should preserve whitespace
.sect input
{{{
    Hello,  
     World   
}}}
.sect expected
<pre>    Hello,  
     World</pre>

.test In preformatted blocks, one leading space is removed
.sect input
{{{
nowikiblock
 }}}
}}}
.sect expected
<pre>nowikiblock
&#125;&#125;&#125;</pre>

.test In inline nowiki, any trailing closing brace is included in the span
.sect input
this is {{{nowiki}}}}

this is {{{nowiki}}}}}

this is {{{nowiki}}}}}}

this is {{{nowiki}}}}}}}
.sect expected
<p>this is <code>nowiki&#125;</code></p>
<p>this is <code>nowiki&#125;&#125;</code></p>
<p>this is <code>nowiki&#125;&#125;&#125;</code></p>
<p>this is <code>nowiki&#125;&#125;&#125;&#125;</code></p>

.test Special HTML chars should be escaped
.sect input
<b>not bold</b>
.sect expected
<p>&lt;b&gt;not bold&lt;/b&gt;</p>

.test Image tags should be escape
.sect input
{{image.jpg|"tag"}}
.sect expected
<p><img src="http://example.net/static/image.jpg" alt="&quot;tag&quot;" /></p>

.test Malicious links should not be converted
.sect input
[[javascript:alert("Boo!")|Click]]
.sect expected
<p>[[javascript:alert(&quot;Boo!&quot;)|Click]]</p>

.test Escapes
.sect input
~** Not Bold ~** ~// Not Italic ~//
~* Not Bullet
.sect expected
<p>** Not Bold ** // Not Italic // * Not Bullet</p>

.test Escapes following char is not a blank
.sect input
Hello ~ world
Hello ~
world
.sect expected
<p>Hello ~ world Hello ~ world</p>

.test Not escaping inside URLs
.sect input
http://example.org/~user/
.sect expected
<p><a href="http://example.org/~user/">http://example.org/~user/</a></p>

.test Escaping links
.sect input
~http://example.org/~user/
.sect expected
<p>http://example.org/~user/</p>

.test Four hyphens make a horizontal rule
.sect input
----
.sect expected
<hr />

.test Whitespaces around hyphens are allowed
.sect input
 ----
----  
  ----  
.sect expected
<hr />
<hr />
<hr />

.test Nothing else than hyphens and whitespace is allowed
.sect input
foo ----

---- foo

  -- --  
.sect expected
<p>foo ----</p>
<p>---- foo</p>
<p>-- --</p>

.test Tables
.sect input
|Hello, World!|
.sect expected
<table>
<tr><td>Hello, World!</td></tr>
</table>

.test Tables multiple columns
.sect input
|c1|c2|c3|
.sect expected
<table>
<tr><td>c1</td><td>c2</td><td>c3</td></tr>
</table>

.test Tables multiple rows
.sect input
|c11|c12|
|c21|c22|
.sect expected
<table>
<tr><td>c11</td><td>c12</td></tr>
<tr><td>c21</td><td>c22</td></tr>
</table>

.test Tables end pipe is optional
.sect input
|c1|c2|c3
.sect expected
<table>
<tr><td>c1</td><td>c2</td><td>c3</td></tr>
</table>

.test Tables empty cells
.sect input
|c1||c3
.sect expected
<table>
<tr><td>c1</td><td></td><td>c3</td></tr>
</table>

.test Tables escaping cell separator
.sect input
|c1~|c2|c3
.sect expected
<table>
<tr><td>c1|c2</td><td>c3</td></tr>
</table>

.test Tables escape in last cell + empty cell
.sect input
|c1|c2~|
|c1|c2~||
|c1|c2~|||
.sect expected
<table>
<tr><td>c1</td><td>c2|</td></tr>
<tr><td>c1</td><td>c2|</td></tr>
<tr><td>c1</td><td>c2|</td><td></td></tr>
</table>

.test Tables equal sign after pipe make a header
.sect input
|=Header|
.sect expected
<table>
<tr><th>Header</th></tr>
</table>

.test Tables pipes in links or images
.sect input
|c1|[[Link|Link text]]|{{Image|Image text}}|
.sect expected
<table>
<tr><td>c1</td><td><a href="http://example.net/wiki/Link">Link text</a></td><td><img src="http://example.net/static/Image" alt="Image text" /></td></tr>
</table>

.test Tables followed by heading
.sect input
|table|
=heading 1=

|table|

=heading 2=
.sect expected
<table>
<tr><td>table</td></tr>
</table>
<h1>heading 1</h1>
<table>
<tr><td>table</td></tr>
</table>
<h1>heading 2</h1>

.test Tables followed by paragraph
.sect input
|table|
par

|table|

par
.sect expected
<table>
<tr><td>table</td></tr>
</table>
<p>par</p>
<table>
<tr><td>table</td></tr>
</table>
<p>par</p>

.test Tables followed by unordered list
.sect input
|table|
*item
.sect expected
<table>
<tr><td>table</td></tr>
</table>
<ul>
<li>item</li>
</ul>

.test Tables followed by ordered list
.sect input
|table|
#item

|table|

#item
.sect expected
<table>
<tr><td>table</td></tr>
</table>
<ol>
<li>item</li>
</ol>
<table>
<tr><td>table</td></tr>
</table>
<ol>
<li>item</li>
</ol>

.test Tables followed by horizontal rule
.sect input
|table|
----

|table|

----
.sect expected
<table>
<tr><td>table</td></tr>
</table>
<hr />
<table>
<tr><td>table</td></tr>
</table>
<hr />

.test Tables followed by verbatim
.sect input
|table|
{{{
verbatim
}}}

|table|

{{{
verbatim
}}}
.sect expected
<table>
<tr><td>table</td></tr>
</table>
<pre>verbatim</pre>
<table>
<tr><td>table</td></tr>
</table>
<pre>verbatim</pre>

.test Tables followed by table
.sect input
|table|
|table|

|table|
.sect expected
<table>
<tr><td>table</td></tr>
<tr><td>table</td></tr>
</table>
<table>
<tr><td>table</td></tr>
</table>

.test Headings followed by headings
.sect input
=heading 1
=heading 2

=heading 3
.sect expected
<h1>heading 1</h1>
<h1>heading 2</h1>
<h1>heading 3</h1>

.test Headings followed by paragraphs
.sect input
=heading 1
par

=heading 2

par
.sect expected
<h1>heading 1</h1>
<p>par</p>
<h1>heading 2</h1>
<p>par</p>

.test Headings followed by unordered list
.sect input
=heading 1
*item

=heading 2

*item
.sect expected
<h1>heading 1</h1>
<ul>
<li>item</li>
</ul>
<h1>heading 2</h1>
<ul>
<li>item</li>
</ul>

.test Headings followed by ordered list
.sect input
=heading 1
#item

=heading 2

#item
.sect expected
<h1>heading 1</h1>
<ol>
<li>item</li>
</ol>
<h1>heading 2</h1>
<ol>
<li>item</li>
</ol>

.test Headings followed by horizontal rule
.sect input
=heading 1
----

=heading 2

----
.sect expected
<h1>heading 1</h1>
<hr />
<h1>heading 2</h1>
<hr />

.test Headings followed by verbatim
.sect input
=heading 1
{{{
verbatim
}}}

=heading 2

{{{
verbatim
}}}
.sect expected
<h1>heading 1</h1>
<pre>verbatim</pre>
<h1>heading 2</h1>
<pre>verbatim</pre>

.test Headings followed by table
.sect input
=heading 1
|cell

=heading 2

|cell
.sect expected
<h1>heading 1</h1>
<table>
<tr><td>cell</td></tr>
</table>
<h1>heading 2</h1>
<table>
<tr><td>cell</td></tr>
</table>

.test Paragraphs followed by headings
.sect input
par
=heading 1

par

=heading 2
.sect expected
<p>par</p>
<h1>heading 1</h1>
<p>par</p>
<h1>heading 2</h1>

.test Paragraphs followed by paragraphs
.sect input
par
par

par

par
.sect expected
<p>par par</p>
<p>par</p>
<p>par</p>

.test Paragraphs followed by unordered list
.sect input
par
*item

par

*item
.sect expected
<p>par</p>
<ul>
<li>item</li>
</ul>
<p>par</p>
<ul>
<li>item</li>
</ul>

.test Paragraphs followed by ordered list
.sect input
par
#item

par

#item
.sect expected
<p>par</p>
<ol>
<li>item</li>
</ol>
<p>par</p>
<ol>
<li>item</li>
</ol>

.test Paragraphs followed by horizontal rule
.sect input
par
----

par

----
.sect expected
<p>par</p>
<hr />
<p>par</p>
<hr />

.test Paragraphs followed by verbatim
.sect input
par
{{{
verbatim
}}}

par

{{{
verbatim
}}}
.sect expected
<p>par</p>
<pre>verbatim</pre>
<p>par</p>
<pre>verbatim</pre>

.test Paragraphs followed by table
.sect input
par
|cell

par

|cell
.sect expected
<p>par</p>
<table>
<tr><td>cell</td></tr>
</table>
<p>par</p>
<table>
<tr><td>cell</td></tr>
</table>

.test Unordered list followed by headings
.sect input
*item
=heading 1

*item

=heading 2
.sect expected
<ul>
<li>item</li>
</ul>
<h1>heading 1</h1>
<ul>
<li>item</li>
</ul>
<h1>heading 2</h1>

.test Unordered list followed by paragraphs
.sect input
*item
par

*item

par
.sect expected
<ul>
<li>item par</li>
</ul>
<ul>
<li>item</li>
</ul>
<p>par</p>

.test Unordered list followed by unordered list
.sect input
*item
*item

*item

*item
.sect expected
<ul>
<li>item</li>
<li>item</li>
</ul>
<ul>
<li>item</li>
</ul>
<ul>
<li>item</li>
</ul>

.test Unordered list followed by ordered list
.sect input
*item
#item

*item

#item
.sect expected
<ul>
<li>item</li>
</ul>
<ol>
<li>item</li>
</ol>
<ul>
<li>item</li>
</ul>
<ol>
<li>item</li>
</ol>

.test Unordered list followed by horizontal rule
.sect input
*item
----

*item

----
.sect expected
<ul>
<li>item</li>
</ul>
<hr />
<ul>
<li>item</li>
</ul>
<hr />

.test Unordered list followed by verbatim
.sect input
*item
{{{
verbatim
}}}

*item

{{{
verbatim
}}}
.sect expected
<ul>
<li>item</li>
</ul>
<pre>verbatim</pre>
<ul>
<li>item</li>
</ul>
<pre>verbatim</pre>

.test Unordered list followed by table
.sect input
*item
|cell

*item

|cell
.sect expected
<ul>
<li>item</li>
</ul>
<table>
<tr><td>cell</td></tr>
</table>
<ul>
<li>item</li>
</ul>
<table>
<tr><td>cell</td></tr>
</table>

.test Ordered list followed by headings
.sect input
#item
=heading 1

#item

=heading 2
.sect expected
<ol>
<li>item</li>
</ol>
<h1>heading 1</h1>
<ol>
<li>item</li>
</ol>
<h1>heading 2</h1>

.test Ordered list followed by paragraphs
.sect input
#item
par

#item

par
.sect expected
<ol>
<li>item par</li>
</ol>
<ol>
<li>item</li>
</ol>
<p>par</p>

.test Ordered list followed by unordered list
.sect input
#item
*item

#item

*item
.sect expected
<ol>
<li>item</li>
</ol>
<ul>
<li>item</li>
</ul>
<ol>
<li>item</li>
</ol>
<ul>
<li>item</li>
</ul>

.test Ordered list followed by ordered list
.sect input
#item
#item

#item

#item
.sect expected
<ol>
<li>item</li>
<li>item</li>
</ol>
<ol>
<li>item</li>
</ol>
<ol>
<li>item</li>
</ol>

.test Ordered list followed by horizontal rule
.sect input
#item
----

#item

----
.sect expected
<ol>
<li>item</li>
</ol>
<hr />
<ol>
<li>item</li>
</ol>
<hr />

.test Ordered list followed by verbatim
.sect input
#item
{{{
verbatim
}}}

#item

{{{
verbatim
}}}
.sect expected
<ol>
<li>item</li>
</ol>
<pre>verbatim</pre>
<ol>
<li>item</li>
</ol>
<pre>verbatim</pre>

.test Ordered list followed by table
.sect input
#item
|cell

#item

|cell
.sect expected
<ol>
<li>item</li>
</ol>
<table>
<tr><td>cell</td></tr>
</table>
<ol>
<li>item</li>
</ol>
<table>
<tr><td>cell</td></tr>
</table>

.test Horizontal rules followed by headings
.sect input
----
=heading 1

----

=heading 2
.sect expected
<hr />
<h1>heading 1</h1>
<hr />
<h1>heading 2</h1>

.test Horizontal rules followed by paragraphs
.sect input
----
par

----

par
.sect expected
<hr />
<p>par</p>
<hr />
<p>par</p>

.test Horizontal rules followed by unordered list
.sect input
----
*item

----

*item
.sect expected
<hr />
<ul>
<li>item</li>
</ul>
<hr />
<ul>
<li>item</li>
</ul>

.test Horizontal rules followed by ordered list
.sect input
----
#item

----

#item
.sect expected
<hr />
<ol>
<li>item</li>
</ol>
<hr />
<ol>
<li>item</li>
</ol>

.test Horizontal rules followed by horizontal rule
.sect input
----
----

----

----
.sect expected
<hr />
<hr />
<hr />
<hr />

.test Horizontal rules followed by verbatim
.sect input
----
{{{
verbatim
}}}

----

{{{
verbatim
}}}
.sect expected
<hr />
<pre>verbatim</pre>
<hr />
<pre>verbatim</pre>

.test Horizontal rules followed by table
.sect input
----
|cell

----

|cell
.sect expected
<hr />
<table>
<tr><td>cell</td></tr>
</table>
<hr />
<table>
<tr><td>cell</td></tr>
</table>

.test Verbatims followed by headings
.sect input
{{{
verbatim
}}}
=heading 1

{{{
verbatim
}}}

=heading 2
.sect expected
<pre>verbatim</pre>
<h1>heading 1</h1>
<pre>verbatim</pre>
<h1>heading 2</h1>

.test Verbatims followed by paragraphs
.sect input
{{{
verbatim
}}}
par

{{{
verbatim
}}}

par
.sect expected
<pre>verbatim</pre>
<p>par</p>
<pre>verbatim</pre>
<p>par</p>

.test Verbatims followed by unordered list
.sect input
{{{
verbatim
}}}
*item

{{{
verbatim
}}}

*item
.sect expected
<pre>verbatim</pre>
<ul>
<li>item</li>
</ul>
<pre>verbatim</pre>
<ul>
<li>item</li>
</ul>

.test Verbatims followed by ordered list
.sect input
{{{
verbatim
}}}
#item

{{{
verbatim
}}}

#item
.sect expected
<pre>verbatim</pre>
<ol>
<li>item</li>
</ol>
<pre>verbatim</pre>
<ol>
<li>item</li>
</ol>

.test Verbatims followed by horizontal rule
.sect input
{{{
verbatim
}}}
----

{{{
verbatim
}}}

----
.sect expected
<pre>verbatim</pre>
<hr />
<pre>verbatim</pre>
<hr />

.test Verbatims followed by verbatim
.sect input
{{{
verbatim
}}}
{{{
verbatim
}}}

{{{
verbatim
}}}

{{{
verbatim
}}}
.sect expected
<pre>verbatim</pre>
<pre>verbatim</pre>
<pre>verbatim</pre>
<pre>verbatim</pre>

.test Verbatims followed by table
.sect input
{{{
verbatim
}}}
|cell

{{{
verbatim
}}}

|cell
.sect expected
<pre>verbatim</pre>
<table>
<tr><td>cell</td></tr>
</table>
<pre>verbatim</pre>
<table>
<tr><td>cell</td></tr>
</table>

.test Images
.sect input
{{image.jpg}}

{{image.jpg|tag}}

{{http://example.org/image.jpg}}
.sect expected
<p><img src="http://example.net/static/image.jpg" alt="" /></p>
<p><img src="http://example.net/static/image.jpg" alt="tag" /></p>
<p><img src="http://example.org/image.jpg" alt="" /></p>

.test Bold combo
.sect input
**bold and
|table|
end**
.sect expected
<p><strong>bold and</strong></p>
<table>
<tr><td>table</td></tr>
</table>
<p>end<strong></strong></p>
"""

class TestCreolize(unittest.TestCase):
    spec = SPEC

    def runTest(self, block):
        got = creolize.Creolize().convert(block['input']).result
        self.assertNotDiff(got, block['expected'], block['name'])

    def assertNotDiff(self, first, second, msg=None):
        if first == second:
            return
        a = [line + '\n' for line in first.splitlines()]
        b = [line + '\n' for line in second.splitlines()]
        d = ''.join(difflib.unified_diff(a, b, fromfile='first', tofile='second'))
        if d != '':
            if msg is None:
                msg = 'got != expected'
            raise self.failureException, msg + '\n' + d

    def _run_block(self, block, result):
        result.startTest(self)
        testMethod = getattr(self, self._testMethodName)
        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                return

            ok = False
            try:
                testMethod(block)
                ok = True
            except self.failureException:
                result.addFailure(self, self._exc_info())
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                ok = False
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)

    def run(self, result=None):
        if result is None: result = self.defaultTestResult()
        re_block = re.compile(r'''
            ^\.test[\t\x20]+(.+?)\n(.*?)(?=^\.test|\Z)
        ''', re.M|re.S|re.X)
        re_part = re.compile(r'''
            ^\.sect[\t\x20]+(.+?)\n(.*?)(?=^\.test|^\.sect|\Z)
        ''', re.M|re.S|re.X)
        for m_block in re_block.finditer(self.spec):
            block = {}
            block['name'] = m_block.group(1).rstrip(' ')
            block_body = m_block.group(2)
            for m_part in re_part.finditer(block_body):
                part_name = m_part.group(1).rstrip(' ')
                part_body = m_part.group(2).rstrip('\r\n ')
                block[part_name] = part_body
            self._testMethodDoc = block['name']
            self._run_block(block, result)

if __name__ == '__main__':
    unittest.main()

