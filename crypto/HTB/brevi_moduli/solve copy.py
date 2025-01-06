from cryptography.hazmat.primitives import serialization
import subprocess
import tempfile
import os
from pwn import *


def load_public_key():
    public_key_str = """
    -----BEGIN PUBLIC KEY-----
    MDcwDQYJKoZIhvcNAQEBBQADJgAwIwIcB71iCdkFORZF7shdGfJ8zM9yCDUApt0v
    MvLUfQIDAQAB
    -----END PUBLIC KEY-----
    """
    # 加载公钥
    public_key = serialization.load_pem_public_key(public_key_str.encode())
    return public_key

def get_modulus(public_key):
    # 提取模数n
    numbers = public_key.public_numbers()
    n = numbers.n
    return n

def factorize_n_with_yafu(n):
    # 将n写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_input:
        temp_input.write(str(n))
        temp_input_path = temp_input.name

    # 定义输出文件路径
    temp_output_path = temp_input_path + '_factors.txt'

    try:
        # 调用 yafu-64.exe 分解n
        # 假设 yafu-64.exe 接受输入文件并输出结果到输出文件
        yafu_command = [
            'yafu-64.exe',
            f'factor({n})',
            f'> {temp_output_path}'
        ]
        # 使用 shell=True 以便正确解析重定向符号
        subprocess.run(' '.join(yafu_command), shell=True, check=True)

        # 读取分解结果
        if os.path.exists(temp_output_path):
            with open(temp_output_path, 'r') as f:
                factors = f.read()
            print("分解结果：")
            print(factors)
        else:
            print("分解结果文件未找到。")
    except subprocess.CalledProcessError as e:
        print("调用 yafu-64.exe 时发生错误：", e)
    finally:
        # 清理临时文件
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if os.path.exists(temp_output_path):
            os.remove(temp_output_path)

if __name__ == "__main__":
    public_key = load_public_key()
    n = get_modulus(public_key)
    print("模数n:")
    print(n)
    factorize_n_with_yafu(n)
