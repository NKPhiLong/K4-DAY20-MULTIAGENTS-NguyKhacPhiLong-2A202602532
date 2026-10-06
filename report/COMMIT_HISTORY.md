# Ghi chú lịch sử commit (cho người chấm)

Lịch sử có **hai chuỗi commit cùng đánh số "part 2-5"**. Lý do: bài có hai bộ hướng dẫn. Chuỗi đầu cài phần bắt buộc của lab Deep Agents (`GUIDE.md`, `RUBRIC.md`). Chuỗi sau cài hệ đa tác tử coordinator–workers theo các hướng dẫn bổ sung (Phần 0–6). Lịch sử đã push và tag `freeze` phụ thuộc vào thời điểm commit (`scripts/verify_freeze.py` so thời điểm tag với `timestamp` của các lần chạy), nên mình **không viết lại lịch sử** (rebase hay force push). Bảng dưới ánh xạ từng commit vào phần tương ứng.

| Commit | Thông điệp | Thuộc về | Nội dung |
|---|---|---|---|
| `a88ecff` | part 0: setup and Deep Agents tour answers | Cả hai (Phần 0) | Cài đặt, trả lời 3 câu làm quen (mục 3 `REPORT.md`) |
| `8f45990` | part 2: coordinator (main Deep Agent ...) | **Lab** - GUIDE Phần 1.2 | `src/lab/agent.py`: `make_backend`, `build_agent` |
| `6a8567a` | part 3: worker subagents ... | **Lab** - GUIDE Phần 1.1 | `src/lab/subagents.py`: explorer, implementer, reviewer |
| `3439741` | part 4: tools integration via runner ... | **Lab** - GUIDE Phần 1.3 | `src/lab/runner.py`: `run_task` |
| `5b0e3c3` | part 5: curator (self-evolving skills) ... | **Lab** - GUIDE Phần 3.1 | `src/lab/curator.py`: `curate_skills` |
| `474ce75` | part 1: multi-agent architecture design | **Hệ đa tác tử** - Phần 1 | Kiến trúc, sơ đồ, giao thức (`report/MULTIAGENT_REPORT.md`) |
| `01be675` | part 2: coordinator implementation | **Hệ đa tác tử** - Phần 2 | `src/coordinator.py`, test và script standalone |
| `e889814` | part 3: workers and communication | **Hệ đa tác tử** - Phần 3 | `src/agents/`, `src/communication/` |
| `fb8a132` | part 4: tools integration | **Hệ đa tác tử** - Phần 4 | `src/tools/` |
| `c1a03ca` | part 5: testing and benchmarking | **Hệ đa tác tử** - Phần 5 | `tests_mas/`, `scripts_mas/`, benchmark v1 |
| `cf2db93` | lab parts 2-3: learning runs ... | **Lab** - GUIDE Phần 2-3 | Kết quả tác vụ học, 3 lần chạy curator, skill |
| `a28f8db` | hypotheses: H1-H3 ... | **Lab** - GUIDE Phần 4.0 | Giả thuyết (trước tag) |
| `660c53e` | freeze skills (tag `freeze`) | **Lab** - GUIDE Phần 4.1 | Đóng băng skill |
| `36356a3` | part 6: final report ... | Cả hai - Phần 6 / GUIDE Phần 4.2-5 | Kết quả tác vụ đánh giá, `table.md`, hai báo cáo |
| (sau đó) | part 6 follow-up ... | **Hệ đa tác tử** | Tối ưu v2, độ phủ test, benchmark 3 lượt, kiểm chứng lỗi với API thật |
