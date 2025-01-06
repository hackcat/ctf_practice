from cryptography.hazmat.primitives import serialization
import subprocess
import tempfile
import os
from pwn import *

def load_public_key(public_key_pem):
    # 加载公钥
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    return public_key

def get_modulus(public_key):
    # 提取模数n
    numbers = public_key.public_numbers()
    n = numbers.n
    return n

def parse_yafu_output(output_text):
    # 从输出中提取两个 P33 值
    p = None
    q = None
    for line in output_text.split('\n'):
        if line.startswith('P3'):
            if p is None:
                p = int(line.split('=')[1].strip())
            else:
                q = int(line.split('=')[1].strip())
    return p, q

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
                factors_output = f.read()
            print("分解结果：")
            print(factors_output)
            
            # 解析结果获取 p 和 q
            p, q = parse_yafu_output(factors_output)
            print(f"p = {p}")
            print(f"q = {q}")
            return p, q
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
    io = remote('94.237.62.184', 35529)

    for _ in range(5):
        io.recvuntil('-----BEGIN PUBLIC KEY-----')
        key_data = io.recvuntil('-----END PUBLIC KEY-----').decode()
        # 构造完整的 PEM 格式公钥
        public_key_pem = "-----BEGIN PUBLIC KEY-----\n" + key_data.strip() + "\n-----END PUBLIC KEY-----"

        public_key = load_public_key(public_key_pem)
        n = get_modulus(public_key)
        print("模数n:")
        print(n)
        p, q = factorize_n_with_yafu(n)
        if p and q:
            print("成功获取两个质因数：")
            print(f"p = {p}")
            print(f"q = {q}")
        
        io.sendlineafter('bpumpkin = ',str(p).encode())
        io.sendlineafter('bpumpkin = ',str(q).encode())
        io.recvline()
