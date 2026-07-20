from __future__ import annotations

import importlib.util
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import AppConfig, MouseConfig, default_config_path, default_mouse_config_path


BOUNDARY_TEXT = (
    "This report improves local safety, reliability, and transparency. "
    "It does not claim the program is undetectable by other software."
)
REQUIRED_IMPORTS = {
    "PySide6": "GUI runtime",
    "PIL": "image loading",
    "mss": "screen capture",
    "pynput": "software drag input",
    "pyautogui": "cursor control",
    "serial": "hardware mouse serial transport",
}


@dataclass(frozen=True)
class SafetyFinding:
    category: str
    status: str
    message: str
    recommended_action: str


@dataclass(frozen=True)
class EffectivenessScore:
    category: str
    score: int
    maximum: int
    weight: int
    rationale: str


@dataclass(frozen=True)
class SafetyReport:
    findings: List[SafetyFinding]
    scores: List[EffectivenessScore]
    total: int
    maximum: int
    boundary: str = BOUNDARY_TEXT

    @property
    def has_failures(self) -> bool:
        return any(finding.status == "FAIL" for finding in self.findings)

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            "findings": [asdict(finding) for finding in self.findings],
            "scores": [asdict(score) for score in self.scores],
            "total": self.total,
            "maximum": self.maximum,
            "has_failures": self.has_failures,
            "boundary": self.boundary,
        }


def _read_json(path: Path) -> tuple[Optional[dict], bool, Optional[str]]:
    if not path.exists():
        return None, False, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data, True, None
        return None, True, "top-level JSON value must be an object"
    except Exception as exc:
        return None, True, str(exc)


def _load_app_config(path: Optional[Path] = None) -> tuple[AppConfig, Path, Optional[dict], bool, Optional[str]]:
    config_path = path or default_config_path()
    data, exists, error = _read_json(config_path)
    if error is not None or data is None:
        return AppConfig(), config_path, data, exists, error
    try:
        return AppConfig.from_json_dict(data), config_path, data, exists, None
    except Exception as exc:
        return AppConfig(), config_path, data, exists, str(exc)


def _load_mouse_config(path: Optional[Path] = None) -> tuple[MouseConfig, Path, Optional[dict], bool, Optional[str]]:
    config_path = path or default_mouse_config_path()
    data, exists, error = _read_json(config_path)
    if error is not None or data is None:
        return MouseConfig(), config_path, data, exists, error
    try:
        return MouseConfig.from_json_dict(data), config_path, data, exists, None
    except Exception as exc:
        return MouseConfig(), config_path, data, exists, str(exc)


def _status_penalty(status: str) -> int:
    return {"PASS": 0, "INFO": 0, "WARN": 1, "FAIL": 2}.get(status, 1)


def _bounded_score(maximum: int, base: int, penalties: int = 0) -> int:
    return max(0, min(maximum, int(base) - int(penalties)))


def _dependency_findings() -> List[SafetyFinding]:
    findings: List[SafetyFinding] = []
    for module, purpose in REQUIRED_IMPORTS.items():
        if importlib.util.find_spec(module) is None:
            findings.append(
                SafetyFinding(
                    "Runtime Dependencies",
                    "FAIL",
                    f"Missing dependency '{module}' required for {purpose}.",
                    "Install project dependencies with the project venv before running the GUI.",
                )
            )
        else:
            findings.append(
                SafetyFinding(
                    "Runtime Dependencies",
                    "PASS",
                    f"Dependency '{module}' is available for {purpose}.",
                    "No action required.",
                )
            )
    return findings


def _configured_hardware_port(cfg: AppConfig, mouse_data: Optional[dict]) -> Optional[str]:
    app_port = getattr(cfg, "hardware_mouse_port", None)
    if app_port:
        return str(app_port)
    if isinstance(mouse_data, dict):
        mouse_port = mouse_data.get("arduino_port")
        if mouse_port:
            return str(mouse_port)
    return None


