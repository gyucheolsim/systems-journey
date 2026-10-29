# systems-journey 공통 규칙

OSTEP(v1.10)과 CS:APP(3판)을 읽으며 운영체제·시스템 프로젝트를 순서대로 만드는 시리즈다.
프로젝트 순서와 읽기 목록은 [ROADMAP.md](ROADMAP.md)에 있다.

## 학습 방식

- 사용자는 직접 코드를 짜지 않고, Claude가 짠 코드를 읽으며 공부한다.
  영리한 트릭보다 **읽기 쉬운 코드**를 우선한다.
- 사용자가 개념을 물으면 **코드를 수정하지 않고 설명만** 한다.
- **한 번에 한 단계만** 구현하고 멈춘다. 사용자가 확인한 뒤 다음 단계로 간다.

## 작업 환경

- 편집은 호스트(Windows)에서, 빌드·실행·테스트는 Docker 컨테이너 안에서 한다.
  - 컨테이너 진입(저장소 루트에서): `docker compose -f docker/compose.yaml run --rm dev`
  - 컨테이너 안에서 저장소는 `/work`에 마운트된다.
  - 컨테이너 밖에서 한 명령만 돌릴 때:
    `docker compose -f docker/compose.yaml run --rm dev make -C 01-shell test`
- `git`과 `gh`는 **호스트에서만** 실행한다 (GitHub 인증 정보가 호스트에 있다).
- 줄바꿈은 LF로 통일한다 (`.gitattributes`). 셸 스크립트에 CRLF가 섞이면 컨테이너에서 깨진다.

## 언어

- 언어는 프로젝트마다 **C17** 또는 **C++20** 중 하나를 쓴다.
  프로젝트를 시작할 때 ROADMAP.md의 권장 언어와 그 이유를 알려주고, **사용자의 확인을 받은 뒤** 시작한다.
- 표준 라이브러리와 POSIX만 쓴다 (`_POSIX_C_SOURCE 200809L`). 웹 프론트엔드(08)는 예외.
  외부 라이브러리가 필요하면 **먼저 묻는다**.
- **C**: 매크로보다 `static inline` 함수를 우선 쓴다.
- **C++**: 자원(메모리, 파일 디스크립터, 락 등)은 RAII로 관리한다.
  - 그 프로젝트에서 배우려는 자료구조(B-트리, 버퍼 풀, 해시 테이블 등)는 STL로 대체하지 않고
    직접 구현한다. STL은 학습 대상이 아닌 곳에만 쓴다.
  - 템플릿 메타프로그래밍처럼 읽기 어려운 기법은 피한다.
  - 파일 이름은 `.cpp` / `.hpp`로 한다.
- **C와 C++가 섞일 때** (예: C로 만든 모듈을 C++ 프로젝트에서 재사용)는 `extern "C"` 경계를
  한 곳(감싸는 헤더 하나)에 모으고, 그 이유를 주석으로 남긴다.

## 코드 규칙

- 주석은 한국어로, '무엇을 하는지'보다 **'왜 이렇게 설계했는지'**를 설명한다.
- 시스템 콜과 라이브러리 호출의 **반환값은 항상 확인**한다.
  `EINTR`, 짧은 읽기/쓰기처럼 실패가 아닌 경우도 의도적으로 처리한다.
- 지금 만드는 부품이 나중에 재사용될 수 있게 설계한다 (ROADMAP.md의 '연결' 참고).
  재사용할 부품은 `foo.h` / `foo.c` 쌍으로 분리하고, 전역 상태에 기대지 않게 한다.

## 빌드

- 프로젝트별 `Makefile`로 빌드한다. 산출물은 모두 프로젝트 안의 `build/`에 둔다
  (`.gitignore`가 `build/`를 무시한다).
- 아래 규칙(경고 최대, `make asan` 타깃)은 **C와 C++에 똑같이** 적용한다.
- C 기본 플래그:
  ```make
  CFLAGS   := -std=c17 -D_POSIX_C_SOURCE=200809L -g -O1 \
              -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wstrict-prototypes \
              -Wmissing-prototypes -Wpointer-arith -Wcast-qual -Wformat=2 \
              -Wnull-dereference -Wvla
  ```
- C++ 기본 플래그 (C 전용 경고 대신 C++에서 의미 있는 경고를 켠다):
  ```make
  CXXFLAGS := -std=c++20 -D_POSIX_C_SOURCE=200809L -g -O1 \
              -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wold-style-cast \
              -Wnon-virtual-dtor -Woverloaded-virtual -Wmissing-declarations \
              -Wcast-qual -Wformat=2 -Wnull-dereference -Wvla
  ```
