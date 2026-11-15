# 빌드 방법

번역 대본(`text/`)과 글꼴 파일은 저장소에 없으므로, 아래는 같은 자료를 갖춘 경우의 절차입니다.

## 준비
- Python 3.11 이상, `pip install pillow keystone-engine` (분석용 capstone 선택)
- 원본 `Dokapon! Ikari no Tekken (Japan) (Rev 2).bin` (README의 해시와 일치)을 저장소 상위 폴더에 둡니다.
- 글꼴: `fonts/Galmuri9.ttf`, `fonts/Galmuri11.ttf`, 상위 폴더에 `NanumSquareNeo-bRg.ttf`, `NanumSquareNeo-dEb.ttf`, `NanumSquareNeo-eHv.ttf`

## 순서
1. 원본 추출: `python tools/extract.py "../Dokapon! Ikari no Tekken (Japan) (Rev 2).bin" orig` → `orig/` (소리·영상 등 번역과 무관한 파일은 건너뛰고, 빌드가 필요하면 원본 디스크에서 직접 읽음). 글자 표 `text/table.txt`(코드 → 문자)가 필요합니다.
2. 원문 추출: `python tools/extract_text.py` → `text/ja.json`, 번역 입력 `text/in/*.tsv`
3. 번역: `text/ko/*.tsv` (`id<TAB>한국어`, `docs/TRANSLATION_GUIDE.md`), 검사 `python tools/ko.py text/ko/*.tsv` → `오류 0`
4. 빌드: `python build.py` → 상위 폴더에 `Dokapon! Ikari no Tekken (Japan) (Rev 2) [KR].bin` (로그는 `build.log`)
5. 차분 파일: `xdelta3 -e -0 -s "Dokapon! Ikari no Tekken (Japan) (Rev 2).bin" "Dokapon! Ikari no Tekken (Japan) (Rev 2) [KR].bin" Dokapon_Ikari_no_Tekken_KO_v1.2.xdelta`
