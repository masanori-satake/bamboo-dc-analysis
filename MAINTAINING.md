# Maintaining — 正本1つで Copilot と Kiro の両対応を維持する

このスキルの保守ルールは1つだけです。**編集するのは正本だけ**。正本はこのリポジトリであり、各ワークスペースでは `.agents/skills/bamboo-dc-analysis/` に置いた clone がそれにあたります。

## なぜコピーが要らないか

- **GitHub Copilot** は `.agents/skills/` をプロジェクトスキルの配置先として直接読みます（他に `.github/skills/`、`.claude/skills/`）。正本をそのまま読むので、Copilot 向けのコピーは存在しません。
- **Kiro** は `.kiro/skills/` しか読まないため、そこにはコピーではなく **ディレクトリリンク**（Windows はジャンクション、POSIX はシンボリックリンク）を置きます。リンクは実体が1つなので、正本を直せば Kiro 側も即座に同じ内容になり、ずれようがありません。
- リンクが使えない環境（リンク先の実体ではなくファイルそのものをコミットする必要があるツリー等）では、コピー方式に切り替えます。その代わり、コピーの同一性は感覚でなく検証で担保します（後述）。

## 配置

ワークスペースのルートで、正本の clone を置いたあとに1回だけ実行します。

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace .
```

- 既定はリンク方式。コピー方式にする場合は `--mode copy`。
- `.github/skills/` にも置きたい場合は `--with-github`（Copilot には不要です）。
- 既存の配置が正本と食い違う場合、スクリプトは上書きを拒否します。意図した置き換えのときだけ `--force` を付けます。

## 同一性の検証

```bash
python .agents/skills/bamboo-dc-analysis/scripts/install.py --workspace . --check
```

配置先ごとに、正本とのファイル集合と SHA-256 を比較します。リンクは「正本へのリンクであること」自体を合格とし、コピーはバイト同一を合格とします。ずれがあれば該当ファイルを示して終了コード 1 を返します。

「同じ動き」の担保は、この同一性検証に加えてフィクスチャテストです。任意の配置先を指定して同じテストを実行できます。

```bash
BAMBOO_SKILL_DIR=<配置先のパス> python tests/test_bamboo.py
```

## リリース手順

1. 正本だけを編集する。
2. `python tests/test_bamboo.py` を正本で実行し、全件合格を確認する。
3. サンドボックスのワークスペースで `install.py` のリンク方式とコピー方式の両方を試し、`--check` が合格すること、コピー側にわざと差分を作ると `--check` が検出することを確認する。
4. `SKILL.md` の `metadata.version` を上げ、`CHANGELOG.md` に英語→日本語で記録する。
5. コミットしてタグ（`vX.Y.Z`）を付け、GitHub に push する。
6. 利用側の各マシンでは、正本の clone を `git pull` するだけです。リンク方式なら Kiro 側は自動で追随します。コピー方式の配置がある場合は `install.py` を再実行し、`--check` で締めます。

## やらないこと

- 配置先（`.kiro/skills/` や `.github/skills/` の中身）を直接編集しない。直したいときは正本を直して再配置する。
- 版を上げる際、SKILL.md のメタデータと CHANGELOG のどちらか片方だけを更新しない。
