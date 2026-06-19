"""경기 전 체크리스트."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChecklistItem:
    label: str
    done: bool
    hint: str


def build_pre_match_checklist(
    *,
    weight_total: int,
    sim_count: int,
    has_simulation: bool,
    has_ai_scenario: bool,
    has_report: bool,
    has_board: bool,
    tactics_linked: bool,
    has_url_or_export: bool = False,
) -> list[ChecklistItem]:
    return [
        ChecklistItem("가중치 합계 100%", weight_total == 100, f"현재 {weight_total}%"),
        ChecklistItem("몬테카를로 1,000회+", has_simulation and sim_count >= 1000, f"설정 {sim_count:,}회"),
        ChecklistItem("AI 시나리오 1회 이상", has_ai_scenario, "왼쪽 AI 시나리오 실행"),
        ChecklistItem("매치 리포트 생성", has_report, "GPT/규칙 리포트"),
        ChecklistItem("상황판 시뮬레이션", has_board, "전술 보드 재생"),
        ChecklistItem("상황판→모델 연동", tactics_linked, "포메이션·부상 반영"),
        ChecklistItem("설정 공유/백업", has_url_or_export, "URL 또는 JSON"),
    ]


def checklist_progress(items: list[ChecklistItem]) -> tuple[int, int]:
    done = sum(1 for item in items if item.done)
    return done, len(items)
