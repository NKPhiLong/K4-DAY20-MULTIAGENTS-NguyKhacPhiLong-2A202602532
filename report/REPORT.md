# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin sinh viên và cấu hình

- Họ tên: Nguy Khắc Phi Long
- Mã sinh viên: 2A202602532

- Nhà cung cấp và mô hình: OpenAI, `LAB_MODEL=openai:gpt-4.1-mini`; `LAB_TEMPERATURE=0`; `recursion_limit=60` (mặc định của runner)
- Deep Agents 0.7.21, Python 3.11.16, macOS (Darwin 23.1.0), chạy trực tiếp (không dùng Docker)
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / 30 (baseline 6, subagents 6, skills-auto 3 ở Phần 3.4 + 6 sau đóng băng; không lần nào phải chạy lại vì lỗi). Ngoài ra curator gọi mô hình 3 lần.
- Commit của tag `freeze`: `660c53e` (commit `hypotheses` là `a28f8db`); `python scripts/verify_freeze.py` → `checked 6 runs of skill conditions: OK`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): subagents KHÔNG cao hơn baseline trên tác vụ đánh giá (dự đoán điểm trung bình thấp hơn hoặc bằng, không cải thiện check `rule_`). Căn cứ: trên tác vụ học, subagents đạt 8/18 check kỹ thuật so với 13/18 của baseline. Tác tử chính không gọi subagent tự định nghĩa nào; nó giao toàn bộ việc cho `general-purpose` ở data-learn và logs-learn rồi dùng nguyên báo cáo mà không kiểm tra (data-learn 0/8, trong khi baseline đúng cả 5 số). Cô lập ngữ cảnh làm mất thông tin, và Anthropic ghi nhận hệ đa tác tử tốn khoảng 15 lần token, hiệu quả chủ yếu ở việc song song hóa, không phải ở tác vụ tuần tự nhỏ như ở đây.
- H2 (skills-auto so với baseline): skills-auto xấp xỉ baseline trên tác vụ đánh giá (chênh lệch điểm trung bình trong khoảng nhiễu, khoảng ±0,15), check `rule_` gần như không cải thiện. Căn cứ: ở Phần 3.4, `skills_read = 0` trên cả 3 tác vụ học, tức là mô hình không đọc skill dù có `SKILLS_NOTE`, nên skill không thể có tác dụng. Thêm vào đó, skill data và logs thiếu giá trị quy ước cụ thể (khối `meta`, `clean.csv`, `schema_version`). SkillsBench ghi nhận skill do mô hình tự sinh trung bình không có lợi; SkillEvolBench ghi nhận lợi ích trên tác vụ học không chuyển sang tác vụ mới.
- H3 (tác vụ học so với tác vụ đánh giá): ở mọi điều kiện, điểm tác vụ đánh giá thấp hơn hoặc bằng tác vụ học, vì mỗi tác vụ đánh giá có thêm một quy ước mới không học được và `detail` rỗng. Mọi chênh lệch giữa các điều kiện trên tác vụ học không phải bằng chứng của "học": cùng cấu hình mà logs-learn đi từ 1/9 (baseline) lên 6/9 (skills-auto ở Phần 3.4, không đọc skill nào) chỉ vì mô hình đổi cách làm (tự viết script thay vì chép tay). Vì vậy dự đoán chênh lệch trên tác vụ đánh giá nhỏ hơn mức nhiễu một lần chạy.

## 3. Làm quen Deep Agents (Phần 0.3)

Nguồn: `python scripts/tour.py` (mô hình giả, không tốn token), Deep Agents 0.7.21.

1. **Công cụ và số tác tử.** Tác tử mặc định được cấp 9 công cụ: công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; shell `execute`; và `task` để giao việc cho subagent. Công cụ **chạy lệnh** là `execute` (shell thật, thư mục làm việc là gốc sandbox). Về số tác tử: ở điều kiện `baseline` có 1 tác tử chính (đóng vai trò điều phối, *coordinator*) và 1 subagent mặc định `general-purpose`. Ở điều kiện `subagents` có thêm 3 tác tử con (*worker*) tự định nghĩa trong `src/lab/subagents.py`: `explorer` (chỉ đọc đặc tả, dữ liệu và báo cáo sự thật), `implementer` (sửa mã hoặc viết script, chạy test) và `reviewer` (kiểm tra độc lập theo từng quy tắc, không sửa tệp).
2. **Giao tiếp coordinator → worker.** Tác tử chính gọi công cụ `task(description, subagent_type)`. Mô tả công cụ `task` giới thiệu `general-purpose` là tác tử cho "researching complex questions, searching for files and content, and executing multi-step tasks", có cùng bộ công cụ với tác tử chính. Subagent **không** thấy hội thoại của tác tử chính: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report." Như vậy kênh giao tiếp duy nhất là prompt giao việc (đi) và một báo cáo cuối (về, dưới dạng `ToolMessage`). Tác tử chính phải tự kiểm tra báo cáo rồi mới dùng. Không có message queue hay trạng thái chung nào ngoài hệ thống tệp.
3. **Công cụ dùng chung và câu hướng dẫn hành vi.** System prompt mặc định rỗng (`''`), nên hành vi được định hướng qua mô tả công cụ. Mọi tác tử (chính và con) dùng chung một backend `LocalShellBackend`, tức là chung bộ công cụ tệp, shell và chung thư mục sandbox. Hệ thống tệp chính là "trạng thái dùng chung" giữa các tác tử. Câu trích từ `task`: "Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls." Câu trích từ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

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

