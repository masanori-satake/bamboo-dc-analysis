# Changelog

## 1.2.0 — 2026-11-20

- Restructured the repository so a plain checkout works immediately: the canonical skill now lives at `.agents/skills/bamboo-dc-analysis/` (Copilot discovers it as-is), with a byte-identical mirror at `.kiro/skills/bamboo-dc-analysis/` (Kiro's discovery location). No install step is needed to use the skill in a checkout of this repository.
- Added `tools/sync_mirror.py` to regenerate the mirror from the canonical and to verify parity (`--check`, file set + SHA-256). The mirror is never edited by hand.

- リポジトリをチェックアウトした途端に使える構成へ再編。正本は `.agents/skills/bamboo-dc-analysis/`（Copilot がそのまま発見する）に置き、Kiro の発見先である `.kiro/skills/bamboo-dc-analysis/` にはバイト同一のミラーを配置。このリポジトリのチェックアウトでは、配置作業なしでスキルが使える。
- `tools/sync_mirror.py` を追加。正本からミラーを再生成し、`--check` で同一性（ファイル集合＋SHA-256）を検証する。ミラーは手で編集しない。

## 1.1.0 — 2026-11-20

- Added `scripts/install.py`: installs the skill from one canonical copy (`.agents/skills/`) into Kiro's location as a directory link (Windows junction / POSIX symlink), with a copy mode fallback and a `--check` parity verification (file set + SHA-256). Copilot reads the canonical `.agents/skills/` directly, so both tools always work from the same content.
- Added the fixture test suite under `tests/`, runnable against any installed location via `BAMBOO_SKILL_DIR`, so "same behaviour in both environments" is verified, not assumed.
- Added `MAINTAINING.md` with the single-canonical release procedure, and a version marker in the SKILL.md metadata.

- `scripts/install.py` を追加。正本（`.agents/skills/`）から Kiro の配置先へディレクトリリンク（Windows はジャンクション、POSIX はシンボリックリンク）で配置し、コピー方式への切替と `--check` による同一性検証（ファイル集合＋SHA-256）も備える。Copilot は正本の `.agents/skills/` を直接読むため、両ツールが常に同じ内容で動く。
- `tests/` にフィクスチャテストを同梱。`BAMBOO_SKILL_DIR` で任意の配置先を指定して実行でき、「両環境で同じ動き」を前提でなく検証で担保する。
- リリース手順を定めた `MAINTAINING.md` と、SKILL.md メタデータへの版マーカーを追加。

## 1.0.0 — 2026-11-20

- Initial release: read-only investigation and analysis of Bamboo Data Center 12.1 over its REST API — inventory, snapshot, history analysis, per-plan dossiers, and task/trigger investigation via Bamboo Specs, with the `scripts/bamboo.py` helper (standard library only).

- 初版。Bamboo Data Center 12.1 を REST API で読み取り専用に調査・分析するスキル。台帳、状況把握、履歴分析、プラン単位のドシエ、Specs 経由のタスク／トリガー調査と、標準ライブラリのみのヘルパー `scripts/bamboo.py` を収録。
