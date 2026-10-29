#!/usr/bin/env python3
"""把未加密的 OpenSSH ed25519 私钥写成 PuTTY PPK v2。

编码按已实测、plink 可接受的规则实现：

- 公钥块 = ssh_string("ssh-ed25519") + ssh_string(32 字节公钥)
- 私钥块 = ssh_string(32 字节 seed)，只有 seed，带 4 字节长度前缀
- MAC = HMAC-SHA1
- MAC 密钥 = SHA1("putty-private-key-file-mac-key") 的二进制摘要
- MAC 数据 = ssh_string(算法名) + ssh_string("none") + ssh_string(注释)
  + ssh_string(公钥块) + ssh_string(私钥块)
- 文件头为 PuTTY-User-Key-File-2: ssh-ed25519，Encryption: none
- Public-Lines / Private-Lines 为 base64，每行 64 个字符

本脚本只把结果写入 --output 指定的文件。标准输出不打印私钥、seed、公钥或 .ppk 正文。
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import struct
import sys
import tempfile
from pathlib import Path


ALGORITHM = "ssh-ed25519"
ENCRYPTION = "none"
MAC_KEY_LABEL = b"putty-private-key-file-mac-key"
DEFAULT_COMMENT = "openssh-ed25519"


def ssh_string(value: bytes | str) -> bytes:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return struct.pack(">I", len(data)) + data


def public_blob(public_key: bytes) -> bytes:
    if len(public_key) != 32:
        raise ValueError("ed25519 公钥必须是 32 字节")
    return ssh_string(ALGORITHM) + ssh_string(public_key)


def private_blob(seed: bytes) -> bytes:
    if len(seed) != 32:
        raise ValueError("ed25519 seed 必须是 32 字节")
    return ssh_string(seed)


def mac_hex(comment: str, public_part: bytes, private_part: bytes) -> str:
    mac_key = hashlib.sha1(MAC_KEY_LABEL).digest()
    payload = b"".join(
        (
            ssh_string(ALGORITHM),
            ssh_string(ENCRYPTION),
            ssh_string(comment),
            ssh_string(public_part),
            ssh_string(private_part),
        )
    )
    return hmac.new(mac_key, payload, hashlib.sha1).hexdigest()


def base64_lines(data: bytes) -> list[str]:
    text = base64.b64encode(data).decode("ascii")
    return [text[index : index + 64] for index in range(0, len(text), 64)]


def render_ppk(comment: str, public_part: bytes, private_part: bytes) -> str:
    public_lines = base64_lines(public_part)
    private_lines = base64_lines(private_part)
    rows = [
        f"PuTTY-User-Key-File-2: {ALGORITHM}",
        f"Encryption: {ENCRYPTION}",
        f"Comment: {comment}",
        f"Public-Lines: {len(public_lines)}",
        *public_lines,
        f"Private-Lines: {len(private_lines)}",
        *private_lines,
        f"Private-MAC: {mac_hex(comment, public_part, private_part)}",
    ]
    return "\n".join(rows) + "\n"


def load_openssh_ed25519(path: Path) -> tuple[bytes, bytes]:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError as exc:
        raise SystemExit("缺少 Python 包 cryptography。安装后重试：python -m pip install cryptography") from exc

    try:
        key = serialization.load_ssh_private_key(path.read_bytes(), password=None)
    except (ValueError, TypeError) as exc:
        raise SystemExit(
            "无法读取未加密的 OpenSSH ed25519 私钥。不要把私钥内容贴进命令或对话。"
        ) from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise SystemExit("只转换 OpenSSH ed25519 私钥。")

    seed = key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return seed, public_key


def write_ppk(private_key: Path, output: Path, comment: str, force: bool) -> None:
    if "\n" in comment or "\r" in comment:
        raise SystemExit("注释不能包含换行。")
    try:
        comment.encode("ascii")
    except UnicodeEncodeError:
        raise SystemExit("注释只接受单行 ASCII。") from None
    if output.exists() and not force:
        raise SystemExit(f"输出文件已存在：{output}。换一个路径，或加上 --force。")
    seed, public_key = load_openssh_ed25519(private_key)
    output.write_text(render_ppk(comment, public_blob(public_key), private_blob(seed)), encoding="ascii", newline="\n")


def _parse_ppk(text: str) -> tuple[str, bytes, bytes, str]:
    lines = text.splitlines()
    if len(lines) < 7 or lines[0] != f"PuTTY-User-Key-File-2: {ALGORITHM}" or lines[1] != f"Encryption: {ENCRYPTION}":
        raise AssertionError("PPK 文件头不符合 v2 ed25519")
    if not lines[2].startswith("Comment: "):
        raise AssertionError("缺少 Comment")
    comment = lines[2].removeprefix("Comment: ")
    if not lines[3].startswith("Public-Lines: "):
        raise AssertionError("缺少 Public-Lines")
    public_count = int(lines[3].split(": ", 1)[1])
    public_b64 = "".join(lines[4 : 4 + public_count])
    private_header = 4 + public_count
    if not lines[private_header].startswith("Private-Lines: "):
        raise AssertionError("缺少 Private-Lines")
    private_count = int(lines[private_header].split(": ", 1)[1])
    private_start = private_header + 1
    private_b64 = "".join(lines[private_start : private_start + private_count])
    mac_line = lines[private_start + private_count]
    if not mac_line.startswith("Private-MAC: "):
        raise AssertionError("缺少 Private-MAC")
    return comment, base64.b64decode(public_b64), base64.b64decode(private_b64), mac_line.split(": ", 1)[1]


def self_test() -> None:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError as exc:
        raise SystemExit("缺少 Python 包 cryptography。安装后重试：python -m pip install cryptography") from exc

    key = Ed25519PrivateKey.generate()
    seed = key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with tempfile.TemporaryDirectory(prefix="ppk-self-test-") as directory:
        root = Path(directory)
        private_key = root / "ephemeral"
        output = root / "ephemeral.ppk"
        private_key.write_bytes(pem)
        write_ppk(private_key, output, DEFAULT_COMMENT, force=False)
        text = output.read_text(encoding="ascii")
        comment, parsed_public, parsed_private, parsed_mac = _parse_ppk(text)
        expected_public = public_blob(public_key)
        expected_private = private_blob(seed)
        if comment != DEFAULT_COMMENT:
            raise SystemExit("self-test 失败：注释不一致")
        if parsed_public != expected_public or parsed_private != expected_private:
            raise SystemExit("self-test 失败：公钥块或私钥块编码不一致")
        if parsed_private != ssh_string(seed):
            raise SystemExit("self-test 失败：私钥块不是 ssh_string(seed)")
        if parsed_mac != mac_hex(comment, expected_public, expected_private):
            raise SystemExit("self-test 失败：MAC 不一致")
        if seed.hex() in text or public_key.hex() in text:
            raise SystemExit("self-test 失败：PPK 正文以十六进制露出了原始密钥")
        stdout_sample = "self-test passed"
        if seed.hex() in stdout_sample or public_key.hex() in stdout_sample:
            raise SystemExit("self-test 失败：输出包含密钥")
    print("self-test passed")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把未加密的 OpenSSH ed25519 私钥写成 PuTTY PPK v2")
    parser.add_argument("--self-test", action="store_true", help="用临时密钥检查编码和 MAC，不保留文件")
    parser.add_argument("--private-key", type=Path, help="OpenSSH ed25519 私钥路径")
    parser.add_argument("--output", type=Path, help="输出的 .ppk 路径")
    parser.add_argument("--comment", default=DEFAULT_COMMENT, help=f"写入 PPK 的注释，默认 {DEFAULT_COMMENT}")
    parser.add_argument("--force", action="store_true", help="输出文件已存在时覆盖")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.self_test:
            self_test()
            return 0
        if args.private_key is None or args.output is None:
            raise SystemExit("转换时必须同时提供 --private-key 和 --output。")
        write_ppk(args.private_key, args.output, args.comment, args.force)
    except SystemExit as exc:
        if exc.code not in (None, 0):
            print(exc.code if isinstance(exc.code, str) else "转换失败", file=sys.stderr)
            return 1
        raise
    print(f"已写入 {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
