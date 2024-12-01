# 参考 中华人民共和国国家标准-出版物上数字用法的规定

中文小写 = '一二三四五六七八九十百千'
中文大写 = '壹贰叁肆伍陆柒捌玖拾佰仟'
中文大写to小写 = dict((u, 中文小写[i]) for i,u in enumerate(中文大写))
中文小写to大写 = dict((u, 中文大写[i]) for i,u in enumerate(中文小写))


中文小写数字 = list(enumerate( '一二三四五六七八九十', start=1))
中文to数字 = dict((c,n) for n,c in 中文小写数字)    
中文to数字['百'] = 100
中文to数字['千'] = 1000
中文to数字['万'] = 10000
中文to数字['亿'] = 10000*10000

数字to中文 = dict((n,c) for c,n in 中文to数字.items()) 


def 大写to小写(s):
    return ''.join((中文大写to小写[c] if c in 中文大写 else c)  for c in list(s))


def 小写to大写(s):
    return ''.join((中文小写to大写[c] if c in 中文小写 else c)  for c in list(s))


def 解析一位中文数字(s, unit):    
    if unit not in s: return 0
    n = 1
    unitn = 中文to数字[unit]
    s = s.rsplit(unit, 1)[0]
    if s.isdigit():
        n = int(s)
        assert n < unitn, f'{unit}这一位的系数最多{unitn}: {s}{unit}'    
    else:
        if len(s) > 1:
            assert False, f'这一部分系数1不是一位中文数字: {s}{unit}'    
        if len(s) == 1:
            assert s in 中文to数字, f'这一部分系数2不是一位中文数字: {s}{unit}'
            n = 中文to数字[s]   
    return n * unitn


def 解析中文到数字(s):
    # 亿万单独解析，后面的依次从高到低解析各位数字
    if s.isdigit():
        return int(s)
    s = 大写to小写(s).replace('零', '').replace('〇', '').replace('貮', '二')
    n = 0
    unitn = 0
    for unit in list('亿万'):
        if unit not in s: continue
        unitn = 中文to数字[unit]
        pre, s = s.rsplit(unit, 1)
        pren = 解析中文到数字(pre)
        if (unit == '万') and ('亿' in s):
            assert pren < unitn, f'{unit}这一位的系数最多{unitn}: {pre}{unit}' 
        n = 解析中文到数字(s)
        assert n < unitn, f'{unit}这一位后面最多{unitn}: {s}'  
        return pren * unitn   +  解析中文到数字(s)

    units = list('千百十')
    for unit in units:
        if unit not in s: continue
        unitn = 中文to数字[unit]
        n = n + 解析一位中文数字(s, unit)
        s = s.rsplit(unit, 1)[-1]
    if s.isdigit():
        lastn = int(s)
        assert lastn < unitn, f'最后的数字最多{unitn}: {lastn}' 
        n = n + int(s)
    elif s:
        assert (s in 中文to数字),  f'这一部分不是一位中文数字: {s}'
        n = n + 中文to数字[s]
    return n

def 数字到中文(n):
    # 亿万单独处理，后面的依次从高到低解析各位数字
    s = ''
    for unit in list('亿万'):
        test = 中文to数字[unit]
        if n >= test:
            pre, n = divmod(n, test)
            return 数字到中文(pre) + unit + 数字到中文(n)
    units = list('千百十')
    for unit in units:
        test = 中文to数字[unit]
        if n < test:
             if not s.endswith('零'):
                    s = s + '零'
        else:
            c, n = divmod(n, test)
            s = s + 数字to中文[c] + unit
    if n > 0: 
        s = s + 数字to中文[n]
    return s

def 解析数字到中文(n):
    n = int(n)
    s = 数字到中文(n)
    if len(s) > 1 :
        s = s.strip('零')
    return s.replace('一十', '十')

def 提取第一个中文数字(s):
    digits = []
    for c in list(大写to小写(s).strip().split()[0]):
        if c.isdigit() or c in 中文to数字:
            digits.append(c)
    return ''.join(digits) 

def 提取第一个中文为数字(s):
    return 解析中文到数字(提取第一个中文数字(s))


assert 提取第一个中文数字('  测５万十捌 试  ') == '５万十八'
assert 提取第一个中文数字('  测试  ') == ''

assert 提取第一个中文为数字('  测５万十捌 试  ') == 50018
assert 提取第一个中文为数字('  测试  ') == 0


assert 解析中文到数字('35亿564万貮千4百75') == 3505642475
assert 解析数字到中文('  ５335') == '五千三百三十五'
assert 解析数字到中文(19) == '十九'
assert 解析数字到中文(31) == '三十一'
assert 解析中文到数字('2十1') == 21
assert 解析中文到数字('三百12') == 312
assert 解析中文到数字('2千123') == 2123
assert 解析中文到数字('2万1234') == 21234
assert 解析中文到数字('一十三') == 13
assert 解析中文到数字('十三') == 13
assert 解析中文到数字('〇零十貮') == 12
assert 解析中文到数字('') == 0
assert 解析数字到中文(10000) == '一万'
assert 解析数字到中文(10) == '十'
assert 解析数字到中文(100000) == '十万'
assert 解析数字到中文(1100140000) == '十一亿零十四万'
# 每一个assert都要有测试用例

''' test case
解析中文到数字('123412341十') #系数太大
解析中文到数字('123412341百') #系数太大
解析中文到数字('2345千') #系数太大
解析中文到数字('23451万') #系数太大
解析中文到数字('123412341亿') #系数太大

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

def test(testcount = 10, maxzeros=None):
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
        if i <= 10:
            print(n1, '==',cn)
    print('rand test ok', testcount, 'times, max', maxzeros, '位')