def collect_safety_findings(
    app_config_path: Optional[Path] = None,
    mouse_config_path: Optional[Path] = None,
) -> tuple[List[SafetyFinding], AppConfig, MouseConfig]:
    cfg, cfg_path, cfg_data, cfg_exists, cfg_error = _load_app_config(app_config_path)
    mouse_cfg, mouse_path, mouse_data, mouse_exists, mouse_error = _load_mouse_config(mouse_config_path)
    findings: List[SafetyFinding] = []

    if cfg_error is not None:
        findings.append(SafetyFinding("Config Integrity", "FAIL", f"Could not parse app config {cfg_path}: {cfg_error}", "Fix config.json or restore a known-good copy before running."))
    elif cfg_exists:
        findings.append(SafetyFinding("Config Integrity", "PASS", f"Loaded app config: {cfg_path}", "No action required."))
    else:
        findings.append(SafetyFinding("Config Integrity", "WARN", f"App config not found at {cfg_path}; defaults will be used.", "Create/save config from the GUI before production painting."))

    if mouse_error is not None:
        findings.append(SafetyFinding("Config Integrity", "FAIL", f"Could not parse mouse config {mouse_path}: {mouse_error}", "Fix mouse_config.json or restore a known-good copy before using hardware input."))
    elif mouse_exists:
        findings.append(SafetyFinding("Config Integrity", "PASS", f"Loaded mouse config: {mouse_path}", "No action required."))
    else:
        findings.append(SafetyFinding("Config Integrity", "INFO", f"Mouse config not found at {mouse_path}; defaults will be used.", "Save mouse settings from the GUI if hardware input is needed."))

    findings.extend(_dependency_findings())

    hardware_enabled = bool(getattr(cfg, "use_hardware_mouse", False))
    hardware_port = _configured_hardware_port(cfg, mouse_data)
    if hardware_enabled and hardware_port:
        findings.append(SafetyFinding("Hardware Input", "WARN", f"Hardware mouse is enabled on {hardware_port}; live input requires operator consent.", "Confirm the game window is focused and you explicitly intend to move/click via HID before painting."))
    elif hardware_enabled:
        findings.append(SafetyFinding("Hardware Input", "FAIL", "Hardware mouse is enabled but no configured serial port was found.", "Set hardware_mouse_port in config.json or disable hardware mouse before painting."))
    else:
        findings.append(SafetyFinding("Hardware Input", "PASS", "Hardware mouse is disabled in saved config.", "No action required unless hardware input is intentionally needed."))

    profile = str(getattr(cfg, "delay_profile", "default")).lower()
    if profile not in {"fast", "default", "careful"}:
        findings.append(SafetyFinding("Input Pacing", "WARN", f"Unknown delay profile '{profile}'.", "Use one of fast, default, or careful."))
    elif bool(getattr(cfg, "use_advanced_delays", False)):
        findings.append(SafetyFinding("Input Pacing", "PASS", f"Human-like timing is enabled with profile '{profile}'.", "No action required."))
    else:
        findings.append(SafetyFinding("Input Pacing", "INFO", "Human-like timing is disabled unless enabled from UI or CLI.", "Enable --humanized or the GUI timing option when natural input pacing is desired."))

    if bool(getattr(cfg, "enable_position_jitter", False)):
        findings.append(SafetyFinding("Input Pacing", "PASS", "Position jitter is enabled for less repetitive software movement.", "No action required."))
    else:
        findings.append(SafetyFinding("Input Pacing", "INFO", "Position jitter is disabled. Pixel-accurate hardware strokes remain unchanged.", "Enable position jitter only if software movement can tolerate bounded offsets."))

    if bool(getattr(cfg, "enable_micro_pauses", True)):
        findings.append(SafetyFinding("Input Pacing", "PASS", "Micro-pauses are enabled.", "No action required."))
    else:
        findings.append(SafetyFinding("Input Pacing", "INFO", "Micro-pauses are disabled.", "Enable micro-pauses for less repetitive long sessions."))

    verify_rows = bool(getattr(cfg, "verify_rows", True))
    verify_max = int(getattr(cfg, "verify_max_passes", 0))
    if verify_rows and verify_max > 0:
        findings.append(SafetyFinding("Painting Reliability", "PASS", f"Row verification is enabled with max passes={verify_max}.", "No action required."))
    elif verify_rows:
        findings.append(SafetyFinding("Painting Reliability", "WARN", "Row verification is enabled but max passes is not positive.", "Set verify_max_passes to a positive number."))
    else:
        findings.append(SafetyFinding("Painting Reliability", "WARN", "Row verification is disabled, so missed cells may persist.", "Enable row verification for safer painting."))

    findings.append(SafetyFinding("Privacy/Transparency", "PASS", "Safety report is local-only and does not send network data.", "No action required."))
    findings.append(SafetyFinding("Privacy/Transparency", "PASS", "No stealth, debugger, VM, sandbox, DLL, or process-obfuscation checks are included.", "No action required."))
    return findings, cfg, mouse_cfg


