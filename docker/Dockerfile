# systems-journey 공통 개발 환경
# 호스트(Windows)에서 편집하고, 이 컨테이너에서 빌드·실행·디버깅한다.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Asia/Seoul

# 필수 도구: 컴파일러 두 종(GCC, Clang)으로 C17·C++20 코드의 경고를 교차 확인하고,
# gdb/strace/valgrind로 프로세스·메모리를 관찰한다.
#   gcc/g++: C·C++ 컴파일러 (build-essential에도 들어 있지만 명시해 둔다)
#   clang: clang과 clang++를 함께 설치한다
#   libclang-rt-18-dev: clang의 ASan·UBSan 런타임. 없으면 clang으로 make asan 링크가 실패한다
#   llvm: llvm-symbolizer — clang ASan 보고서의 주소를 함수 이름·줄 번호로 바꿔 준다
# 나머지는 프로젝트 진행 중 자주 쓰는 보조 도구다
#   man-pages: 시스템 콜 문서 (man 2 fork)
#   procps/psmisc: ps, pstree — 셸의 작업 제어 확인용
#   curl/netcat/iproute2: 05 웹 서버, 06 Redis 클론 테스트용
# 최소 이미지는 설치하는 man 페이지를 지우도록 설정돼 있어, 설치 전에 그 설정을 없앤다.
RUN rm -f /etc/dpkg/dpkg.cfg.d/excludes \
    && apt-get update && apt-get install -y --no-install-recommends \
        build-essential gcc g++ clang libclang-rt-18-dev llvm \
        make gdb strace ltrace valgrind \
        python3 \
        man-db manpages manpages-dev manpages-posix manpages-posix-dev \
        procps psmisc less file vim-tiny \
        curl netcat-openbsd iproute2 \
        ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/*

# 최소 이미지는 진짜 man을 man.REAL로 옮기고 안내 스크립트로 바꿔 둔다. 원래대로 되돌린다.
RUN rm /usr/bin/man \
    && dpkg-divert --quiet --local --remove --rename /usr/bin/man \
    && mandb --quiet

# root가 아닌 사용자로 작업한다. 권한 문제를 root가 가려 버리면
# 파일 권한·시그널 관련 동작을 잘못 이해하기 쉽기 때문이다.
# ubuntu:24.04에는 UID 1000인 'ubuntu' 사용자가 이미 있어 이름만 바꿔 쓴다.
RUN usermod -l dev -d /home/dev -m ubuntu && groupmod -n dev ubuntu

# gdb가 기본으로 쓰는 설정: 출력 페이지 나눔 끄기, 히스토리 저장
RUN printf 'set pagination off\nset history save on\nset history filename ~/.gdb_history\n' \
        > /home/dev/.gdbinit && chown dev:dev /home/dev/.gdbinit

USER dev
WORKDIR /work
CMD ["bash", "-l"]
