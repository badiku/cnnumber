# 参考 中华人民共和国国家标准-出版物上数字用法的规定
中文小写 = '一二三四五六七八九十百千'
中文大写 = '壹贰叁肆伍陆柒捌玖拾佰仟'
中文大写to小写 = dict((u, 中文小写[i]) for i,u in enumerate(中文大写))
中文小写to大写 = dict((u, 中文大写[i]) for i,u in enumerate(中文小写))


中文小写数字 = list(enumerate( '零一二三四五六七八九十'))
单个中文to数字 = dict((c,n) for n,c in 中文小写数字)
单个中文to数字['百'] = 100
单个中文to数字['千'] = 1000
单个中文to数字['万'] = 10000
单个中文to数字['亿'] = 10000*10000

单个数字to中文 = dict((n,c) for c,n in 单个中文to数字.items())


def 大写to小写(s):
    return ''.join((中文大写to小写[c] if c in 中文大写 else c)  for c in list(s))


def 小写to大写(s):
    return ''.join((中文小写to大写[c] if c in 中文小写 else c)  for c in list(s))


def _解析一位中文数字(s, unit):
    if unit not in s: return 0
    n = 1
    unitn = 单个中文to数字[unit]
    s = s.rsplit(unit, 1)[0]
    if s.isdigit():
        n = int(s)
        assert n < unitn, f'{unit}这一位的系数最多{unitn}: {s}{unit}'
    else:
        if len(s) > 1:
            assert False, f'这一部分系数不是一位中文数字: {s}{unit}'
        if len(s) == 1:
            assert s in 单个中文to数字, f'这一部分系数不是一位中文数字: {s}{unit}'
            n = 单个中文to数字[s]
    return n * unitn


def _中文到数字(s):
    if s.isdigit():
        return int(s)
    s = s.replace('零', '').replace('〇', '').replace('貮', '二').replace('两', '二')
    n = 0
    unitn = 0
    for unit in list('亿万'):
        if unit not in s: continue
        unitn = 单个中文to数字[unit]
        pre, s = s.rsplit(unit, 1)
        pren = _中文到数字(pre)
        if (unit == '万') and ('亿' in s):
            assert pren < unitn, f'{unit}这一位的系数最多{unitn}: {pre}{unit}'
        n = _中文到数字(s)
        assert n < unitn, f'{unit}这一位后面最多{unitn}: {s}'
        return pren * unitn  +  n

    units = list('千百十')
    for unit in units:
        if unit not in s: continue
        unitn = 单个中文to数字[unit]
        n = n + _解析一位中文数字(s, unit)
        s = s.rsplit(unit, 1)[-1]
    if (s in 单个中文to数字):
                return n + 单个中文to数字[s]
    if s.isdigit():
        return n + int(s)
    assert s == '',  f'这一部分不是一位中文数字: {s}'
    return n

def 解析中文到数字(s):
    s = 大写to小写(s.strip())
    if s and s[0] == '负':
        return - 解析中文到数字(s[1:])
    if len(s) >= 2 and s[-1] in 单个中文to数字 and 单个中文to数字[s[-1]] < 10 and s[-2] in '万千百' :   # 三万八 这一种
        return _中文到数字(s[:-1]) + 单个中文to数字[s[-2]] // 10 * 单个中文to数字[ s[-1] ]
    else:
        return _中文到数字(s)


def _数字到中文(n):
    # 分段,从小到大依次处理 个十 百千 万亿 6个范围即可
    if n < 0 :
        return '负' + _数字到中文(-n)
    if n < 10 :
        return 单个数字to中文[n]
    if 10 <= n < 100:
        pre, n = divmod(n, 10)
        return 单个数字to中文[pre] + '十' + (单个数字to中文[n] if n > 0 else '')
    if 100 <= n < 10000:
        s = ''
        for unit in list('千百十'):
            unitn = 单个中文to数字[unit]
            if n >= unitn:
                pre, n = divmod(n, unitn)
                s = s + 单个数字to中文[pre] + unit
                if n == 0: return s
            elif s and not s.endswith('零'):
                s = s + '零'
        return s + 单个数字to中文[n]
    if 10000 <= n < 10000_0000 :
        pre, n = divmod(n, 10000)
        pres = _数字到中文(pre)
        if n > 0 :
            return pres + '万' + ('零' if n < 1000 else '') + _数字到中文(n)
        return _数字到中文(pre) + '万'
    pre, n = divmod(n, 10000_0000)
    pres = _数字到中文(pre)
    if n > 0 :
        return pres + '亿' + ('零' if n < 1000_0000 else '') + _数字到中文(n)
    return _数字到中文(pre) + '亿'

def 解析数字到中文(n):
    s = _数字到中文(int(n))
    if s.startswith('一十'):
        return s[1:]
    return s

