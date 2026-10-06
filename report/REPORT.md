# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Nguy Khắc Phi Long
- Mã sinh viên: 2A202602532

- Nhà cung cấp và mô hình: OpenAI, `LAB_MODEL=openai:gpt-4.1-mini`; `LAB_TEMPERATURE=0`; `recursion_limit=60` (mặc định của runner)
- Deep Agents 0.7.21, Python 3.11.16, macOS (Darwin 23.1.0), chạy trực tiếp (không dùng Docker)
- Số lần chạy tác vụ đã dùng / ngân sách: (điền sau Phần 4) / 30
- Commit của tag `freeze`: (điền sau Phần 4)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): subagents KHÔNG cao hơn baseline trên tác vụ đánh giá (dự đoán điểm trung bình thấp hơn hoặc bằng, không cải thiện check `rule_`). Căn cứ: trên tác vụ học, subagents đạt 8/18 check kỹ thuật so với 13/18 của baseline. Tác tử chính không gọi subagent tự định nghĩa nào; nó giao toàn bộ việc cho `general-purpose` ở data-learn và logs-learn rồi dùng nguyên báo cáo mà không kiểm tra (data-learn 0/8, trong khi baseline đúng cả 5 số). Cô lập ngữ cảnh làm mất thông tin, và Anthropic ghi nhận hệ đa tác tử tốn khoảng 15 lần token, hiệu quả chủ yếu ở việc song song hóa, không phải ở tác vụ tuần tự nhỏ như ở đây.
- H2 (skills-auto so với baseline): skills-auto xấp xỉ baseline trên tác vụ đánh giá (chênh lệch điểm trung bình trong khoảng nhiễu, khoảng ±0,15), check `rule_` gần như không cải thiện. Căn cứ: ở Phần 3.4, `skills_read = 0` trên cả 3 tác vụ học, tức là mô hình không đọc skill dù có `SKILLS_NOTE`, nên skill không thể có tác dụng. Thêm vào đó, skill data và logs thiếu giá trị quy ước cụ thể (khối `meta`, `clean.csv`, `schema_version`). SkillsBench ghi nhận skill do mô hình tự sinh trung bình không có lợi; SkillEvolBench ghi nhận lợi ích trên tác vụ học không chuyển sang tác vụ mới.
- H3 (tác vụ học so với tác vụ đánh giá): ở mọi điều kiện, điểm tác vụ đánh giá thấp hơn hoặc bằng tác vụ học, vì mỗi tác vụ đánh giá có thêm một quy ước mới không học được và `detail` rỗng. Mọi chênh lệch giữa các điều kiện trên tác vụ học không phải bằng chứng của "học": cùng cấu hình mà logs-learn đi từ 1/9 (baseline) lên 6/9 (skills-auto ở Phần 3.4, không đọc skill nào) chỉ vì mô hình đổi cách làm (tự viết script thay vì chép tay). Vì vậy dự đoán chênh lệch trên tác vụ đánh giá nhỏ hơn mức nhiễu một lần chạy.

## 3. Làm quen Deep Agents (Phần 0.3)

Nguồn: `python scripts/tour.py` (mô hình giả, không tốn token), Deep Agents 0.7.21.

