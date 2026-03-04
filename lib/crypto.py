"""Git-based CTF v2.0 — GPG encryption/decryption.

Exploits are encrypted with PGP before submission as GitHub Issues.
This ensures only the target team and instructor can read them.
"""

from __future__ import annotations

import os
import shutil

from lib.utils import random_string, rmdir, rmfile, run_command


def encrypt_exploit(exploit_dir: str, target_team: str, config: dict,
                    signer: str | None = None) -> str | None:
    exploit_dir = exploit_dir.rstrip("/")
    out_file = exploit_dir + ".zip.pgp"

    teams = config["teams"]
    instructor_pubkey = teams["instructor"]["pub_key_id"]
    target_pubkey = teams[target_team]["pub_key_id"]

    tmp_path = f"/tmp/gitctf_{random_string(6)}"
    shutil.make_archive(tmp_path, "zip", exploit_dir)
    zip_file = tmp_path + ".zip"

    encrypt_cmd = f"gpg -o {out_file} "
    if signer is not None:
        signer_pubkey = config["individual"][signer]["pub_key_id"]
        encrypt_cmd += f"--default-key {signer_pubkey} --sign "
    encrypt_cmd += f"-e -r {instructor_pubkey} -r {target_pubkey} "
    encrypt_cmd += f"--armor {zip_file}"

    _, err, ret = run_command(encrypt_cmd, None)
    rmfile(zip_file)

    if ret != 0:
        print(f"[!] Failed to sign/encrypt: {err}")
        return None
    return out_file


def decrypt_exploit(encrypted_path: str, config: dict, team: str,
                    out_dir: str | None = None,
                    expected_signer: str | None = None) -> str | None:
    if out_dir is None:
        out_dir = "exploit"
    rmdir(out_dir)

    tmpzip = f"/tmp/gitctf_{random_string(6)}.zip"
    tmpdir = f"/tmp/gitctf_{random_string(6)}"
    tmpgpg = f"/tmp/gitctf_{random_string(6)}.gpg"

    if expected_signer is None:
        decrypt_cmd = f"gpg -o {tmpzip} {encrypted_path}"
    else:
        instructor_id = config["teams"]["instructor"]["pub_key_id"]
        team_id = config["teams"][team]["pub_key_id"]
        signer_id = config["individual"][expected_signer]["pub_key_id"]

        run_command(
            f"gpg -o {tmpgpg} --export {signer_id} {instructor_id} {team_id}",
            os.getcwd(),
        )
        decrypt_cmd = (
            f"gpg --no-default-keyring --keyring {tmpgpg} "
            f"-o {tmpzip} {encrypted_path}"
        )

    _, err, ret = run_command(decrypt_cmd, os.getcwd())
    if ret != 0:
        print(f"[!] Failed to decrypt/verify: {err}")
        return None

    run_command(f"unzip {tmpzip} -d {tmpdir}", os.getcwd())
    shutil.move(tmpdir, out_dir)

    rmfile(tmpzip)
    rmfile(tmpgpg)
    rmdir(tmpdir)
    return out_dir