def 提取第一个中文数字为小写(s):
    digits = []
    for c in list(大写to小写(s).strip().split()[0]):
        if c.isdigit() or c in 单个中文to数字:
            digits.append(c)
    return ''.join(digits)

def 提取第一个中文为数字(s):
    return _中文到数字(提取第一个中文数字为小写(s))


assert 提取第一个中文数字为小写('  测５万十捌 试  ') == '５万十八'
assert 提取第一个中文数字为小写('  测试  ') == ''

assert 提取第一个中文为数字('  测５万十捌 试  ') == 50018
assert 提取第一个中文为数字('  测试  ') == 0



assert 解析数字到中文('  ５335') == '五千三百三十五'  #
assert 解析数字到中文(19) == '十九', 解析数字到中文(19)
assert 解析数字到中文(31) == '三十一'
assert 解析数字到中文(10000) == '一万'
assert 解析数字到中文(10) == '十'
assert 解析数字到中文(11) == '十一'
assert 解析数字到中文(111) == '一百一十一'
assert 解析数字到中文(1011) == '一千零一十一'
assert 解析数字到中文(100000) == '十万'
assert 解析数字到中文(11_0014_0000) == '十一亿零一十四万'
assert 解析数字到中文(100_0000) == '一百万'
assert 解析数字到中文(100_0000_0000) == '一百亿'
assert 解析数字到中文(100000010) == '一亿零一十', 解析数字到中文(100000010)

assert 解析中文到数字('2十1') == 21
assert 解析中文到数字('三百12') == 312
assert 解析中文到数字('2千123') == 2123
assert 解析中文到数字('2万1234') == 21234
assert 解析中文到数字('一十三') == 13
assert 解析中文到数字('十三') == 13
assert 解析中文到数字('〇零十貮') == 12
assert 解析中文到数字('') == 0
assert 解析中文到数字('23451万') == 23451*10000
assert 解析中文到数字('123412341亿') == 123412341 * 1_0000_0000
assert 解析中文到数字('13百万') == 13 * 100_0000
assert 解析中文到数字('13千万') == 13 * 1000_0000
assert 解析中文到数字('13万亿') == 13 * 10000 * 1_0000_0000
assert 解析中文到数字('两千') == 2000
assert 解析中文到数字('6百四') == 640
assert 解析中文到数字('两千八') == 2800
assert 解析中文到数字('三万九') == 39000
assert 解析中文到数字('四万五千九百零九') == 45909
assert 解析中文到数字('六万零七') == 60007
assert 解析中文到数字('35亿564万貮千4百75') == 3505642475
assert 解析中文到数字('10亿零817万5288') == 10_0000_0000 + 817_0000 + 5288
assert 解析中文到数字('壹拾万零叁仟肆佰伍拾叁') == 103453
assert 解析中文到数字('一千一十') == 1010
assert 解析中文到数字('一百十一') == 111
assert 解析中文到数字('十万零一千') == 101000
assert 解析中文到数字('一亿五千万零六千三百五十五') == 150006355
assert 解析中文到数字('一百十六') == 116
assert 解析中文到数字('一百01') == 101

assert 解析中文到数字('负一百零一') == -101
assert 解析数字到中文(-101) == '负一百零一'

# 每一个assert都要有测试用例

''' test case
解析中文到数字('123412341十') #系数太大
解析中文到数字('123412341百') #系数太大
解析中文到数字('2345千') #系数太大

解析中文到数字('2万23451千') #系数太大 在中间

解析中文到数字('三十18') #后面太大
解析中文到数字('2百13451') #后面太大
解析中文到数字('2千13451') #后面太大
解析中文到数字('2万13451') #后面太大
解析中文到数字('2亿123412341') #后面太大

解析中文到数字('四五千') # 不是一位中文数字 大于1位
解析中文到数字('测千') #不是一位中文数字 1位
解析中文到数字('测千') #系数不是一位中文数字
解析中文到数字('四五万')  #系数不是一位中文数字
'''



def test(testcount = 10, maxzeros=None, show=False):
    import random
    maxzeros = maxzeros or random.randint(1,  256)
    for i in range(testcount):
        n1 = random.randint(0, pow(10, maxzeros))
        cn = 解析数字到中文(n1)
        n2 = 解析中文到数字(cn)
        大写 = 小写to大写(cn)
        小写 = 大写to小写(大写)
        n3 = 解析中文到数字(小写)
        n4 = 解析中文到数字(大写)
        assert n1 == n2, f'Error {n1} != {cn}'
        assert 小写 == cn, f'Error {n1} != 小写 {小写}'
        assert n1 == n3, f'Error {n1} != 小写 {小写}'
        assert n1 == n4, f'Error {n1} != 大写 {大写}'
        if show: print(f'{n1} == {cn}')
    print('rand test ok', testcount, 'times, max', maxzeros, '位')