1. **Công cụ và số tác tử.** Tác tử mặc định được cấp 9 công cụ: công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; shell `execute`; và `task` để giao việc cho subagent. Công cụ **chạy lệnh** là `execute` (shell thật, thư mục làm việc là gốc sandbox). Về số tác tử: ở điều kiện `baseline` có 1 tác tử chính (đóng vai trò điều phối, *coordinator*) và 1 subagent mặc định `general-purpose`. Ở điều kiện `subagents` có thêm 3 tác tử con (*worker*) tự định nghĩa trong `src/lab/subagents.py`: `explorer` (chỉ đọc đặc tả, dữ liệu và báo cáo sự thật), `implementer` (sửa mã hoặc viết script, chạy test) và `reviewer` (kiểm tra độc lập theo từng quy tắc, không sửa tệp).
2. **Giao tiếp coordinator → worker.** Tác tử chính gọi công cụ `task(description, subagent_type)`. Mô tả công cụ `task` giới thiệu `general-purpose` là tác tử cho "researching complex questions, searching for files and content, and executing multi-step tasks", có cùng bộ công cụ với tác tử chính. Subagent **không** thấy hội thoại của tác tử chính: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report." Như vậy kênh giao tiếp duy nhất là prompt giao việc (đi) và một báo cáo cuối (về, dưới dạng `ToolMessage`). Tác tử chính phải tự kiểm tra báo cáo rồi mới dùng. Không có message queue hay trạng thái chung nào ngoài hệ thống tệp.
3. **Công cụ dùng chung và câu hướng dẫn hành vi.** System prompt mặc định rỗng (`''`), nên hành vi được định hướng qua mô tả công cụ. Mọi tác tử (chính và con) dùng chung một backend `LocalShellBackend`, tức là chung bộ công cụ tệp, shell và chung thư mục sandbox. Hệ thống tệp chính là "trạng thái dùng chung" giữa các tác tử. Câu trích từ `task`: "Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls." Câu trích từ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

Nguồn: `results/baseline/*-learn/run.json` và `trace.md` (baseline, 3 tác vụ học, 14 check thất bại).

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | "RULE: every public function ... has type annotations on all parameters and on the return value" |
| code-learn | `rule_regression_tests` | E | "RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3)" |
| code-learn | `rule_changelog` | E | "RULE: record each fix in CHANGELOG.md under the heading '## Unreleased'" |
| data-learn | `rule_money_in_cents` | E | "RULE: money values in answer.json are integer cents" |
| data-learn | `rule_meta_block` | E | "RULE: answer.json has an object `meta` = {source, rows_in, rows_used}" |
| data-learn | `rule_clean_csv` | E | "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents" |
| logs-learn | `timestamps_utc` | D | detail "7/25 timestamps match". Vết: dòng `2024-04-30T22:06:40-05:00 [ERROR]` được ghi thành `"2024-04-30T22:06:40Z"` (bỏ qua offset) |
| logs-learn | `entry_count` | B | detail "wrong number of entries (got 19)". Vết: 0 lệnh `execute`; tác tử đọc log bằng `read_file` rồi tự viết toàn bộ `errors.json` bằng một lệnh `write_file`, không chạy script, không đếm lại |
| logs-learn | `exception_fields` | B | detail "18 wrong `exception` values": giá trị chép tay từ ngữ cảnh, không kiểm chứng |
| logs-learn | `repeat_counts` | B | detail "18 wrong `repeat_count` values", cùng nguyên nhân |
| logs-learn | `counts_by_service` | B | detail "counts_by_service: wrong values", hệ quả của hai lỗi trên |
| logs-learn | `rule_service_names` | E | "RULE: service names ... lower-case with '-' replaced by '_'" |
| logs-learn | `rule_sorted_errors` | E | "RULE: `errors` is sorted by service, then by timestamp_utc, ascending" |
| logs-learn | `rule_schema_header` | E | "RULE: the top-level object has \"schema_version\": 2 and \"generated_by\": \"log-triage\"" |

Nhận xét:

- **Nhóm đa số là E (9/14 check thất bại):** 100% check quy ước đều trượt (0/9 theo `scripts/check_breakdown.py`). Đây là tri thức chỉ có trong phản hồi `detail`, đề bài không nêu, nên skill **có thể** phòng ngừa nếu skill chép đúng giá trị quy ước và tác tử đọc skill.
- **Bằng chứng phủ định cho A, C:** check kỹ thuật của baseline đạt 13/18. code-learn đạt toàn bộ 7/7 check kỹ thuật, kể cả các check chỉ thấy qua docstring (`low_stock_follows_docstring`, `csv_quoting_follows_docstring`, nên không thuộc nhóm A) và lỗi ở hàm dùng chung (`other_caller_fixed`, nên không thuộc nhóm C). data-learn đạt 5/5 check kỹ thuật (xử lý trùng lặp, giá trị thiếu, múi giờ đúng, nên không thuộc nhóm D).
- **Lỗi kỹ thuật tập trung ở logs-learn (5 check, nhóm B và D)** với nguyên nhân chung là *không viết và chạy script* (0 lệnh `execute`). Tác tử "tính bằng đầu" trên 156 dòng log, nên vừa sai offset múi giờ vừa sai số đếm.
- **Không xếp vào F:** câu trả lời cuối nói "converted timestamps to UTC... accounted for repeated messages" là mô tả sai về chất lượng, nhưng tệp `errors.json` có thật.
- **Skill phòng ngừa được nhóm B:** quy trình "luôn viết script, chạy, đối chiếu đầu ra" là thủ tục tổng quát.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa** (`src/lab/subagents.py`), theo mô hình explorer → implementer → reviewer, tách đọc, làm và kiểm tra:
  - `explorer`: chỉ đọc README, docstring, tệp quy ước và mẫu dữ liệu, rồi báo cáo sự thật kèm trích dẫn; không sửa gì. Mục đích: chống nhóm A.
  - `implementer`: sửa nguyên nhân gốc, ưu tiên viết và chạy script, báo cáo đúng các tệp đã đổi. Mục đích: chống nhóm C và F.
  - `reviewer`: kiểm tra độc lập từng quy tắc (PASS/FAIL kèm bằng chứng); không sửa gì. Mục đích: chống nhóm B.
  - `description` mỗi subagent nêu rõ khi nào gọi (BEFORE, to make the change, AFTER).
- **`subagent_calls` ở từng tác vụ:** code-learn 0, data-learn 1, logs-learn 1. Cả hai lần gọi đều là `subagent_type: "general-purpose"` (grep trong `trace.md`); 3 subagent tự định nghĩa **không được gọi lần nào**. Ở code-learn, tác tử chính tự làm (12 tool call) và đạt 7/10, bằng baseline. Khả năng cao là mô hình chọn `general-purpose` vì mô tả của nó ("has access to all tools as the main agent") khớp với "làm cả việc", còn 3 vai trò của mình đòi hỏi chia nhỏ việc mà tác tử chính không chủ động làm.
- **Thông tin truyền đi:** lời giao việc ở data-learn **đủ thông tin của đề**: chép đủ 5 khóa, quy tắc "missing amount", và liệt kê `workspace/sales.csv`, `workspace/answer.json`, `workspace/README.md (for column descriptions)`. Không thể truyền quy ước Acme vì tác tử chính cũng không biết chúng. Vấn đề nằm ở chiều về: tác tử chính **không kiểm tra** báo cáo trả về, dù `SUBAGENTS_NOTE` yêu cầu "Check what a subagent returns": nó chép nguyên 5 con số của subagent (`north_q1_revenue` 3165.49, `top_region` "east" chữ thường, ...) vào câu trả lời cuối, và cả 5 đều sai (0/8, so với baseline 5/5 check kỹ thuật). logs-learn: subagent chỉ ghi 2 mục (detail "got 2"), so với 19 mục của baseline.
- **Token và thời gian:** token trung bình trên tác vụ học là 34 456 (subagents) so với 40 318 (baseline). Số token không tăng vì mỗi lần giao việc chỉ có một subagent và tác tử chính hầu như không làm gì thêm. Tuy vậy data-learn chậm gần gấp đôi (49,8 s so với 26,6 s) với số token tương đương (46 351 so với 45 089), điểm tụt từ 0,625 xuống 0. Đa tác tử ở đây không đáng chi phí: cùng hoặc nhiều token hơn mà chất lượng thấp hơn.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator: 3** (1 lần đầu + 2 lần chạy lại, mức tối đa cho phép). Mỗi lần chạy lại thì xóa toàn bộ skill cũ khỏi `skills/auto/`; bản cũ lưu ở `report/curator_runs/run1/` và `run2/` để đối chiếu. Không sửa tay nội dung skill nào.
  - **Lần 1 → xóa 3 skill:** skill data viết quy ước thành ví dụ mềm ("e.g., integer cents ... as required by conventions"), mất tên khóa `meta` (`source`, `rows_in`, `rows_used`), mất tên tệp `clean.csv` và header. Skill logs nói "schema_version and generated_by" mà thiếu giá trị `2` / `"log-triage"`. Không skill nào nêu bài học quy trình lớn nhất của vết (logs-learn: 0 lệnh `execute`). Mình sửa prompt của curator (mã trong `curate_skills`, không phải nội dung skill): yêu cầu chép **nguyên văn** giá trị quy ước (GUIDE cho phép tên và giá trị do quy ước Acme yêu cầu) và rút bài học quy trình từ vết.
  - **Lần 2 → xóa 2 skill:** curator sinh 3 skill, nhưng skill quy ước `enforce-organisation-conventions` bị `validate_skill` từ chối vì chứa marker của tác vụ đánh giá ("mentions evaluation material: orders"). Từ này nằm ngay trong RULE của data-learn ("distinct orders with a known amount"), nên đây là dương tính giả của bộ lọc. Hai skill còn lại thiếu toàn bộ quy ước data và logs. Mình **không** lách bộ lọc (đó là hành vi mục 6c cảnh báo), chỉ yêu cầu curator viết mỗi loại tác vụ một skill để một skill bị loại không làm mất các quy ước khác (`max_skills=4`).
  - **Lần 3: giữ 3 skill** dưới đây (đã hết lượt chạy lại).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `code-package-fixes-and-tests` | Tổng quát cho mọi gói Python cần sửa lỗi. Chỉ chứa tên do quy ước yêu cầu (`tests/test_regressions.py`, `CHANGELOG.md`, `## Unreleased`, `- fix(<function name>): ...`) | Đúng và đủ cả 3 quy ước (type hints; ≥3 test, một test mỗi lỗi; changelog). Thêm bài học hữu ích "run tests with PYTHONPATH set". Bước 1 "read all RULE comments verbatim" vô dụng vì lúc chạy không có RULE nào để đọc | 20 dòng; description "Use when fixing bugs and improving a Python code package..." nêu đúng tình huống; `skills_read=0` |
