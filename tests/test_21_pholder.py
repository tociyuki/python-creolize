import unittest
import re
import difflib
import creolize

SPEC = r"""
.test Place holder one line
.sect input
<<<hoge>>>
.sect expected
<p>hoge</p>

.test Place holder few lines
.sect input
<<<hoge
fuga
>>>
.sect expected
<p>hoge
fuga</p>

.test Place holder escape xml
.sect input
<<< <div class="hoge">hoge&amp;</div> >>>
.sect expected
<p>&lt;div class=&quot;hoge&quot;&gt;hoge&amp;amp;&lt;/div&gt;</p>
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

