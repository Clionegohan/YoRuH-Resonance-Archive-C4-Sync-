---
id: "002-02-07"
title: "マルチレベル検索統合"
status: "completed"
---

# Subtask: マルチレベル検索統合

## Acceptance Criteria

- [x] **THE SYSTEM SHALL** ResultIntegratorクラスを提供すること

- [x] **THE SYSTEM SHALL** integrate()メソッドで検索結果を統合すること
  - level1_results（List[Dict]）とlevel2_results（List[Dict]）を入力として受け取る
  - 両方の結果リストを結合する
  - 距離（distance）でソート（昇順）
  - 同じidが複数ある場合、最も小さい距離を持つものを採用
  - 上位3件を返す

- [x] **THE SYSTEM SHALL** 入力リストがNoneまたは空の場合でも正しく処理すること
  - 両方が空の場合は空リストを返す
  - 一方のみ空の場合は、もう一方から上位3件を返す

- [x] **THE SYSTEM SHALL** 結果が3件未満の場合、存在する全件を返すこと

- [x] **THE SYSTEM SHALL** 各結果にid, distance, metadataフィールドを含むこと
