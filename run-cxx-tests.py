#!/usr/bin/env python


"""
run all c++ tests in a directory.

The c++ test src file can be marked as skip by:

// skip = <reason>

"""


import fnmatch
import os


def findTestSources(root='.', like='test*.cc'):
    rt = []
    for root, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, like):
            rt.append(os.path.join(root, filename))
    return rt


def findCorrespondingBinary(src, ext='.cc'):
    assert src.endswith(ext)
    return src[:-len(ext)]


class NoTestBinary(Exception): pass
class TestRunFailed(Exception): pass


import shlex, subprocess

def spawn(cmd, cwd=None, env=None, stdin=None, stdout=None, stderr=None):
    '''spawn a new process

    cmd: the command to execute in the new process
    cwd: the directory where the command will be executed
    env: the environment dictionary
    stdin, stdout, stderr:

    return: new process
    '''
    args = shlex.split(cmd)
    p = subprocess.Popen(args, cwd=cwd, env=env, stdin=stdin, stdout=stdout, stderr=stderr)
    return p


def execute(cmd, input=None, cwd=None, env=None):
    '''execute a command and return the returncode, stdout data, and stderr data
    '''
    print '* executing %s...' % cmd
    p = spawn(
        cmd, cwd=cwd, env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    outdata, errdata = p.communicate(input=input)
    retcode = p.wait()
    return retcode, outdata, errdata


def getSrcMetadata(src):
    s = open(src)
    sig = '// skip ='
    found = None
    # read 10 lines
    for i in range(10):
        line = s.readline()
        if line.startswith(sig):
            found = line
        continue
    if found:
        v = found[len(sig):].strip()
        try: v = eval(v)
        except: pass
        return {'skip':v}
    return


def runtest(src, dry=False):
    print '* %s' % src
    bin = findCorrespondingBinary(src)
    if not os.path.exists(bin): raise NoTestBinary
    dirname = os.path.dirname(bin)
    fn = os.path.basename(bin)
    cmd = './%s' % (fn,)
    if dry:
        print "* running %s in %s" % (cmd, dirname)
        return
    code, out, err = execute(cmd, cwd=dirname)
    if code:
        raise TestRunFailed, '%s failed: out:\n%serr:\n%s' % (
            src, out, err)
    return


def runtests(root='.', dry=False):
    sources = findTestSources(root)
    nobinaries = []
    failed = []
    skipped = []
    for src in sources:
        meta = getSrcMetadata(src)
        if meta and meta['skip']:
            skipped.append((src, meta['skip']))
            continue
        try: runtest(src, dry=dry)
        except NoTestBinary:
            nobinaries.append(src)
        except TestRunFailed, e:
            failed.append((src, e))
        continue
    return sources, nobinaries, failed, skipped


def createReport(sources, nobinaries, failed, skipped):
    print
    print "Report:"
    if not nobinaries and not failed:
        print '* SUCCEED'
    else:
        print '* FAILED'
    
    npassed = len(sources) - len(nobinaries) - len(failed) - len(skipped)
    s = '* Out of %s tests, %s passed' % (len(sources), npassed)
    if nobinaries:
        s += ', %s have no test binaries' % (len(nobinaries),)
    if failed:
        s += ', %s failed' % (len(failed),)
    if skipped:
        s += ', skipped %s' % (len(skipped),)
    print s
    
    if nobinaries:
        print " - no binaries:"
        for item in nobinaries:
            print item
    
    if failed:
        print " - failed:"
        for src, e in failed:
            print e
    
    if skipped:
        print " - skipped:"
        for src, reason in skipped:
            print "%s: %s" % (src, reason)

    # 
    if nobinaries or failed:
        import sys
        sys.exit(1)
    return


def main():
    
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-d', '--dry-run', action='store_true', dest='dry')
    opts, args = parser.parse_args()
    
    if len(args) > 1: raise NotImplementedError
    if len(args) == 1:
        path = args[0]
    else:
        path = os.curdir
    
    dry = opts.dry
    
    res = runtests(path, dry=dry)
    createReport(*res)
    
    return


if __name__ == '__main__': main()

