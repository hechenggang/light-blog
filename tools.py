#coding:utf-8
import re
import time
import hashlib


def to_integer(raw=None, max=None, default=0):
    '''
    将输入转换为整数
    参数：
        raw String/Integer 输入
        max Integer 最大值
        default Integer 默认值/失败后的输出
    输出：
        Integer

    '''
    # 检验输入
    if not raw:
        return 0
    else:
        pass

    # 判断输入是否整数
    if not isinstance(raw,int):
        try:
            # 如果输入不是整数，尝试转换
            raw = int(raw)
        except:
            # 如果转换失败，返回默认值
            return default
    else:
        pass

    # 如果存在最大值限制，则进一步判断
    if bool(max):
        # 判断输入是否达到上限
        if raw < max:
            return raw
        # 若达到上限，则返回上限
        else:
            return max
    else:
        return raw


def is_mail_address(raw=None,max_length=50):
    '''
    校验邮件地址是否正确
    参数：
        raw String/Integer 输入
        max_length Integer 最大长度
    输出：
        Bool

    '''

    # 检验输入
    if not raw:
        return False
    else:
        pass

    # 使用正则表达式匹配"aaa@bbb.ccc"的字符串
    r = re.compile(r'\w+@\w+\.\w+')
    if not bool(r.search(raw)):
        return False
    else:
        return True


def timestamp(length=13):
    '''
    获取当前时间戳
    参数：
        length Integer 长度
    输出：
        Integer

    '''
    t = str(time.time()).replace('.','')[:length]
    while len(t) < length:
        t += '0'
    return int(t)


def string_time(ts=None,style=1):
    '''
    时间戳转换为可读时间
    参数：
        timestamp Integer 13位时间戳
        style Integer 可读时间的样式
            1 xxxx年xx月xx日
            2 xxxx-xx-xx xx:xx:xx
    输出：
        Integer

    '''

    if not ts:
        ts = timestamp()
    if style == 1:
        strTime = time.strftime('%Y-%m-%d',time.localtime(int(str(ts)[:10]))).split('-')
        return '{}年{}月{}日'.format(strTime[0],strTime[1],strTime[2])
    elif style == 2:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(str(ts)[:10])))


def to_md5(raw=None, mix_text=None):
    '''传入一个字符串，转换字符串为 md5'''
    '''
    将输入转换为 md5
    参数：
        raw String 原始字符串
        mix_text String 混入字符串
            
    输出：
        None
        String

    '''
    if not raw:
        raw = timestamp()
    else:
        pass

    string = str(raw)

    if bool(mix_text):
        string = mix_text + string
    else:
        pass

    return hashlib.md5(string.encode(encoding="UTF-8")).hexdigest()


class kv_cache(object):
    '''基于内存的键值对缓存'''

    def __init__(self, pool_name="01", default_timeout=3600):
        '''初始化内存，建立入口,结构如下：
        cache {
            "pool_name":{
                "key":{
                    "value":value,
                    "timestamp":timestamp
                }
            }
        }
        config {
            "pool_name":{
               "default_timeout":default_timeout
            }
        }

        参数：
            pool_name String 缓存池名称
            default_timeout Integer 默认过期间隔
                
        输出：
            None
        '''
        # 建立缓存
        self.cache = {}
        # 设置默认储存池
        self.default_pool = pool_name
        # 将默认储存池添加到内存
        self.cache[self.default_pool] = {}
        # 建立储存池列表
        self.pool_list = []
        # 将默认储存池添加到储存池列表
        self.pool_list.append(self.default_pool)
        
        # 建立配置,精确到缓存池级
        self.config = {}
        # 添加配置到默认储存池
        self.config[self.default_pool] = {
            "default_timeout":default_timeout
        }


    def add_pool(self, pool_name=None, default_timeout=3600):
        '''实例初始化后，新建缓存池
        参数：
            pool_name String 缓存池名称
            default_timeout Integer 默认过期间隔
                
        输出：
            {"code":401,"errmsg":"该缓存池已存在"}
            {"code":200}
            
        '''
        if pool_name in self.CACHE:
            return {"code":401,"errmsg":"该缓存池已存在"}
        else:
            self.cache[pool_name] = {}
            self.pool_list.append(pool_name)
            self.config[pool_name] = {
                "default_timeout":default_timeout
            }
            return {"code":200}


    def get(self, pool_name=None, key=None):
        '''从缓存池获取数据
        参数：
            pool_name String 缓存池名称
            key String 键名
                
        输出：
            {"code":404,"errmsg":"无法在缓存池[{}]找到键[{}]"}
            {"code":200,"value":value}
            
        '''
        # 未传入储存池名称时,使用默认储存池
        if not bool(pool_name):
            pool_name = self.default_pool
        else:
            pass

        # 判断键是否存在
        if pool_name in self.cache:
            if key in self.cache[pool_name]:
                # 判断键是否过期
                if (timestamp() - self.cache[pool_name][key]["timestamp"])/1000 > self.config[pool_name]["default_timeout"]:
                    # 移除缓存
                    del self.cache[pool_name][key]
                    return {"code":404,"errmsg":"该缓存已过期"}
                else:
                    return {"code":200,"value":self.cache[pool_name][key]["value"],"timestamp":self.cache[pool_name][key]["timestamp"]}
            else:
                return {"code":404,"errmsg":"无法在缓存池[{}]找到键[{}]".format(pool_name,key)}
        else:
            return {"code":404,"errmsg":"不存在的缓存池"}
    

    def put(self, pool_name=None, key=None, value=None):
        '''写入缓存(会覆盖)
        参数：
            pool_name String 缓存池名称
            key String 键名
            value String/Integer/List/Dict 值
                
        输出：
            {"code":404,"errmsg":"不存在的缓存池"}
            {"code":200}
            
        '''
        # 未传入储存池名称时,使用默认储存池
        if not bool(pool_name):
            pool_name = self.default_pool
        else:
            pass

        if pool_name in self.cache:
            self.cache[pool_name][key] = {
                "value":value,
                "timestamp":timestamp()
            }
            return {"code":200}
            
        else:
            return {"code":404,"errmsg":"不存在的缓存池"}

    def delete(self, pool_name=None, key=None):
        '''删除缓存
        参数：
            pool_name String 缓存池名称
            key String 键名
                
        输出：
            
            
        '''
        # 未传入储存池名称时,使用默认储存池
        if not bool(pool_name):
            pool_name = self.default_pool
        else:
            pass

        if pool_name in self.cache:
            if key in self.cache[pool_name]:
                del self.cache[pool_name][key]
                return {"code":200}
            else:
                return {"code":404,"errmsg":"不存在的键"}
            
        else:
            return {"code":404,"errmsg":"不存在的缓存池"}

