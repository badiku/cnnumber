-- 参考 中华人民共和国国家标准-出版物上数字用法的规定
-- lua，支持最大18位整数互转

local 中文小写s = '一 二 三 四 五 六 七 八 九 十 百 千 '
local 中文大写s = '壹 贰 叁 肆 伍 陆 柒 捌 玖 拾 佰 仟 '
local 中文小写 = {}
local 中文大写 = {}
for c in 中文小写s:gmatch('(.-) ') do 中文小写[#中文小写 + 1] = c end
for c in 中文大写s:gmatch('(.-) ') do 中文大写[#中文大写 + 1] = c end
local 中文小写to大写 = {}
local 中文大写to小写 = {}
for i, c in ipairs(中文小写) do 中文小写to大写[c] = 中文大写[i] end
for i, c in ipairs(中文大写) do 中文大写to小写[c] = 中文小写[i] end


local 中文to数字 = {}
for i, c in ipairs(中文小写) do if i < 10 then 中文to数字[c] = i end end
local 数字to中文 = {}
for i, c in ipairs(中文小写) do if i < 10 then 数字to中文[i] = c end end

中文to数字['十'] = 10
中文to数字['百'] = 100
中文to数字['千'] = 1000
中文to数字['万'] = 10000
中文to数字['亿'] = 10000*10000

local 全角数字 = '０ １ ２ ３ ４ ５ ６ ７ ８ ９ '
for i,c in 全角数字:gmatch('()(.-) ') do 中文大写to小写[c] = tostring(i//4) end

local function 大写to小写(s)
  local chars = {}
  for c in s:gmatch(utf8.charpattern) do
    chars[#chars+1] = 中文大写to小写[c] or c
  end
  return table.concat(chars)
end

assert(大写to小写('a５七捌') == 'a5七八')

local function 小写to大写(s)
  local chars = {}
  for c in s:gmatch(utf8.charpattern) do
    chars[#chars+1] = 中文小写to大写[c] or c
  end
  return table.concat(chars)
end

assert(小写to大写('七捌b') == '柒捌b')


local function rsplit(s, sep)
  local a,b = s:find('.*'..sep)
  if b then return {s:sub(1, b - #sep), s:sub(b+1)} end
  return {s}
end

assert(rsplit('五万亿二十三万八千四', '万')[1] == '五万亿二十三')
assert(rsplit('五万亿二十三万八千四', '万')[2] == '八千四')

local function len(s)
  local a,c = s:gsub(utf8.charpattern,'')
  if #a > 0 then error('invalid utf8 string') end
  return c
end

assert(len('abc测试') == 5 )



local function 解析一位中文数字(s, unit)
    if not s:find(unit) then return 0 end
    local n = 1
    local unitn = 中文to数字[unit]
    s = rsplit(s, unit)[1]
    if tonumber(s) then
        n = math.floor(tonumber(s))
        assert(n < unitn, unit..'这一位的系数最多'..unitn..':  '..s..unit)
    else
       if len(s) > 1 then
         error('这一部分系数不是一位中文数字:'..s..unit) end
       if len(s) == 1 then
         assert(中文to数字[s], '这一部分系数不是一位中文数字: '..s..unit)
         n = 中文to数字[s] end
    end
    return n * unitn
end

assert(解析一位中文数字('8万3', '万') == 80000)
assert(解析一位中文数字('九万3', '万') == 90000)


local function 解析中文到数字(s)
  -- 亿万单独解析，后面的依次从高到低解析各位数字
    if tonumber(s) then
        return math.floor(tonumber(s)) end
    s = 大写to小写(s):gsub('零', ''):gsub('〇', ''):gsub('貮', '二')
    local n = 0
    local unitn = 0
    for i,unit in ipairs({'亿', '万'}) do
        if s:find(unit) then
           unitn = 中文to数字[unit]
           local pre, s = table.unpack(rsplit(s,unit))
           local pren = 解析中文到数字(pre)
           if (unit == '万') and (s:find'亿') then
               assert(pren < unitn, unit..'这一位的系数最多'..unitn..': '..pre..unit) end
           n = 解析中文到数字(s)
           assert(n < unitn, unit..'这一位后面最多'..unitn..': '..s)
           return pren * unitn + n
        end
    end

    local units = {'千', '百', '十'}
    for i,unit in ipairs(units) do
        if s:find(unit) then
           unitn = 中文to数字[unit]
           n = n + 解析一位中文数字(s, unit)
           s = rsplit(s, unit)[2]
        end
    end
    if tonumber(s) then
        local lastn = math.floor(tonumber(s))
        assert(lastn < unitn, '最后的数字最多'..unitn..': '..lastn)
        n = n + lastn
    elseif #s > 0 then
        assert(中文to数字[s],  '这一部分不是一位中文数字: '..s)
        n = n + 中文to数字[s]
    end
    return n
end

assert(解析中文到数字('35亿564万貮千4百75') == 3505642475)



local function endswith(s, c)
   local a,b = s:find('.*'..c)
   if b and (b == #s) then return true end
end

assert(endswith('ab零cd零','零'))

local function 数字到中文(n)
    -- 亿万单独处理，后面的依次从高到低解析各位数字
    local s = ''
    for i, unit in ipairs({'亿', '万'}) do
        local unitn = 中文to数字[unit]
        if n >= unitn then
            local pre
            pre, n =  (n // unitn), (n % unitn)
            return 数字到中文(pre) ..unit.. 数字到中文(n)
            end
    end
    local units = {'千', '百', '十'}
    for i,unit in ipairs(units) do
        local unitn = 中文to数字[unit]
        if n < unitn then
           if not endswith(s, '零') then
             s = s .. '零' end
        else
            local c
            c, n = (n // unitn), (n % unitn)
            s = s .. 数字to中文[c] .. unit
         end
    end
    if n > 0 then
        s = s .. 数字to中文[n] end
    return s
end

assert(数字到中文(123) == '零一百二十三')

local function strip(s, c)
  local a,b = s:find(c)
  if a==1 then
    s = s:sub(b+1)
  end
  if endswith(s,c) then
   return s:sub(1, #s - #c)
  end
  return s
end

assert(strip('c零abc零','零') == 'c零abc')
assert(strip('零abc零','零') == 'abc')

local function 解析数字到中文(n)
    if type(n)=='string' then
      n = 大写to小写(n)
      if not tonumber(n) then
         error('不是数字  '..n)
         end end
    n = math.floor(tonumber(n))
    local s = 数字到中文(n)
    if len(s) > 1 then
        s = strip(s, '零')
        end
    return s:gsub('一十', '十')
end

assert(解析数字到中文('123') == '一百二十三')


local function 提取第一个中文数字(s)
    local digits = {}
    for c in 大写to小写(s):gmatch(utf8.charpattern) do
        if tonumber(c) or 中文to数字[c] then
            digits[#digits+1] = c end end
    return table.concat(digits)
end


local function 提取第一个中文为数字(s)
    return 解析中文到数字(提取第一个中文数字(s))
end

assert(提取第一个中文数字('测５万十捌 试') == '5万十八')
assert(提取第一个中文数字('测试') == '')

assert(提取第一个中文为数字('测５万十捌 试') == 50018)
assert(提取第一个中文为数字('测试') == 0)

assert(解析中文到数字('35亿564万貮千4百75') == 3505642475)
assert(解析中文到数字('2十1') == 21)
assert(解析中文到数字('三百12') == 312)
assert(解析中文到数字('2千123') == 2123)
assert(解析中文到数字('2万1234') == 21234)
assert(解析中文到数字('一十三') == 13)
assert(解析中文到数字('十三') == 13)
assert(解析中文到数字('〇零十貮') == 12)
assert(解析中文到数字('') == 0)

assert(解析数字到中文('  ５335') == '五千三百三十五')
assert(解析数字到中文(19) == '十九')
assert(解析数字到中文(31) == '三十一')
assert(解析数字到中文(10000) == '一万')
assert(解析数字到中文(10) == '十')
assert(解析数字到中文(100000) == '十万')
assert(解析数字到中文(1100140000) == '十一亿零十四万')

-- 每一个assert都要有测试用例

--[[ test case
解析中文到数字('123412341十') -- 系数太大
解析中文到数字('123412341百') -- 系数太大
解析中文到数字('2345千') -- 系数太大
解析中文到数字('23451万') -- 系数太大?可以
解析中文到数字('123412341亿') -- 系数太大?可以

解析中文到数字('2万23451千') -- 系数太大 在中间

解析中文到数字('三十18') -- 后面太大
解析中文到数字('2百13451') -- 后面太大
解析中文到数字('2千13451') -- 后面太大
解析中文到数字('2万13451') -- 后面太大
解析中文到数字('2亿123412341') -- 后面太大



解析中文到数字('四五千') --  不是一位中文数字 大于1位
解析中文到数字('测千') -- 不是一位中文数字 1位
解析中文到数字('四五万')  -- 系数不是一位中文数字
]]

local function test(testcount, maxzeros)
    testcount = testcount or 10
    local random = math.random
    maxzeros = maxzeros or random(1,  18)
    local maxn = math.floor(10^maxzeros)
    for i = 1,testcount do
        local n1 = random(0, maxn)
        local cn = 解析数字到中文(n1)
        local n2 = 解析中文到数字(cn)
        local 大写 = 小写to大写(cn)
        local 小写 = 大写to小写(大写)
        local n3 = 解析中文到数字(小写)
        local n4 = 解析中文到数字(大写)
        assert( n1 == n2, 'Error '.. n1)
        assert( 小写 == cn, 'Error '.. n1)
        assert( n1 == n3, 'Error '.. n1)
        assert( n1 == n4, 'Error '.. n1)
        if i <= 10 then
            print(n1, '==',cn) end end
    print('rand test ok', testcount, 'times, max', maxzeros, '位')
end

return {
   解析中文到数字 = 解析中文到数字,
   解析数字到中文 = 解析数字到中文,
   提取第一个中文为数字 = 提取第一个中文为数字,
   大写to小写 = 大写to小写,
   小写to大写 = 小写to大写,
   test = test,
   }