def build_effectiveness_scores(findings: List[SafetyFinding], cfg: AppConfig) -> List[EffectivenessScore]:
    by_category: Dict[str, List[SafetyFinding]] = {}
    for finding in findings:
        by_category.setdefault(finding.category, []).append(finding)

    def penalties(category: str) -> int:
        return sum(_status_penalty(finding.status) for finding in by_category.get(category, []))

    humanized = bool(getattr(cfg, "use_advanced_delays", False))
    jitter = bool(getattr(cfg, "enable_position_jitter", False))
    micro = bool(getattr(cfg, "enable_micro_pauses", True))
    verify = bool(getattr(cfg, "verify_rows", True))

    return [
        EffectivenessScore("Config integrity", _bounded_score(5, 5, penalties("Config Integrity")), 5, 2, "JSON parseability and presence of app/mouse config."),
        EffectivenessScore("Runtime dependencies", _bounded_score(5, 5, penalties("Runtime Dependencies")), 5, 2, "Required Python modules are importable without starting the GUI."),
        EffectivenessScore("Hardware input safety", _bounded_score(5, 5, penalties("Hardware Input")), 5, 3, "Hardware mode is explicit and complete before any live input."),
        EffectivenessScore("Input naturalness", _bounded_score(5, 1 + int(humanized) + int(jitter) + int(micro) + int(verify), penalties("Input Pacing")), 5, 1, "Scores timing, jitter, micro-pauses, and verification settings."),
        EffectivenessScore("Painting reliability", _bounded_score(5, 4 + int(verify), penalties("Painting Reliability")), 5, 3, "Verification settings and bounded repair reduce missed-cell risk."),
        EffectivenessScore("Privacy/transparency", _bounded_score(5, 5, penalties("Privacy/Transparency")), 5, 2, "Local-only reporting with no stealth/evasion behavior."),
    ]


def build_safety_report(
    app_config_path: Optional[Path] = None,
    mouse_config_path: Optional[Path] = None,
) -> SafetyReport:
    findings, cfg, _mouse_cfg = collect_safety_findings(app_config_path, mouse_config_path)
    scores = build_effectiveness_scores(findings, cfg)
    total = sum(score.score * score.weight for score in scores)
    maximum = sum(score.maximum * score.weight for score in scores)
    return SafetyReport(findings=findings, scores=scores, total=total, maximum=maximum)


def render_safety_report(
    app_config_path: Optional[Path] = None,
    mouse_config_path: Optional[Path] = None,
) -> str:
    report = build_safety_report(app_config_path, mouse_config_path)
    warnings = [finding for finding in report.findings if finding.status in {"WARN", "FAIL"}]
    lines = [
        "Heartopia Auto Painter - Safety Report",
        "",
        "Purpose: improve local safety, reliability, and transparency. This is not an anti-detection or bypass report.",
        "",
        "Findings:",
    ]
    lines.extend(
        f"- [{finding.status}] {finding.category}: {finding.message} Action: {finding.recommended_action}"
        for finding in report.findings
    )
    lines.extend(["", "Effectiveness Assessment:"])
    lines.extend(
        f"- {score.category}: {score.score}/{score.maximum} (weight {score.weight}) - {score.rationale}"
        for score in report.scores
    )
    lines.extend(["", "Warnings/Failures:"])
    if warnings:
        lines.extend(f"- [{finding.status}] {finding.category}: {finding.recommended_action}" for finding in warnings)
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            f"Overall weighted defensive effectiveness: {report.total}/{report.maximum}",
            "",
            f"Boundary: {report.boundary}",
        ]
    )
    return "\n".join(lines)


def render_safety_report_json(
    app_config_path: Optional[Path] = None,
    mouse_config_path: Optional[Path] = None,
) -> str:
    report = build_safety_report(app_config_path, mouse_config_path)
    return json.dumps(report.to_json_dict(), indent=2, sort_keys=True)
