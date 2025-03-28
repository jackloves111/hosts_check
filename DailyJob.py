# 调用http://www.ip33.com/的接口解析域名，避免dns污染
import datetime
import json
import platform
import requests
from ping3 import ping

# dns解析用到的api
api = "http://api.ip33.com/dns/resolver"

# 待解析的域名
hosts = ["api.themoviedb.org", "image.tmdb.org", "www.themoviedb.org"]

# dns服务商
dnsProvider = ["156.154.70.1", "208.67.222.222"]



# 批量ping
def pingBatch(ips):
    if ips is not None and type(ips) == list:
        for ip in ips:
            result = pingIp(ip)
            if not result:
                ips.remove(ip)


# ping ip返回ip是否连通
# def pingIp(ip) -> bool:
#     result = ping(ip)
#     if result is not None:
#         print(f"[√] IP:{ip}  可以ping通，延迟为{result}毫秒")
#         return True
#     else:
#         print(f"[×] IP:{ip}  无法ping通")
#         return False
        
# 替换原来的 pingIp 函数
def pingIp(ip):
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

# 返回host对饮domain的解析结果列表
def analysis(domain, dns) -> list:
    params = {
        "domain": domain,
        "type": "A",
        "dns": dns
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60"

    }
    try:
        response = requests.post(url=api, data=params, headers=headers)
        html = response.text
        ipDics = json.loads(html)["record"]
        ips = []
        for dic in ipDics:
            ips.append(dic["ip"])
        return ips
    except Exception as e:
        print("解析dns出错：")
        print(e)


# 写入host信息  
def hostWritor(hostDic):  
    origin = ""  
    origin += "###start###\n"  
    for eachHost in hostDic:  
        ips_set = set(hostDic[eachHost])  # 使用集合去重  
        for eachIp in ips_set:  
            # 明确使用英文字符的空格 ' '  
            origin += f"{eachIp} {eachHost}\n"  # 这里使用了英文字符的空格  
    origin += f"###最后更新时间:{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}###\n"  
    origin += "###end###\n"  
    with open("hosts.txt", "w", encoding="utf-8") as f:  # 修改文件路径  
        f.write(origin)


if __name__ == '__main__':
    resultDic = {}
    for host in hosts:
        for dns in dnsProvider:
            records = analysis(host, dns)
            pingBatch(records)
            if records is not None and len(records) > 0:
                if host not in resultDic:
                    resultDic[host] = records
                else:
                    resultDic[host] += records
    hostWritor(resultDic)