`python -m lab.compare > report/table.md`:

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 7/10 |
| data-learn | 5/8 | 0/8 | 3/8 |
| logs-learn | 1/9 | 1/9 | 1/9 |
| code-eval | 7/11 | 7/11 | 7/11 |
| data-eval | 4/9 | 5/9 | 5/9 |
| logs-eval | 1/10 | 0/10 | 1/10 |
| **Mean score - learning tasks** | 0.48 | 0.27 | 0.40 |
| **Mean score - evaluation tasks** | 0.39 | 0.40 | 0.43 |
| **Mean tokens per run** | 50,770 | 50,140 | 57,762 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

`python scripts/check_breakdown.py` (check kỹ thuật và check quy ước đạt / tổng):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     12/18         0/12          61,221      0/3
baseline      learn    13/18         0/9           40,318      0/3
subagents     eval     12/18         0/12          65,824      0/3
subagents     learn     8/18         0/9           34,456      0/3
skills-auto   eval     13/18         0/12          63,985      0/3
skills-auto   learn    11/18         0/9           51,539      0/3
```

Không lần chạy nào có `error`; mọi lần chạy có `skills_modified = false`. Kết quả skills-auto ở Phần 3.4 (trước đóng băng, cùng bộ skill) được sao lưu ở `results/skills-auto-dev/`: code-learn 7/10, data-learn 5/8, logs-learn 6/9 (trung bình 0,664).

Điểm trung bình, token, thời gian và hiệu quả theo vai trò (tính từ `run.json`):

| Điều kiện | Vai trò | Điểm TB | Token TB | Giây TB | Tool call TB | Điểm / 100k token |
|---|---|---|---|---|---|---|
| baseline | học | 0,479 | 40 319 | 24,9 | 8,7 | 1,19 |
| baseline | đánh giá | 0,394 | 61 222 | 21,6 | 9,3 | 0,64 |
| subagents | học | 0,270 | 34 456 | 26,4 | 5,0 | 0,78 |
| subagents | đánh giá | 0,397 | 65 824 | 45,8 | 7,0 | 0,60 |
| skills-auto | học | 0,395 | 51 539 | 23,4 | 9,7 | 0,77 |
| skills-auto | đánh giá | 0,431 | 63 985 | 22,3 | 11,7 | 0,67 |
| skills-auto (Phần 3.4) | học | 0,664 | 51 394 | 21,9 | 10,0 | 1,29 |

## 8. Phân tích

**1. Cải thiện so với baseline.**
- *Tác vụ học:* sau đóng băng, không điều kiện nào cải thiện. Subagents 0,27 và skills-auto 0,40, so với baseline 0,48. Subagents tụt do data-learn 0/8 (mục 5).
- *Tác vụ đánh giá:* subagents 0,397 (+0,003) và skills-auto 0,431 (+0,037), so với baseline 0,394. Chênh lệch của skills-auto chỉ tương ứng **một** check (data-eval 5/9 so với 4/9: check kỹ thuật `march_revenue_utc`). Subagents được +1 check ở data-eval và −1 check ở logs-eval (`valid_structure` trượt).
- *Có điều kiện nào cải thiện tác vụ học mà không cải thiện tác vụ đánh giá?* Bề ngoài là có: skills-auto ở Phần 3.4 đạt 0,664 trên tác vụ học, cao hơn baseline 0,186, nhưng trên tác vụ đánh giá chỉ hơn 0,037. Đó thường là dấu hiệu quá khớp, nhưng ở đây **không phải**. `skills_read = 0` trong cả 9 lần chạy skills-auto, và cùng bộ skill đó sau đóng băng chỉ còn 0,395 trên tác vụ học. "Cải thiện" ở Phần 3.4 là nhiễu (câu 6), không phải học.

**2. Check kỹ thuật và check quy ước.**
- Check quy ước đạt **0/9** (học) và **0/12** (đánh giá) ở **cả ba điều kiện**.
- Check kỹ thuật trên tác vụ đánh giá: 12/18, 12/18, 13/18. Như vậy skill không giúp nhóm nào: không check `rule_` nào đạt, và +1 check kỹ thuật của skills-auto cũng xuất hiện ở subagents (data-eval 5/9), nên đây là dao động, không phải tác dụng của skill.
- Mỗi tác vụ đánh giá có một check quy ước **mới**: `rule_version_bump` (code), `rule_sorted_keys_format` (data), `rule_source_line` (logs). Cả ba trượt ở mọi điều kiện. Skill **không thể** giúp các check này: tri thức đó không có trong bất kỳ phản hồi nào của tác vụ học, nên curator không có nguồn để học. Kể cả khi tác tử có đọc skill, kết quả cũng vậy.
- Các quy ước **cũ** (lặp lại ở tác vụ đánh giá: `rule_type_hints`, `rule_regression_tests`, `rule_changelog`, `rule_money_in_cents`, `rule_meta_block`, `rule_clean_csv`, `rule_service_names`, `rule_sorted_errors`, `rule_schema_header`) là nơi skill lẽ ra có tác dụng, nhưng chúng cũng trượt ở skills-auto.

**3. Một check skill giúp và một check skill không giúp.**
- *Skill giúp:* **không có check nào** có thể quy cho skill, vì `skills_read = 0` ở cả 9 lần chạy skills-auto (3 ở Phần 3.4 và 6 sau đóng băng). Trường hợp dễ nhầm nhất là logs-learn ở Phần 3.4 (6/9, so với 1/9 của baseline): 5 check kỹ thuật đạt. Nhưng `trace.md` cho thấy bước đầu là `read_file /workspace/README.md`, không có lệnh đọc `skills/` nào, và mô hình tự viết script Python (1 lệnh `execute`, baseline có 0). Sau đóng băng, cùng cấu hình lại về 1/9.
- *Skill không giúp vì không được đọc:* `rule_changelog` ở code-learn và code-eval. Skill `code-package-fixes-and-tests` chứa đúng và đủ quy tắc ("CHANGELOG.md, under ## Unreleased, with bullet format '- fix(<function name>): <short description>'"), nhưng tác tử không mở skill, nên check vẫn trượt như baseline.
- *Skill không giúp vì skill thiếu:* `rule_schema_header` (logs) và `rule_meta_block` (data). Skill không chứa giá trị `schema_version: 2` / `generated_by: "log-triage"` và các khóa của `meta`, nên kể cả khi được đọc, tác tử cũng không thể đạt.

**4. Chi phí.**
- Token trung bình mỗi lần chạy: baseline 50 770, subagents 50 140, skills-auto 57 762 (+14%). skills-auto tốn hơn vì system prompt dài hơn (mục "Available Skills" và hướng dẫn progressive disclosure, gửi lại ở mọi lượt) và vì nhiều tool call hơn (11,7 so với 9,3 trên tác vụ đánh giá).
- Điểm / 100k token trên tác vụ đánh giá: skills-auto 0,67, baseline 0,64, subagents 0,60. Chênh lệch nằm trong nhiễu (câu 6). Trên toàn bộ 6 tác vụ, baseline hiệu quả nhất: 0,435 điểm cho 50 770 token, tức 0,86/100k (subagents 0,67, skills-auto 0,72).
- Đa tác tử **không đáng chi phí** trong thí nghiệm này. Token tương đương baseline, nhưng thời gian gấp 2,1 lần trên tác vụ đánh giá (45,8 s so với 21,6 s) và điểm không tăng (tác vụ học còn giảm 0,21). Ba subagent tự định nghĩa không được gọi; lợi ích song song hóa của đa tác tử không xuất hiện với các tác vụ tuần tự, nhỏ như ở đây.

**5. Rò rỉ dữ liệu và quá khớp.**
- *Rò rỉ:* không có định danh của tác vụ đánh giá trong skill. Cả 3 skill cuối qua `validate_skill` (kiểm tra `eval_markers()`). Bộ lọc còn chặn một skill ở lần chạy curator thứ 2 vì từ "orders". Đây là dương tính giả (từ đó có trong RULE của tác vụ học), và mình không lách bộ lọc.
- *Quá khớp:* skill data nhắc `order_id`, một tên cột của workspace data-learn (quy ước Acme không yêu cầu tên này), nên đây là dấu hiệu quá khớp nhẹ. Ngoài ra không có con số hay tên tệp dữ liệu cụ thể.
- *Biện pháp phòng tránh:*
  - `curate_skills` chỉ đọc run có `role == "learn"`; test `test_04_curator` kiểm tra prompt không chứa tác vụ đánh giá.
  - Giả thuyết được commit trước (`a28f8db`), sau đó mới tag `freeze` (`660c53e`); các lần chạy tác vụ đánh giá diễn ra sau tag (`verify_freeze` OK).
  - Không sửa tay `skills/auto/`.
  - Chỉ đọc tên check và số liệu tổng hợp của tác vụ đánh giá **sau** tag; không mở `trace.md` hay `check.py` của chúng.
- *Công khai:* ở đầu phiên làm việc, trước khi viết bất kỳ dòng mã nào, lệnh đọc tài liệu đã in nhầm cả `tasks/*-eval/instruction.md`. Không thông tin nào từ đó đi vào skill: skill do curator sinh từ prompt chỉ chứa dữ liệu tác vụ học, và nội dung skill không nhắc đến chúng.

**6. Nhiễu.**
- Cùng bộ skill, cùng mô hình, nhiệt độ 0: điểm tác vụ học ở Phần 3.4 là **0,664**, sau đóng băng là **0,395**, tức Δ = **0,269**.
- Theo từng tác vụ: code 7/10 → 7/10, data 5/8 → 3/8, logs 6/9 → 1/9. Cả hai lần chạy đều không đọc skill, nên toàn bộ chênh lệch là **nhiễu của mô hình** (khác cách làm: lần đầu viết script, lần sau chép tay).
- Mức nhiễu này lớn gấp khoảng 7 lần chênh lệch lớn nhất giữa các điều kiện trên tác vụ đánh giá (0,037). Vì vậy **không chênh lệch nào trong bảng ở mục 7 có ý nghĩa thống kê**. Với 3 tác vụ mỗi vai trò, một lần chạy cho mỗi cấu hình, chỉ một tác vụ "lật" cũng đã đổi trung bình tới 0,19.
- Kết luận đáng tin duy nhất về khác biệt là ở các check **ổn định qua mọi lần chạy**: check `rule_` luôn trượt (0/63 lượt check quy ước: 21 mỗi điều kiện × 3), và code luôn 7 check kỹ thuật đạt.

**Đối chiếu giả thuyết** (đã commit ở `a28f8db`):
- **H1 đúng:** subagents không cao hơn baseline (0,397 so với 0,394), không check `rule_` nào cải thiện, và tốn gấp 2,1 lần thời gian.
- **H2 đúng:** skills-auto xấp xỉ baseline (+0,037, trong khoảng ±0,15), `rule_` vẫn 0/12.
- **H3 đúng một phần:** đúng với baseline (0,48 → 0,39) và với việc chênh lệch giữa điều kiện nhỏ hơn nhiễu (0,037 so với 0,269). Sai một phần vì subagents và skills-auto có điểm tác vụ đánh giá *cao hơn* tác vụ học sau đóng băng (0,27 → 0,40; 0,40 → 0,43); nguyên nhân vẫn là nhiễu ở data-learn và logs-learn.

## 9. Hạn chế và tính hợp lệ

1. **Một lần chạy cho mỗi cấu hình, nhiễu lớn.** Cùng cấu hình mà điểm tác vụ học chênh 0,269 (mục 8.6), lớn hơn mọi khác biệt giữa các điều kiện. Ảnh hưởng: không thể kết luận điều kiện nào tốt hơn. Muốn tách tín hiệu cần chạy lặp ít nhất 3–5 lần mỗi cấu hình (hướng 6e) và báo cáo khoảng dao động.
2. **Chỉ 3 tác vụ mỗi vai trò, và một tác vụ quyết định phần lớn điểm.** Mỗi tác vụ chiếm 1/3 trung bình; logs dao động 1/9 ↔ 6/9 tùy mô hình có viết script hay không. Ảnh hưởng: trung bình theo vai trò rất nhạy với một tác vụ; kết luận không tổng quát hóa ra ngoài 3 họ tác vụ này.
3. **Một mô hình duy nhất và mô hình này không dùng skill.** `gpt-4.1-mini` không đọc skill trong cả 9 lần chạy, dù có `SKILLS_NOTE`. Ảnh hưởng: thí nghiệm đo tác dụng của *skill không được đọc*, không đo được chất lượng của skill. Không thể kết luận "skill tự sinh vô ích" nói chung; với mô hình tuân thủ chỉ dẫn tốt hơn, skill code (đủ 3 quy ước) có thể đã giúp 3 check.
4. **Tác vụ do giảng viên thiết kế, quy ước mới không học được.** Mỗi tác vụ đánh giá có thêm một quy ước không xuất hiện trong phản hồi của tác vụ học. Ảnh hưởng: trần điểm của skills-auto trên tác vụ đánh giá thấp hơn 1 theo thiết kế; lab đo khả năng *chuyển giao* quy ước cũ chứ không đo khả năng học quy ước mới.
5. **Curator ngẫu nhiên, giới hạn 2 lần chạy lại, bộ lọc rò rỉ có dương tính giả.** Lần 2 mất skill quy ước vì từ "orders". Ảnh hưởng: bộ skill cuối thiếu quy ước data và logs, nên kể cả khi được đọc cũng không thể đạt các check đó; chất lượng skill phụ thuộc vào lần lấy mẫu.
6. **Quan sát bị giới hạn.** `trace.md` cắt mỗi mục ở 1500 ký tự và không chứa hoạt động bên trong subagent. Ảnh hưởng: phân tích điều kiện subagents chỉ dựa trên lời giao việc và báo cáo trả về.

## 10. Kết luận

Với `gpt-4.1-mini`, một lần chạy cho mỗi cấu hình, cả đa tác tử và skill tự sinh đều không cải thiện điểm tác vụ đánh giá vượt mức nhiễu: 0,394 (baseline), 0,397 (subagents), 0,431 (skills-auto), trong khi nhiễu giữa hai lần chạy cùng cấu hình là 0,269. Nguyên nhân cơ chế đã được xác định từ vết: tác tử chính không dùng 3 subagent tự định nghĩa và không kiểm tra báo cáo của `general-purpose`; mô hình không đọc skill nào (`skills_read = 0` ở 9/9 lần chạy). Check quy ước trượt hoàn toàn (0/63 lượt) ở mọi điều kiện, nên tri thức tổ chức là nhóm lỗi chính mà thí nghiệm chưa giải được. Đa tác tử tốn gấp 2,1 lần thời gian mà không tăng điểm, nên không đáng chi phí cho các tác vụ nhỏ, tuần tự như ở đây. Đề xuất tiếp theo: lặp lại thí nghiệm với một mô hình tuân thủ chỉ dẫn tốt hơn và 3 lần chạy mỗi cấu hình, đồng thời chèn tóm tắt skill vào prompt (thay vì chỉ dựa vào progressive disclosure) để tách hai câu hỏi "skill có đúng không" và "skill có được đọc không".

## Phụ lục

- Lệnh đã chạy (theo thứ tự):

```bash
python3.11 -m venv .venv && source .venv/bin/activate && pip install -e .
cp .env.example .env            # LAB_MODEL=openai:gpt-4.1-mini, OPENAI_API_KEY tự điền
pytest tests/test_01_provided.py                 # 15 passed
python scripts/tour.py
pytest tests/                                    # 32 passed (sau khi cài 4 tệp)
python -m lab.runner --condition baseline --tasks learn
python -m lab.runner --condition subagents --tasks learn
python -m lab.curator                            # lần 1 -> report/curator_runs/run1/
python -m lab.curator                            # lần 2 (prompt sửa) -> report/curator_runs/run2/
python -c "from lab.curator import curate_skills; curate_skills(max_skills=4)"   # lần 3 = skills/auto/
python -m lab.runner --condition skills-auto --tasks learn
mv results/skills-auto results/skills-auto-dev
git commit -m "hypotheses: ..." && git commit --allow-empty -m "freeze skills" && git tag freeze
python -m lab.runner --condition baseline --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
python scripts/verify_freeze.py                  # OK
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
```

- Thử thách mở rộng của lab (Phần 6): không thực hiện. Hướng 6e (lặp để đo nhiễu) cần thêm 18 lần chạy, vượt ngân sách còn lại (9/30); mục 8.6 dùng cặp Phần 3.4 / sau đóng băng làm ước lượng nhiễu thay thế.
- Ghi chú khác: hệ đa tác tử coordinator–workers (Data/Code/Evaluator, MessageQueue, tool, benchmark) theo các hướng dẫn bổ sung được báo cáo riêng ở `report/MULTIAGENT_REPORT.md`; mã ở `src/coordinator.py`, `src/agents/`, `src/communication/`, `src/tools/`, test ở `tests_mas/` (32 passed), script ở `scripts_mas/`.