- 필수 타깃:
  - `make` — 기본 빌드
  - `make asan` — `-fsanitize=address,undefined -fno-omit-frame-pointer`로 빌드
  - `make test` — 기본 빌드 후 `tools/runtests.py`로 테스트
  - `make clean` — `build/` 삭제
  - (권장) `make test-asan` — ASan 빌드로 같은 테스트
- GCC와 Clang 둘 다 경고 없이 빌드되어야 한다: C는 `make CC=clang`, C++는 `make CXX=clang++`.

## 테스트

- '입력 파일 → 기대 출력 파일' 비교 방식이고, 공통 러너 `tools/runtests.py`를 쓴다.
- 테스트는 프로젝트의 `tests/` 아래에 둔다:
  - `이름.in` 입력, `이름.out` 기대 stdout (필수)
  - `이름.err` 기대 stderr, `이름.code` 기대 종료 코드 (선택)
- 실행 예: `python3 ../tools/runtests.py --cmd ./build/mysh tests/`
  (자세한 사용법은 `python3 tools/runtests.py --help`)
- 기대 출력은 손으로 쓰고 직접 검증한다. 프로그램 출력을 그대로 복사해 기대값으로 만들지 않는다.

## 교재 연결

- 단계를 시작할 때, **코드를 쓰기 전에** 먼저 읽을 OSTEP 장과 CS:APP 장·절을 알려준다
  (ROADMAP.md의 읽기 목록 참고, 그 단계에 해당하는 부분만 골라서).
- 단계가 끝나면 그 프로젝트의 `NOTES.md`에 다음 형식으로 추가한다:

  ```markdown
  ## s<번호>: <단계 이름> (YYYY-MM-DD)
  ### 구현한 것
  ### 핵심 설계 결정
  ### 관련 OSTEP 장
  ### 관련 CS:APP 장·절
  ### 두 책의 관점 차이 (있으면)
  ### 남은 의문점
  ### 다음 프로젝트로 가져갈 것
  ```
- 단계가 끝나면 사용자에게 다음을 제안한다:
  - 코드 읽는 순서 (파일·함수 단위)
  - 이해도 확인 질문 3개
  - '일부러 고장 내보기' 실험 1개 (무엇을 바꾸면 어떤 증상이 나오는지 예측해 보게)

## GitHub 기록

- 저장소: `gyucheolsim/systems-journey`
- 프로젝트 폴더 이름은 `NN-이름` (예: `01-shell`), 짧은 이름은 커밋·태그에 쓴다
  (shell, malloc, chip8, lang, httpd, redis, db, web, ...).
- 프로젝트를 시작할 때:
  - 권장 언어를 알리고 확인을 받는다 (위 '언어' 참고).
  - 폴더(`NN-이름/`)와 `README.md`, `NOTES.md`, `Makefile`, `tests/`를 만든다.
  - GitHub 마일스톤을 만든다 (예: `01 shell`).
  - 단계마다 이슈를 하나씩 만들어 마일스톤에 연결한다 (제목 예: `[shell] s1: 기본 실행 루프`).
- 단계가 끝나면 **이 순서로** 기록한다:
  1. 루트 `README.md` 진행 현황 표에 한 줄 추가
  2. 커밋 — 메시지 형식 `[shell] s1: 기본 실행 루프`, 본문에 `Closes #번호`
  3. 태그 `<짧은이름>-s<번호>` (예: `shell-s1`)
  4. 커밋과 태그 push (`git push && git push origin <태그>`)
- 진행 표의 '변경 비교 링크'는 **이전 단계 태그**와 비교하는 compare 링크다:
  `https://github.com/gyucheolsim/systems-journey/compare/<이전태그>...<이번태그>`
  - 프로젝트의 첫 단계는 직전 프로젝트의 마지막 태그와, 맨 첫 단계(`shell-s1`)는 `setup` 태그와 비교한다.
- 프로젝트가 끝나면 그 프로젝트의 `README.md`에 설계 요약, 다이어그램(Mermaid), 측정 결과를 정리한다.
  측정 수치는 `results/*.csv`로도 남긴다 (첫 줄은 헤더, 단위는 열 이름에 표기. 예: `latency_us`).
  나중에 홈페이지(08)에서 읽어 쓴다.
