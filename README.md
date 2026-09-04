# GitHub Achievement Lab

一個小型、可驗證的 GitHub 工作流實驗場：用真實的 issue、pull request、review 與開源貢獻，記錄 GitHub profile achievements 的進度。

## 原則

- 只記錄 GitHub profile 或事件頁能驗證的成就，不把推測當成已解鎖。
- 每個變更都要對專案本身有用途：文件、測試、工具或維護改善。
- 尊重其他維護者的貢獻流程；外部 repo 先取得共識，再開始工作。
- 不灌水、不製造無意義的 issue/PR、不操弄 star 或 reaction。

## 專案內容

- [`achievements.yml`](achievements.yml)：成就狀態與證據索引。
- [`scripts/validate_tracker.py`](scripts/validate_tracker.py)：不需第三方套件的追蹤檔驗證器。
- [`CONTRIBUTING.md`](CONTRIBUTING.md)：貢獻與驗證規則。
- [`docs/achievement-rules.md`](docs/achievement-rules.md)：目前採用的判定邊界與倫理守則。

## 本機檢查

```powershell
python scripts/validate_tracker.py
python scripts/validate_tracker.py --summary
python scripts/validate_tracker.py --json
```

GitHub Actions 會在每次 push 與 pull request 自動執行相同檢查。

## 狀態

詳細進度放在 [`achievements.yml`](achievements.yml)。成就只有在 GitHub profile 顯示後才會標記為 `earned`；延遲中的事件會保留 PR、CI 與查核日期，但維持 `pending`。
