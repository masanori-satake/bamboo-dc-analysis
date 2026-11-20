# Maintaining — 正本1つ、チェックアウトで即利用、両対応を維持する

## リポジトリの構成

このリポジトリは、チェックアウトした途端にスキルが使える構成にします。

- 正本: `.agents/skills/bamboo-dc-analysis/`（SKILL.md、references/、scripts/、tests/）
- ミラー: `.kiro/skills/bamboo-dc-analysis/`（正本とバイト同一）
- リポジトリ直下: README、CHANGELOG、LICENSE、本書、`tools/sync_mirror.py`

Copilot は `.agents/skills/` をそのまま発見し、Kiro は `.kiro/skills/` を発見します。チェックアウトを開けば、どちらのツールでも配置作業なしでスキルが有効になります。

## 編集のルール

- 編集するのは正本だけです。ミラーを直接編集しません。
- 正本を編集したら、コミット前に必ず次を実行します。

```bash
python tools/sync_mirror.py
python tools/sync_mirror.py --check
```

`sync_mirror.py` は正本からミラーを再生成し、`--check` はファイル集合と SHA-256 で同一性を検証します（ずれがあれば該当ファイルを示して終了コード 1）。

## 他のワークスペースへ入れるとき

このリポジトリ以外のワークスペースで使う場合は、正本フォルダをそのワークスペースの `.agents/skills/` に置き、正本同梱のインストーラで Kiro 向けの配置を作ります。

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace .
```

- 既定はリンク方式（Windows はジャンクション、POSIX はシンボリックリンク）で、実体は正本1つです。更新は正本の入れ替えだけで追随します。
- リンクが使えない環境では `--mode copy` を使い、`install.py --check` で同一性を検証します。
- 「同じ動き」の担保は、同一性検証に加えてフィクスチャテストです。任意の配置先を指定して実行できます: `BAMBOO_SKILL_DIR=<配置先> python tests/test_bamboo.py`（tests は正本フォルダ内にあります）。

## リリース手順

1. 正本だけを編集する。
2. `python tools/sync_mirror.py` でミラーを再生成し、`--check` で同一性を確認する。
3. 正本とミラーの両方でフィクスチャテストを実行する（`BAMBOO_SKILL_DIR` にそれぞれのパスを指定）。
4. `SKILL.md` の `metadata.version` を上げ、`CHANGELOG.md` に英語→日本語で記録する。版を上げたら手順 2 をやり直す（版マーカーも同期対象のため）。
5. コミットして GitHub に push する。
6. 利用側は、このリポジトリを pull するだけです。チェックアウト構成のため、追加の配置作業はありません。

## やらないこと

- ミラーや配置先の中身を直接編集しない。直したいときは正本を直して再生成・再配置する。
- 版を上げる際、SKILL.md のメタデータと CHANGELOG のどちらか片方だけを更新しない。