| `data-cleaning-and-aggregation` | Phần lớn tổng quát. Có một chi tiết riêng của tác vụ học: "unique key (e.g., order_id)" (tên cột của workspace) | **Thiếu và mềm hóa quy ước**: không có khối `meta` và các khóa của nó, không có tên `clean.csv` và header, tiền cent chỉ là "if required". "convert to UTC naive" có thể gây hại vì quy ước yêu cầu hậu tố `Z`. Có bài học quy trình đúng ("Run the full pipeline and verify") | 20 dòng; description rộng, hợp lý; `skills_read=0` |
| `log-file-parsing-and-normalization` | Tổng quát cho tác vụ parse log | Đúng quy ước tên service (`-` → `_`, chữ thường) và thứ tự sắp xếp; **thiếu giá trị** `schema_version: 2`, `generated_by: "log-triage"`. Bước 7 lặp lại bước 1. Không nói rõ "viết script" dù đó là lỗi chính của vết | 25 dòng; description đúng tình huống; `skills_read=0` |

**`skills_read = 0` trên cả 3 tác vụ học ở Phần 3.4** (`results/skills-auto-dev/`). Mình kiểm tra harness bằng mô hình giả: 3 skill có trong system prompt (mục "Available Skills" kèm đường dẫn `/skills/<name>/SKILL.md`), cùng `SKILLS_NOTE` ("As your FIRST action, read the SKILL.md ..."); `skills_sha256` khớp `hash_skills(skills/auto)`. Vậy lỗi không nằm ở harness hay `description` mà ở hành vi của `gpt-4.1-mini`: bước đầu của cả 3 vết là `read_file /workspace/README.md`. Điểm 3.4: code 7/10, data 5/8, logs 6/9 (cùng các check `rule_` trượt như baseline). logs-learn tăng từ 1/9 lên 6/9 **không nhờ skill**: lần này mô hình tự viết script Python (1 lệnh `execute`). Đây là ước lượng đầu tiên về nhiễu giữa hai lần chạy cùng mô hình.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Bạn đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
