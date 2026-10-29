# systems-journey

셸부터 malloc, 에뮬레이터, 스크립트 언어, 웹 서버, 데이터베이스, 커널까지 —
운영체제와 시스템 프로그래밍을 **직접 만들어 보며** 배우는 프로젝트 시리즈입니다.

- 교재: [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/) v1.10, *Computer Systems: A Programmer's Perspective* (CS:APP) 3판
- 언어: 프로젝트마다 C17 또는 C++20 (표준 라이브러리 + POSIX), 08 홈페이지의 프론트엔드는 TypeScript.
  프로젝트별 권장 언어는 [ROADMAP.md](ROADMAP.md)에 있습니다
- 프로젝트 순서와 읽기 목록: [ROADMAP.md](ROADMAP.md)
- 단계별 학습 기록: 각 프로젝트 폴더의 `NOTES.md`

## 진행 현황

| 프로젝트 | 단계 | 날짜 | 한 줄 요약 | NOTES | 변경 비교 |
|---|---|---|---|---|---|
| — | setup | 2026-10-28 | 저장소 구조, Docker 개발 환경, 공통 테스트 러너 준비 | — | — |

## 프로젝트

| # | 프로젝트 | 상태 |
|---|---|---|
| 01 | 셸 | 예정 |
| 02 | malloc | 예정 |
| 03 | CHIP-8 에뮬레이터 | 예정 |
| 04 | 스크립트 언어 | 예정 |
| 05 | 웹 서버 | 예정 |
| 06 | Redis 클론 | 예정 |
| 07 | 데이터베이스 | 예정 |
| 08 | 풀스택 홈페이지 | 예정 |
| 09 | 심화 (커널 · TCP/IP · Raft) | 예정 |

## 개발 환경

편집은 호스트에서, 빌드와 실행은 Docker 컨테이너(Ubuntu 24.04)에서 합니다.
컨테이너에는 gcc·g++, clang·clang++, make, gdb, strace, valgrind, python3가 들어 있습니다.

```bash
# 저장소 루트에서 — 컨테이너 셸로 들어가기 (/work = 저장소)
docker compose -f docker/compose.yaml run --rm dev

# 명령 하나만 실행하기
docker compose -f docker/compose.yaml run --rm dev make -C 01-shell test
```

자세한 내용은 [docker/README.md](docker/README.md), 테스트 러너는 [tools/README.md](tools/README.md)를 보세요.

## 저장소 구조

```
systems-journey/
  README.md     이 파일 (진행 현황)
  CLAUDE.md     시리즈 공통 규칙
  ROADMAP.md    프로젝트 순서, 연결, 읽기 목록
  docker/       공통 개발 환경
  tools/        공통 테스트 러너
  01-shell/ …   프로젝트 폴더 (시작할 때 추가)
```
