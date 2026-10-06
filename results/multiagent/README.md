# results/multiagent - kết quả của hệ đa tác tử coordinator–workers

Kết quả của phần hướng dẫn bổ sung (Phần 1–6), tách khỏi kết quả thí nghiệm lab (`results/<điều kiện>/`).
`lab.compare`, `scripts/check_breakdown.py` và `scripts/verify_freeze.py` không đọc thư mục này.

| Tệp | Nội dung | Tạo bởi |
|---|---|---|
| `../../benchmark_results.json` | Benchmark **v3 (hiện tại)**, 27 request + 10 đồng thời. Để ở gốc repo theo đúng đường dẫn của hướng dẫn Phần 5 | `python scripts_mas/benchmark.py --iterations 3 --rounds 3 --concurrency 10` |
| `benchmark_results_v1.json` | Benchmark v1 (trước tối ưu, 1 lượt, 9 request) | như trên, bản mã v1 |
| `benchmark_results_v2.json` | Benchmark v2 (Evaluator một lượt, tool SVG, cắt bàn giao) | như trên, bản mã v2 |
| `resilience_results.json` | Kiểm chứng xử lý lỗi với API thật: 401 → retry → fallback, timeout, yêu cầu phá hoại | `python scripts_mas/test_resilience_real.py` |
| `profile_real.txt` | cProfile 5 request với mô hình thật (đo trên bản v2) | `python scripts_mas/profile_system.py --real` |
| `logs/*.log` | Bản chụp log JSON-lines (`coordinator`, `communication`, `data_agent`, `code_agent`, `evaluator_agent`, `tools`, ...) của các lần chạy benchmark, kiểm chứng, profile; báo cáo dẫn chứng từ đây. Đã kiểm tra không chứa khóa API hay đường dẫn tuyệt đối | `src/logger.py` (thư mục `logs/` gốc bị gitignore) |
