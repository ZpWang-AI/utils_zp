
from utils_zp import *

import alibabacloud_oss_v2 as oss
'''
https://help.aliyun.com/zh/oss/user-guide/simple-upload?spm=a2c4g.11186623.help-menu-31815.d_0_3_1_0.1632311dpHzVwy&scm=20140722.H_31848._.OR_help-T_cn~zh-V_1#dcc5cf606csij
'''

def main():
    """
    Python SDK V2 客户端初始化配置说明：

    1. 签名版本：Python SDK V2 默认使用 V4 签名，提供更高的安全性
    2. Region配置：初始化 Client 时，必须指定阿里云 Region ID 作为请求地域标识，例如华东1（杭州）Region ID：cn-hangzhou
    3. Endpoint配置：
       - 可通过Endpoint参数自定义服务请求的访问域名
       - 当不指定 Endpoint 时，将根据 Region 自动构造公网访问域名，例如Region为cn-hangzhou时，构造访问域名为：https://oss-cn-hangzhou.aliyuncs.com
    4. 协议配置：
       - SDK 默认使用 HTTPS 协议构造访问域名
       - 如需使用 HTTP 协议，在指定域名时明确指定：http://oss-cn-hangzhou.aliyuncs.com
    """
   

    # 从环境变量中加载凭证信息，用于身份验证
    """
echo "export OSS_ACCESS_KEY_ID='xxx'" >> ~/.bashrc
echo "export OSS_ACCESS_KEY_SECRET='xxx'" >> ~/.bashrc
cat ~/.bashrc
    """
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

    # 加载SDK的默认配置，并设置凭证提供者
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider

    # 方式一：只填写Region（推荐）
    # 必须指定Region ID，以华东1（杭州）为例，Region填写为cn-hangzhou，SDK会根据Region自动构造HTTPS访问域名
    # cfg.region = 'cn-hangzhou' 
    cfg.region = 'cn-beijing'

    # # 方式二：同时填写Region和Endpoint
    # # 必须指定Region ID，以华东1（杭州）为例，Region填写为cn-hangzhou
    # cfg.region = 'cn-hangzhou'
    # # 填写Bucket所在地域对应的公网Endpoint。以华东1（杭州）为例，Endpoint填写为'https://oss-cn-hangzhou.aliyuncs.com'
    # cfg.endpoint = 'https://oss-cn-hangzhou.aliyuncs.com'

    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    # 定义要上传的字符串内容
    text_string = "Hello, OSS!"
    data = text_string.encode('utf-8')  # 将字符串编码为UTF-8字节串

    # 执行上传对象的请求，指定存储空间名称、对象名称和数据内容
    result = client.put_object(oss.PutObjectRequest(
        bucket="oss-pai-100cyf682fo257ine4-cn-beijing",
        key="Your Object Key",
        body=data,
    ))

    # 输出请求的结果状态码、请求ID、ETag，用于检查请求是否成功
    print(f'status code: {result.status_code}\n'
          f'request id: {result.request_id}\n'
          f'etag: {result.etag}'
    )

# 当此脚本被直接运行时，调用main函数
if __name__ == "__main__":
    main()  # 脚本入口，当文件被直接运行时调用main函数