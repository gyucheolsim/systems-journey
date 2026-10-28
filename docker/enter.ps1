# 컨테이너 셸로 들어가거나(인자 없음) 명령 하나를 실행한다.
#   .\docker\enter.ps1
#   .\docker\enter.ps1 make -C 01-shell test
$compose = Join-Path $PSScriptRoot "compose.yaml"
docker compose -f $compose run --rm dev @args
