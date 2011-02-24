import unittest
import re
import difflib
import creolize

SPEC = r"""
.test Headings in Creole 1.0 Test
.sect input
= Top-level heading (1)
== This a test for creole 0.1 (2)
=== This is a Subheading (3)
==== Subsub (4)
===== Subsubsub (5)
.sect expected
<h1>Top-level heading (1)</h1>
<h2>This a test for creole 0.1 (2)</h2>
<h3>This is a Subheading (3)</h3>
<h4>Subsub (4)</h4>
<h5>Subsubsub (5)</h5>

.test End equals in Creole 1.0 Test
.sect input
= Top-level heading (1) =
== This a test for creole 0.1 (2) ==
=== This is a Subheading (3) ===
==== Subsub (4) ====
===== Subsubsub (5) =====
.sect expected
<h1>Top-level heading (1)</h1>
<h2>This a test for creole 0.1 (2)</h2>
<h3>This is a Subheading (3)</h3>
<h4>Subsub (4)</h4>
<h5>Subsubsub (5)</h5>

.test Level 6 and mores
.sect input
====== Level 6
======= Level 7
======== Level 8
.sect expected
<h6>Level 6</h6>
<h6>Level 7</h6>
<h6>Level 8</h6>

.test End equals more
.sect input
= a2 ==
= a3 ===
= a4 ====
= a5 =====
== b1 =
== b3 ===
== b4 ====
== b5 =====
.sect expected
<h1>a2</h1>
<h1>a3</h1>
<h1>a4</h1>
<h1>a5</h1>
<h2>b1</h2>
<h2>b3</h2>
<h2>b4</h2>
<h2>b5</h2>

.test Left Paddings
.sect input
=A
 =B
= C
 = D
.sect expected
<h1>A</h1>
<h1>B</h1>
<h1>C</h1>
<h1>D</h1>

.test Right Paddings
.sect input
= A=
= B =
= C= 
= D = 
.sect expected
<h1>A</h1>
<h1>B</h1>
<h1>C</h1>
<h1>D</h1>

.test Equal signs in text
.sect input
= a = b =
= = a =
= a = =
.sect expected
<h1>a = b</h1>
<h1>= a</h1>
<h1>a =</h1>

.test Escaped equals
.sect input
= a1 ~=
= a2 ~==
= a3 ~===
= b1 ~= =
= b2 ~== =
= b3 ~=== =
.sect expected
<h1>a1 =</h1>
<h1>a2 ==</h1>
<h1>a3 ===</h1>
<h1>b1 =</h1>
<h1>b2 ==</h1>
<h1>b3 ===</h1>

.test Heading between Paragraphs
.sect input
a b c.
= A
d e f.
.sect expected
<p>a b c.</p>
<h1>A</h1>
<p>d e f.</p>
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

