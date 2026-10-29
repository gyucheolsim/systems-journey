# 개발 환경 (Docker)

호스트가 Windows이므로 Linux 도구는 컨테이너(Ubuntu 24.04)에서 쓴다.

| 구분 | 어디서 |
|---|---|
| 코드 편집 | 호스트 (VS Code 등) |
| 빌드·실행·테스트·디버깅 | 컨테이너 (`/work` = 저장소) |
| `git`, `gh` | 호스트 (GitHub 인증 정보가 호스트에 있음) |

## 들어 있는 도구

| 용도 | 도구 |
|---|---|
| C17 / C++20 컴파일러 | gcc·g++ 13, clang·clang++ 18 |
| 메모리 검사 | ASan·UBSan (GCC, Clang 모두), valgrind |
| 디버깅·추적 | gdb, strace, ltrace |
| 기타 | make, python3, man 페이지, curl, netcat |

## 준비 (한 번만)

1. Docker Desktop 설치: <https://www.docker.com/products/docker-desktop/>
   (WSL 2 백엔드 사용. 설치 중 안내에 따라 WSL을 켜고 재부팅)
2. Docker Desktop을 실행한 뒤 확인: `docker version`
3. 이미지 빌드 (저장소 루트에서): `docker compose -f docker/compose.yaml build`

## 사용

```powershell
# 컨테이너 셸로 들어가기 (나올 때는 exit — 컨테이너는 자동 삭제, 파일은 저장소에 남음)
docker compose -f docker/compose.yaml run --rm dev

# 같은 동작의 짧은 스크립트
.\docker\enter.ps1
.\docker\enter.ps1 make -C 01-shell test

# 서버 프로젝트(05·06)를 호스트에서 접속하려면 포트 열기 (8080, 6379)
docker compose -f docker/compose.yaml run --rm --service-ports dev
```

## 설정 이유

| 설정 | 이유 |
|---|---|
| `stdin_open` + `tty` | `-it`와 같다. 셸 작업 제어·줄 편집기는 진짜 터미널이 있어야 동작한다 |
| `cap_add: SYS_PTRACE` | gdb·strace·ltrace가 ptrace(2)를 쓰기 때문 |
| `seccomp=unconfined` | 기본 seccomp 프로필이 막는 `personality(2)` 등을 gdb가 쓰기 때문 (ASLR 끄기) |
| `init: true` | 우리 프로그램이 PID 1이 되면 시그널 기본 동작이 달라져 실험 결과가 왜곡된다 |
| 사용자 `dev` (UID 1000) | root는 권한 오류를 가려 버린다 |

## 동작 확인

컨테이너 안에서:

```bash
gcc --version && g++ --version && clang --version && clang++ --version
gdb --version | head -1
strace -c true            # ptrace 권한 확인
echo 'int main(void){return 0;}' > /tmp/t.c && gcc -g /tmp/t.c -o /tmp/t \
  && gdb -batch -ex run /tmp/t   # 경고 없이 "exited normally"가 나와야 정상
valgrind --version
```
