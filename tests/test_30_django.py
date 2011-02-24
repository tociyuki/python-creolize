import unittest
import re
import difflib
import creolize

SPEC = r"""
.test single squoted string
.sect input
You can make things **bold** or //italic// or **//both//** or //**both**//.

Character formatting extends across line breaks: **bold,
this is still bold. This line deliberately does not end in star-star.

Not bold. Character formatting does not cross paragraph boundaries.

Here's a external link without a description: [[http://www.wikicreole.org]]

Free links without braces should be rendered as well, like http://www.wikicreole.org/ and http://www.wikicreole.org/users/~example. 

.sect expected
<p>You can make things <strong>bold</strong> or <em>italic</em> or <strong><em>both</em></strong> or <em><strong>both</strong></em>.</p>
<p>Character formatting extends across line breaks: <strong>bold, this is still bold. This line deliberately does not end in star-star.</strong></p>
<p>Not bold. Character formatting does not cross paragraph boundaries.</p>
<p>Here&#39;s a external link without a description: <a href="http://www.wikicreole.org">http://www.wikicreole.org</a></p>
<p>Free links without braces should be rendered as well, like <a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a> and <a href="http://www.wikicreole.org/users/~example">http://www.wikicreole.org/users/~example</a>.</p>

.test escaped internal link
.sect input
You can use ~[[internal links]].

give the link a ~[[internal links|different]] name.

.sect expected
<p>You can use [[internal links]].</p>
<p>give the link a [[internal links|different]] name.</p>

.test internal link
.sect input
You can use [[internal links]].

give the link a [[internal links|different]] name.

.sect expected
<p>You can use {% wiki_link 'internal%20links','internal links' %}.</p>
<p>give the link a {% wiki_link 'internal%20links','different' %} name.</p>

.test plugin
.sect input
Modified << last_modified >>.
.sect expected
<p>Modified {% wiki_plugin last_modified %}.</p>
"""

class TestCreolize(unittest.TestCase):
    spec = SPEC

    def runTest(self, block):
        creo = creolize.Creolize()
        creo.type = 'django'
        got = creo.convert(block['input']).result
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

