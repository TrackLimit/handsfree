# Handsfree

[English](README.md) | **한국어**

푸시투토크 방식의 **로컬** 음성 인식(STT) macOS 앱입니다. 키를 누른 채 말하고 손을 떼면, 음성이
기기 안에서 텍스트로 변환되어 현재 포커스된 앱(터미널, 편집기, 브라우저 등)의 커서 위치에
붙여넣어집니다. 오디오는 절대 기기 밖으로 나가지 않습니다.

Apple Silicon에서 [MLX Whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper)로
구동됩니다. **영어, 한국어, 일본어**를 지원하며 메뉴 막대 아이콘에서 전환할 수 있습니다.

---

## 요구 사항

- **Apple Silicon Mac** (M1 이상) — 모델이 Apple의 MLX/Metal에서 실행됩니다.
- **macOS 13.5 이상.**
- **[uv](https://docs.astral.sh/uv/)** (Python 도구체인 + 러너). 설치:
  ```sh
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **약 2 GB의 여유 디스크 공간**(의존성 + 음성 모델)과 최초 실행 시 인터넷 연결.

## 설치

```sh
git clone <repository-url> handsfree
cd handsfree
uv sync                      # CPython 3.12 + 의존성(torch 포함, ~1–2 GB) 설치
./packaging/build_app.sh     # ~/Applications/Handsfree.app 빌드
open ~/Applications/Handsfree.app
```

> **앱은 각자 자신의 기기에서 빌드합니다 — 미리 빌드된 다운로드는 없습니다.** 번들은 *alias 모드*로
> 만들어져 (용량이 큰) 의존성을 복사해 넣지 않고 로컬 클론을 참조합니다. 따라서 한 Mac에서 만든
> `Handsfree.app`은 다른 Mac에서 동작하지 않습니다. 각자 클론한 뒤 `build_app.sh`를 실행하세요.
> (torch/mlx를 다시 묶지 않으므로 빠릅니다.)

최초 실행 시 음성 모델(`whisper-large-v3-turbo-q4`, ~0.46 GB)이 자동으로 다운로드되고, 이어서
macOS가 권한을 요청합니다.

## 권한 부여 (최초 1회)

Handsfree는 전역 단축키를 감지하고 텍스트를 붙여넣어야 하므로 두 가지 권한이 필요합니다.
**시스템 설정 → 개인정보 보호 및 보안**을 열고 **두 항목 모두**에서 **Handsfree**를 켜세요:

- **손쉬운 사용(Accessibility)** — 붙여넣기(⌘V 합성)와 전역 단축키 리스너 실행용.
- **입력 모니터링(Input Monitoring)** — 푸시투토크 키 감지용.

목록에 `Handsfree`가 없으면 **+** 를 눌러 `~/Applications/Handsfree.app`을 선택하세요.
**마이크** 권한은 처음 받아쓰기를 할 때 별도로 요청됩니다 — 허용하세요.

⚠️ **권한은 새로 실행할 때만 적용됩니다.** 권한을 켠 뒤 메뉴의 **Quit Handsfree**로 앱을 종료하고
다시 여세요:

```sh
open ~/Applications/Handsfree.app
```

## 사용법

**오른쪽 Command** 키를 누른 채 말하고 떼면, 변환된 텍스트가 커서 위치에 붙여넣어집니다.

**🎙 메뉴 막대 아이콘**에서 언어를 실시간으로 전환할 수 있습니다(**영어 / 한국어 / 일본어**).
선택은 다음 발화부터 적용되며 아이콘에 현재 코드가 표시됩니다(예: `🎙 KO`). **Quit Handsfree**도
같은 메뉴에 있습니다.

## 설정 (환경 변수)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `HANDSFREE_PTT_KEY` | `cmd_r` | 푸시투토크 키: `cmd_r`, `cmd_l`, `alt_r`, `ctrl_r`, `f8`, `f9` |
| `HANDSFREE_MODEL` | `mlx-community/whisper-large-v3-turbo-q4` | MLX Whisper 저장소. 더 높은 정확도는 `…/whisper-large-v3-turbo` |
| `HANDSFREE_LANGUAGE` | `en` | 시작 언어: `en`, `ko`, `ja` |

## 제거

```sh
./packaging/uninstall.sh           # 앱 종료, 번들 삭제, 권한 초기화
./packaging/uninstall.sh --model   # 캐시된 음성 모델(~442 MB)도 삭제
```

`~/Applications/Handsfree.app`을 삭제하고 손쉬운 사용 / 입력 모니터링 / 마이크 권한을 초기화합니다.
프로젝트 폴더는 그대로 두므로, 소스가 더 이상 필요 없다면 저장소 폴더를 직접 `rm -rf` 하세요.

## 문제 해결

- **메뉴 막대에 🎙가 안 보이나요?** 노치가 있는 MacBook에서는 메뉴 막대가 꽉 차면 새 아이콘이
  노치 *뒤에* 숨습니다. 다른 메뉴 막대 앱을 몇 개 종료하거나(또는 아이콘 관리 앱 사용) 확인하세요.
- **키를 눌러도 아무 일도 없거나 붙여넣기가 안 됩니다.** 위 권한이 **Handsfree**에 부여되지 않았거나,
  마지막 (재)빌드 이전에 부여된 것입니다. 손쉬운 사용 + 입력 모니터링에서 Handsfree를 다시 켜고
  **재실행**하세요. 그래도 안 되면 항목을 초기화하세요:
  ```sh
  tccutil reset Accessibility com.handsfree.dictation
  tccutil reset ListenEvent  com.handsfree.dictation
  ```
  그런 다음 다시 부여하세요.
- **로그/오류를 보고 싶다면** 번들 바이너리를 포그라운드로 실행하세요:
  ```sh
  ~/Applications/Handsfree.app/Contents/MacOS/Handsfree   # Ctrl-C로 중지
  ```
- **앱을 빌드하지 않고 빠르게 테스트:** `uv run handsfree` — 단, 이 경우 *실행한 터미널에만*
  받아쓰기가 됩니다(앱의 안정적인 서명 신원이 없으면 macOS가 단축키를 해당 프로세스로 한정함).
  앱에 권한을 부여하기 전 빠른 확인용으로 쓰세요.

## 동작 방식

| 단계 | 내용 |
|---|---|
| 트리거 | `pynput`로 전역 푸시투토크 단축키 |
| 캡처 | `sounddevice`로 마이크 → 16 kHz 모노 버퍼 |
| 변환 | 로컬 MLX Whisper(`mlx-whisper`), Metal 가속 |
| 삽입 | 클립보드 설정(`NSPasteboard`) → ⌘V → 이전 클립보드 복원 |
| UI | `rumps` 기반 메뉴 막대 언어 선택 |

`.app`은 [py2app](https://py2app.readthedocs.io/) **alias** 번들입니다. 작은 서명된 스텁이 Python을
인프로세스로 실행하여 앱이 고유한 신원을 갖습니다(개인정보 보호 설정에 **Handsfree**로 표시되고,
Python/uv 업데이트 후에도 권한이 유지됨). 번들 ID, `Info.plist`, Python 버전을 변경한 경우
`./packaging/build_app.sh`로 다시 빌드하세요. 일상적인 코드 수정은 다시 빌드하지 않아도 즉시
반영됩니다.
