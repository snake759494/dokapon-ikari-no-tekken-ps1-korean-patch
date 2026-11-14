# 도카폰! 분노의 철검 (PS1) 비공식 한글패치

PS1 일본판 **ドカポン！怒りの鉄剣 (도카폰! 분노의 철검, SLPS-01559)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 적용 방법
1. 아래 해시와 일치하는 **원본 `.bin`/`.cue`** (Redump 형식 Rev 2, 트랙 1개)를 준비합니다. (CHD·PBP·ECM 등으로 변환한 이미지에는 적용할 수 없습니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Dokapon! Ikari no Tekken (Japan) (Rev 2).bin'`
2. xdeltaUI 같은 도구로 원본 `.bin` 에 `Dokapon_Ikari_no_Tekken_KO_v1.0.xdelta` 를 적용합니다. (Patch = xdelta, Source File = 원본 BIN, Output File = 새 파일명)
   - 명령줄: `xdelta3 -d -s "Dokapon! Ikari no Tekken (Japan) (Rev 2).bin" Dokapon_Ikari_no_Tekken_KO_v1.0.xdelta "Dokapon! Ikari no Tekken (Korean).bin"`
3. 원본 `.cue` 를 복사해 이름을 바꾸고, 안의 `FILE "..."` 줄을 새 `.bin` 파일명으로 고칩니다.
4. 만들어진 `.cue` 를 DuckStation 등 PS1 에뮬레이터나 ODE 장치에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 BIN 크기 | 219,563,904 바이트 |
| 원본 BIN MD5 | `de9a5e3cd33a7863ca6470014a17c074` |
| 원본 BIN SHA-256 | `99eba7cf5c261a4102a1bfd118bb9e827253806f78d67fc4b8b4a6e9fd934232` |
| xdelta SHA-256 | `7337213393f2b7023c89e4b4d2933e2f7eeb062d64b946ad3bfa13f6ff6ad379` |
| 결과 BIN 크기 | 219,563,904 바이트 |
| 결과 BIN SHA-256 | `a97be8b56636daeecc766cb16eabb66de103e4671807b4f3ce50ca589305a6ad` |

## 주의
- 원본에서 만든 **상태저장(세이브 스테이트)** 은 불러오지 마세요. 글꼴 배치가 달라 글자가 깨집니다. 메모리 카드 세이브는 그대로 쓸 수 있습니다.
- xdelta는 압축하지 않은 형식(`-0`)입니다(약 260KB).

## 한글화 내용
- 대사·메뉴·아이템·마법·장비·몬스터·이벤트·전투 메시지·도움말 문자열 3,874개 전수 직접 번역
- 게임 글꼴(16×16)에 한글 1,054자 추가, 글자 출력 루틴을 고쳐 반각 띄어쓰기·반각 문장부호 지원, 요일 표시 한글화
- 이름 입력 화면의 가나 표를 한글 음절 180자 표로 교체
- 그림 글자 — 상점·은행·교회·여관·성·마을·카지노 버튼, 상점 간판·은행 「예금」·성 「도카폰성」·아이템점 「감정」 현수막, 전투 커맨드(공격·방어·항복·카운터·필살)·특기 35종·마법 55종 이름, 장 제목 10종, 오프닝 문장, 타이틀 메뉴·캐릭터 선택 화면(이름·특기·프로필), 보드 지도 마을 이름 간판, 순위·주 표시
- 도구·마법 목록 칸(한글 4자)에 맞춰 일부 아이템·마법 이름은 짧게 옮김(예: 1의 크리스탈 → 1마수정, 우르릉썬더 → 우르썬더)
- 글꼴: 본문 나눔스퀘어 네오, 그림 글자 나눔스퀘어 네오, 아주 작은 그림 글자 갈무리9·11

## 그대로 둔 것
- 음성, 영상, 「BANK」「SALE」「DOKAPON CASTLE」 등 그림 속 영문, 저작권 표기, 메모리 카드 관리 화면에 보이는 세이브 제목

## 검증 범위
DuckStation에서 보드 화면 메뉴·정보(강함·장비) 화면, 교회(워프)·여관·아이템점·감정·마법점·무기점·은행·도카폰성 메뉴와 대사, 전투(커맨드·마법공격·승리 결과), 도구·마법 사용 화면을 확인했습니다. 모든 문자열 파일을 전수 검사해 번역이 빠진 줄이 없고 길이·제어 코드 오류가 없는 것을 확인했습니다. 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/TRANSLATION_GUIDE.md](docs/TRANSLATION_GUIDE.md) — 번역 지침
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
