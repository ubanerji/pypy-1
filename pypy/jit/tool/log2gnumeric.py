#! /usr/bin/env python
"""
Usage: log2gnumeric logfile

Produces a logfile.gnumeric file which contains the data extracted from the
logfile generated with the PYPYLOG env variable.

Currently, it expects log to contain the translation-task and gc-collect
categories.

You can freely edit the graph in log-template.gnumeric: this script will
create a new file replacing the 'translation-task' and 'gc-collect' sheets.
"""

import re, sys
import gzip


def main():
    logname = sys.argv[1]
    outname = logname + '.gnumeric'
    data = open(logname).read()
    data = data.replace('\n', '')
    minclock, maxclock = get_clock_range(data)
    time0 = minclock # we want "relative clocks"
    maxtime = maxclock-time0
    #
    xml = gzip.open('log-template.gnumeric').read()
    xml = replace_sheet(xml, 'translation-task', tasks_rows(time0, data))
    xml = replace_sheet(xml, 'gc-collect', gc_collect_rows(time0, data))
    xml = replace_sheet(xml, 'loops', loops_rows(time0, data))
    xml = replace_sheet(xml, 'vmrss', memusage_rows(logname + '.vmrss', maxtime))
    #
    out = gzip.open(outname, 'wb')
    out.write(xml)
    out.close()


# ========================================================================
# functions to manipulate gnumeric files
# ========================================================================

def replace_sheet(xml, sheet_name, data):
    pattern = '<gnm:Sheet .*?<gnm:Name>%s</gnm:Name>.*?(<gnm:Cells>.*?</gnm:Cells>)'
    regex = re.compile(pattern % sheet_name, re.DOTALL)
    cells = gen_cells(data)
    match = regex.search(xml)
    if not match:
        print 'Cannot find sheet %s' % sheet_name
        return xml
    a, b = match.span(1)
    xml2 = xml[:a] + cells + xml[b:]
    return xml2

def gen_cells(data):
    # values for the ValueType attribute
    ValueType_Empty  = 'ValueType="10"'
    ValueType_Number = 'ValueType="40"'
    ValueType_String = 'ValueType="60"'
    #
    parts = []
    parts.append('<gnm:Cells>')
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            if val is None:
                attr = ValueType_Empty
                val = ''
            elif isinstance(val, (int, long, float)):
                attr = ValueType_Number
            else:
                attr = ValueType_String
            cell = '        <gnm:Cell Row="%d" Col="%d" %s>%s</gnm:Cell>'
            parts.append(cell % (i, j, attr, val))
    parts.append('      </gnm:Cells>')
    return '\n'.join(parts)
    

# ========================================================================
# functions to extract various data from the logs
# ========================================================================

def get_clock_range(data):
    s = r"\[([0-9a-f]+)\] "
    r = re.compile(s)
    clocks = [int(x, 16) for x in r.findall(data)]
    return min(clocks), max(clocks)

def gc_collect_rows(time0, data):
    s = r"""
----------- Full collection ------------------
\| used before collection:
\|          in ArenaCollection:      (\d+) bytes
\|          raw_malloced:            (\d+) bytes
\| used after collection:
\|          in ArenaCollection:      (\d+) bytes
\|          raw_malloced:            (\d+) bytes
\| number of major collects:         (\d+)
`----------------------------------------------
\[([0-9a-f]+)\] gc-collect\}"""
    #
    r = re.compile(s.replace('\n', ''))
    yield 'clock', 'gc-before', 'gc-after'
    for a,b,c,d,e,f in r.findall(data):
        clock = int(f, 16) - time0
        yield clock, int(a)+int(b), int(c)+int(d)

def tasks_rows(time0, data):
    s = r"""
\[([0-9a-f]+)\] \{translation-task
starting ([\w-]+)
"""
    #
    r = re.compile(s.replace('\n', ''))
    yield 'clock', None, 'task'
    for a,b in r.findall(data):
        clock = int(a, 16) - time0
        yield clock, 1, b


def loops_rows(time0, data):
    s = r"""
\[([0-9a-f]+)\] \{jit-mem-looptoken-(alloc|free)
(.*?)\[
"""
    #
    r = re.compile(s.replace('\n', ''))
    yield 'clock', 'total', 'loops', 'bridges'
    loops = 0
    bridges = 0
    for clock, action, text in r.findall(data):
        clock = int(clock, 16) - time0
        if text.startswith('allocating Loop #'):
            loops += 1
        elif text.startswith('allocating Bridge #'):
            bridges += 1
        elif text.startswith('freeing Loop #'):
            match = re.match('freeing Loop # .* with ([0-9]*) attached bridges', text)
            loops -=1
            bridges -= int(match.group(1))
        total = loops+bridges
        yield clock, loops+bridges, loops, bridges


def memusage_rows(filename, maxtime):
    try:
        lines = open(filename).readlines()
    except IOError:
        print 'Warning: cannot find file %s, skipping the memusage sheet'
        lines = []
    for row in memusage_rows_impl(lines, maxtime):
        yield row

def memusage_rows_impl(lines, maxtime):
    yield 'inferred clock', 'VmRSS'
    numlines = len(lines)
    for i, line in enumerate(lines):
        mem = int(line)
        clock = maxtime * i // (numlines-1)
        yield clock, mem


if __name__ == '__main__':
    main()
