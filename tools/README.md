# tools

## runtests.py — 공통 테스트 러너

'입력 파일 → 기대 출력 파일'을 비교한다. 실행할 명령을 인자로 받으므로
셸, 스크립트 언어, DB 등 모든 프로젝트에서 같은 방식으로 쓴다.

### 테스트 파일

```
tests/
  echo.in      입력 (필수)
  echo.out     기대 stdout (필수)
  echo.err     기대 stderr (선택 — 없으면 검사 안 함)
  echo.code    기대 종료 코드 (선택 — 없으면 0)
```

하위 디렉터리도 찾는다 (`tests/pipe/basic.in` → 테스트 이름 `pipe/basic`).

### 입력을 넘기는 두 방식

| `--cmd` | 동작 | 쓰는 곳 |
|---|---|---|
| `"./build/mysh"` | 입력 파일을 **stdin**으로 넣는다 | 셸, REPL, DB CLI |
| `"./build/lang {in}"` | `{in}`을 **입력 파일 경로**로 바꾼다 (stdin은 비움) | 스크립트 언어, 에뮬레이터 |

### 옵션

```
-k 문자열      이름에 문자열이 들어간 테스트만
--timeout 초   테스트당 제한 시간 (기본 5초, 넘으면 실패)
-v             통과한 테스트도 표시
```

종료 코드: 모두 통과 0, 하나라도 실패 1, 사용법 오류 2.

### Makefile에서

```make
test: all
	python3 ../tools/runtests.py --cmd ./build/mysh tests/
```
