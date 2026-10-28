#!/usr/bin/env python3
"""systems-journey 공통 테스트 러너: '입력 파일 → 기대 출력 파일' 비교.

테스트 디렉터리 안의 파일 규칙
    이름.in    입력 (필수)
    이름.out   기대 stdout (필수)
    이름.err   기대 stderr (선택 — 없으면 stderr는 검사하지 않음)
    이름.code  기대 종료 코드 (선택 — 없으면 0을 기대)

입력을 넘기는 방식은 --cmd 문자열로 정한다
    --cmd "./build/mysh"           입력 파일을 stdin으로 넣는다 (셸, REPL, DB CLI)
    --cmd "./build/lang {in}"      {in} 자리에 입력 파일 경로를 넣는다 (스크립트 언어)
                                   이때 stdin은 비워 둔다

사용 예
    python3 tools/runtests.py --cmd ./01-shell/build/mysh 01-shell/tests
    python3 tools/runtests.py --cmd "./build/lang {in}" -k closure tests/
"""

import argparse
import difflib
import shlex
import subprocess
import sys
from pathlib import Path

# 터미널일 때만 색을 쓴다. make 로그를 파일로 남길 때 제어 문자가 섞이지 않게 하려는 것.
USE_COLOR = sys.stdout.isatty()


def color(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def find_tests(test_dir, keyword):
    """.in 파일을 기준으로 테스트를 찾는다. 이름순 정렬로 실행 순서를 항상 같게 한다."""
    tests = []
    for in_path in sorted(test_dir.rglob("*.in")):
        if keyword and keyword not in str(in_path.relative_to(test_dir)):
            continue
        tests.append(in_path)
    return tests


def build_argv(cmd, in_path):
    """--cmd를 실행할 인자 목록으로 바꾼다.

    셸(shell=True)을 거치지 않고 직접 실행한다. 테스트 대상이 우리가 만든 셸일 때
    시스템 셸이 끼어들면 무엇이 무엇을 해석했는지 헷갈리기 때문이다.
    """
    argv = shlex.split(cmd)
    uses_placeholder = any("{in}" in arg for arg in argv)
    argv = [arg.replace("{in}", str(in_path)) for arg in argv]
    return argv, uses_placeholder


def read_text(path):
    # 기대 출력 파일은 바이트 그대로 비교한다. 줄바꿈 변환을 하지 않아야
    # '마지막 줄 개행 누락' 같은 실제 버그를 잡을 수 있다.
    return path.read_bytes().decode("utf-8", errors="replace")


def show_diff(label, expected, actual):
    print(f"    --- {label}: 기대(-) / 실제(+)")
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        lineterm="",
        n=2,
    )
    for line in list(diff)[2:]:  # 앞의 파일 이름 두 줄은 생략
        line = line.rstrip("\n")
        if line.startswith("+"):
            line = color(line, "32")
        elif line.startswith("-"):
            line = color(line, "31")
        print("    " + line)
    if expected and not expected.endswith("\n"):
        print("    (기대 출력의 마지막 줄에 개행 없음)")
    if actual and not actual.endswith("\n"):
        print("    (실제 출력의 마지막 줄에 개행 없음)")


def run_one(in_path, args):
    """테스트 하나를 실행하고 (통과 여부, 실패 이유 목록)을 돌려준다."""
    stem = in_path.with_suffix("")
    out_path = stem.with_suffix(".out")
    err_path = stem.with_suffix(".err")
    code_path = stem.with_suffix(".code")

    if not out_path.exists():
        return False, [f"기대 출력 파일 없음: {out_path.name}"], None

    argv, uses_placeholder = build_argv(args.cmd, in_path)

    try:
        if uses_placeholder:
            stdin = subprocess.DEVNULL
            proc = subprocess.run(argv, stdin=stdin, capture_output=True,
                                  timeout=args.timeout)
        else:
            with open(in_path, "rb") as f:
                proc = subprocess.run(argv, stdin=f, capture_output=True,
                                      timeout=args.timeout)
    except FileNotFoundError:
        return False, [f"실행 파일을 찾을 수 없음: {argv[0]}"], None
    except subprocess.TimeoutExpired:
        # 무한 루프·교착 상태를 '실패'로 보고하고 다음 테스트로 넘어간다
        return False, [f"시간 초과 ({args.timeout}초)"], None

    reasons = []
    actual_out = proc.stdout.decode("utf-8", errors="replace")
    actual_err = proc.stderr.decode("utf-8", errors="replace")

    expected_out = read_text(out_path)
    if actual_out != expected_out:
        reasons.append(("stdout", expected_out, actual_out))

    if err_path.exists():
        expected_err = read_text(err_path)
        if actual_err != expected_err:
            reasons.append(("stderr", expected_err, actual_err))

    expected_code = int(read_text(code_path).strip()) if code_path.exists() else 0
    # 시그널로 죽으면 returncode가 음수(-시그널 번호)다. 셸 관례(128+n)와 다르니 그대로 보여 준다.
    if proc.returncode != expected_code:
        reasons.append(f"종료 코드: 기대 {expected_code}, 실제 {proc.returncode}")

    return not reasons, reasons, actual_err


def main():
    parser = argparse.ArgumentParser(
        description="입력 파일 → 기대 출력 파일 비교 테스트 러너",
        epilog="--cmd 안의 {in}은 입력 파일 경로로 바뀐다. {in}이 없으면 입력을 stdin으로 넣는다.",
    )
    parser.add_argument("test_dir", type=Path, help="*.in / *.out 파일이 있는 디렉터리")
    parser.add_argument("--cmd", required=True, help='실행할 명령. 예: "./build/mysh", "./build/lang {in}"')
    parser.add_argument("-k", dest="keyword", help="이름에 이 문자열이 들어간 테스트만 실행")
    parser.add_argument("--timeout", type=float, default=5.0, help="테스트당 제한 시간(초), 기본 5")
    parser.add_argument("-v", "--verbose", action="store_true", help="통과한 테스트도 출력")
    args = parser.parse_args()

    if not args.test_dir.is_dir():
        print(f"테스트 디렉터리가 없음: {args.test_dir}", file=sys.stderr)
        return 2

    tests = find_tests(args.test_dir, args.keyword)
    if not tests:
        print("실행할 테스트가 없음", file=sys.stderr)
        return 2

    failed = []
    for in_path in tests:
        name = str(in_path.relative_to(args.test_dir).with_suffix(""))
        ok, reasons, actual_err = run_one(in_path, args)
        if ok:
            if args.verbose:
                print(f"{color('PASS', '32')} {name}")
            continue

        failed.append(name)
        print(f"{color('FAIL', '31')} {name}")
        for reason in reasons:
            if isinstance(reason, tuple):
                show_diff(*reason)
            else:
                print(f"    {reason}")
        # stderr를 검사하지 않는 테스트라도 실패 원인을 찾는 데 도움이 되므로 보여 준다
        if actual_err and not any(isinstance(r, tuple) and r[0] == "stderr" for r in reasons):
            print("    --- stderr (참고)")
            for line in actual_err.splitlines()[:20]:
                print("    " + line)

    passed = len(tests) - len(failed)
    summary = f"{passed}/{len(tests)} 통과"
    print(color(summary, "32" if not failed else "31"))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
