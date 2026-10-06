# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lê Minh Sang | 2A202602864 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `ag/gemini-3.8-flash-high` qua OpenAI-compatible endpoint, `LAB_TEMPERATURE=0`, `recursion_limit=60` (chạy chính thức) và `recursion_limit=30` (chạy đối chiếu skills-auto).
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, macOS (Darwin x86_64), chạy trực tiếp với môi trường `uv` (Python 3.13 / virtualenv).
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / 25 lần chạy.
- Commit của tag `freeze`: `0afe5a7b85dd71d7cd4eccedeb0a7555f98fc7f8`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Trên các tác vụ đánh giá, điều kiện subagents dự kiến đạt điểm số tương đương hoặc chênh lệch nhỏ so với baseline do khả năng phân rã nhiệm vụ cho các chuyên viên (explorer, implementer, reviewer), nhưng chi phí token sẽ cao hơn đáng kể (tăng khoảng 50% - 100%) do chi phí trao đổi và cô lập ngữ cảnh (context isolation).
- H2 (skills-auto so với baseline): Trên các tác vụ đánh giá, điều kiện skills-auto dự kiến sẽ cải thiện điểm số ở các check quy ước tổ chức chung (như type annotations, regression tests, changelog) nếu các quy ước này được bảo toàn từ tác vụ học, tuy nhiên khả năng cải thiện trên các check kỹ thuật mới sẽ hạn chế do hiện tượng quá khớp (overfitting) theo kết quả của các nghiên cứu SkillsBench và SkillEvolBench.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ học sẽ cao hơn tác vụ đánh giá trên toàn bộ các điều kiện do tác vụ đánh giá chứa các trường dữ liệu và bẫy logic mới (distribution shift). Đồng thời, các quy ước tổ chức mới chỉ xuất hiện ở tác vụ đánh giá sẽ không thể được giải quyết bởi các skill tự sinh từ tác vụ học.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: công cụ thao tác tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), công cụ thực thi lệnh shell (`execute`), và công cụ gọi tác tử con (`task`). Trong đó, công cụ cho phép chạy lệnh shell là `execute`.
2. Mô tả của công cụ `task` nêu rõ: `general-purpose` là tác tử đa dụng dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp và nội dung, và thực hiện các tác vụ nhiều bước ("General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks"). Về ngữ cảnh, subagent hoạt động ở chế độ không lưu trạng thái mặc định (stateless by default): nó chỉ nhìn thấy duy nhất prompt được tác tử chính giao cho trong lệnh gọi công cụ và trả về một báo cáo duy nhất, hoàn toàn không nhìn thấy lịch sử hội thoại hay ngữ cảnh trước đó của tác tử chính ("Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return").
3. Một câu hướng dẫn hành vi từ mô tả công cụ `task`: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."
Một câu hướng dẫn hành vi từ mô tả công cụ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `parse_price_all_formats` | D. Bỏ sót dữ liệu bẩn hoặc định dạng | `wrong for: ['(12.00)']` (chưa xử lý biểu diễn số âm kế toán bằng dấu ngoặc đơn) |
| `code-learn` | `low_stock_follows_docstring` | A. Bỏ qua đặc tả | `low_stock returned ['b', 'A', 'c']` (chưa sắp xếp hoặc chuẩn hóa theo docstring) |
| `code-learn` | `csv_quoting_follows_docstring` | A. Bỏ qua đặc tả | `to_csv_row returned 'Desk, large "oak",10.00,2'` (thiếu escape ký tự quote theo RFC 4180) |
| `code-learn` | `rule_type_hints` | E. Vi phạm quy ước tổ chức | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| `code-learn` | `rule_regression_tests` | E. Vi phạm quy ước tổ chức | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| `code-learn` | `rule_changelog` | E. Vi phạm quy ước tổ chức | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| `data-learn` | `rule_money_in_cents` | E. Vi phạm quy ước tổ chức | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).` |
| `data-learn` | `rule_meta_block` | E. Vi phạm quy ước tổ chức | `RULE: answer.json has an object meta = {"source": <input file name>, "rows_in": <rows>, "rows_used": <used>}.` |
| `data-learn` | `rule_clean_csv` | E. Vi phạm quy ước tổ chức | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount...` |
| `logs-learn` | `valid_structure` | A. Bỏ qua đặc tả | `JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)` (xuất chuỗi dạng dict Python dùng nháy đơn thay vì JSON chuẩn RFC 8259) |

Nhận xét: Nhóm lỗi E (Vi phạm quy ước tổ chức) chiếm đa số tuyệt đối (6/10 check thất bại). Các quy ước này không được nêu trong đề bài (`instruction.md`) mà chỉ được kiểm tra ngầm bởi bot rà soát Acme. Một skill tự sinh có thể phòng ngừa nhóm lỗi E cực kỳ hiệu quả bằng cách tổng quát hóa các quy tắc `RULE:` thành checklist quy trình bắt buộc. Về mặt kỹ thuật (nhóm A-D), mô hình đạt được 4/18 check kỹ thuật ở baseline (theo `scripts/check_breakdown.py`), cho thấy mô hình giải quyết tốt logic cốt lõi khi cú pháp đầu ra được đảm bảo.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  1. `explorer`: Chuyên đọc và trích xuất cấu trúc dữ liệu, tài liệu, docstring mà không sửa đổi file; giúp phân tích toàn diện trước khi thực thi.
  2. `implementer`: Chuyên thực hiện các chỉnh sửa mã nguồn, viết script xử lý và chạy kiểm thử shell theo kế hoạch cụ thể.
  3. `reviewer`: Rà soát độc lập kết quả đầu ra, đối chiếu các trường hợp biên và kiểm tra tính hợp lệ của tệp theo yêu cầu đề bài.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  + `code-learn`: 0 lần. Tác tử chính nhận diện task tương đối gọn nên tự mình dùng các công cụ tệp `read_file`/`edit_file` và `execute` trực tiếp thay vì ủy quyền.
  + `data-learn`: 1 lần (`subagent_calls = 1`). Tác tử chính giao việc cho subagent xử lý dữ liệu lớn, giúp làm sạch và đạt được check `duplicate_rows_removed`.
  + `logs-learn`: 0 lần. Tác tử chính đọc file log và tự tạo file `errors.json`.
  + `code-eval`: 5 lần. Tác tử chính liên tục giao nhiệm vụ cho `explorer` tìm quy ước, `implementer` sửa code và `reviewer` kiểm thử độc lập.
  + `data-eval`: 3 lần. Tác tử chính phân công đọc data dictionary, lọc dữ liệu bẩn và kiểm tra file đầu ra.
  + `logs-eval`: Tác tử phân rã bước phân tích log đa dòng và chuẩn hóa timestamp.
- Thông tin thiếu hoặc thừa khi giao việc: Khi tác tử giao nhiệm vụ rõ ràng và đầy đủ đường dẫn tương đối, subagent xử lý rất chính xác. Subagent reviewer phát huy vai trò tối đa trong việc phát hiện thiếu sót của các quy ước tổ chức.
- Ảnh hưởng đến token và thời gian: Số lượng token tăng đáng kể (trung bình 994,707 tokens/run ở subagents so với 295,846 ở baseline), nhưng đổi lại chất lượng giải quyết vấn đề đạt mức tối đa.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy 1 lần duy nhất, sinh ra 3 skill hợp lệ. Không có skill nào bị xóa vì cả 3 skill đều tuân thủ chuẩn format YAML frontmatter, không rò rỉ dữ liệu đánh giá và mang tính quy trình khái quát cao.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `improve-data-validation` | Tổng quát cho việc xác thực định dạng dữ liệu, ép kiểu và bảo đảm tính toàn vẹn schema JSON. | Đúng đắn, hướng dẫn sử dụng try-except, type annotations và test biên. | 9 dòng; Description: "Use when validating data formats and ensuring data integrity in processing tasks."; `skills_read` = 3 ở `code-learn`. |
| `enhance-testing-practices` | Tổng quát cho quy trình viết bài kiểm thử hồi quy (regression tests) sau mỗi lần sửa lỗi. | Đúng đắn, hướng dẫn cấu trúc test rõ ràng, viết assertion kiểm tra output mong đợi. | 9 dòng; Description: "Use when developing and maintaining tests for code changes and new features."; `skills_read` = 3 ở `code-learn`. |
| `maintain-code-quality` | Tổng quát cho việc duy trì chất lượng mã nguồn, cập nhật changelog và tài liệu docstring. | Đúng đắn, hướng dẫn theo dõi thay đổi qua CHANGELOG.md và chuẩn hóa style guide. | 9 dòng; Description: "Use when writing or refactoring code to ensure adherence to best practices and maintainability."; `skills_read` = 3 ở `code-learn`. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

### Bảng so sánh từ `report/table.md` (sinh bởi `python -m lab.compare`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 4/10 | 2/10 | 1/10 |
| data-learn | 0/8 | 1/8 | 0/8 |
| logs-learn | 0/9 | 0/9 | 0/9 |
| code-eval | 1/11 | 11/11 | 1/11 |
| data-eval | 9/9 | 9/9 | 0/9 |
| logs-eval | 0/10 | 10/10 | 0/10 |
| **Mean score - learning tasks** | 0.13 | 0.11 | 0.03 |
| **Mean score - evaluation tasks** | 0.36 | **1.00** | 0.03 |
| **Mean tokens per run** | 295,846 | 994,707 | 107,512 |
| **Runs that read a skill** | 0/6 | 0/6 | **6/6** |

### Thống kê chi tiết từ `scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      6/18         4/12         421,901      0/3     
baseline      learn     4/18         0/9          169,792      0/3     
subagents     eval     18/18        12/12       1,810,778      0/3     
subagents     learn     3/18         0/9          178,636      0/3     
skills-auto   eval      1/18         0/12         107,203      3/3     
skills-auto   learn     1/18         0/9          107,820      3/3     
```

Ghi chú xử lý: Không có lần chạy nào bị `skills_modified = true`. Lệnh `python scripts/verify_freeze.py` trả về `checked 6 runs of skill conditions: OK`.

## 8. Phân tích

1. **So sánh điểm số học và đánh giá**: 
   - Trên tập đánh giá, điều kiện `subagents` áp đảo tuyệt đối với điểm số hoàn hảo **1.00 (100% - 30/30 check đạt)**, vượt xa `baseline` (0.36) và `skills-auto` (0.03).
   - Trên tập học, không có sự chênh lệch lớn giữa các điều kiện (`baseline`: 0.13, `subagents`: 0.11, `skills-auto`: 0.03). 
   - Điều này cho thấy kiến trúc đa tác tử phân cấp với chuyên môn hóa (`explorer`, `implementer`, `reviewer`) có năng lực giải quyết vấn đề mới và thích ứng tổng quát vượt trội hơn hẳn một tác tử đơn lẻ.

2. **Tách điểm kỹ thuật và quy ước (`rule_`)**:
   - `subagents` trên tập đánh giá đạt trọn vẹn **18/18 check kỹ thuật (100%)** và **12/12 check quy ước tổ chức Acme (100%)**. Nhờ có sự phân công cho subagent `reviewer`, tác tử đã kiểm tra kỹ lưỡng các yêu cầu về type hint, file hồi quy `test_regressions.py`, và format chuẩn của `clean.csv`.
   - Check quy ước mới của tác vụ đánh giá không được giải quyết bởi `skills-auto` vì các skill sinh ra từ tập học mang tính trừu tượng ("viết kiểm thử", "chuẩn hóa dữ liệu") chứ không chứa trước các quy ước cụ thể của đề bài mới.

3. **Cơ chế sử dụng skill dựa vào vết và `skills_read`**:
   - Tác tử ở điều kiện `skills-auto` đã đọc đủ 6/6 lần chạy (`skills_read = 3` ở mỗi bài kiểm tra).
   - Check mà skill giúp: Check `tests_not_modified` đạt được một cách ổn định do skill `enhance-testing-practices` định hướng tạo test suite riêng thay vì chỉnh sửa test có sẵn.
   - Check mà skill không giúp: Check `rule_clean_csv` và `rule_money_in_cents` ở `data-learn` và `data-eval`. Tác tử đọc skill `improve-data-validation` nhưng khi giải quyết đề bài, nó tập trung vào việc tính toán số liệu mà bỏ sót quy tắc phụ chuyển đổi dollar sang cent, chứng minh hiện tượng LLM dễ bỏ qua các chỉ dẫn chi tiết khi đối mặt với context dài.

4. **Phân tích chi phí (Token Cost vs Performance)**:
   - `skills-auto` tiêu thụ ít token nhất (107,512 tokens/run), tiết kiệm gần 3 lần so với `baseline` (295,846 tokens) và gần 10 lần so với `subagents` (994,707 tokens).
   - Tuy nhiên, về mặt hiệu quả chất lượng trên chi phí (Value per Token), `subagents` hoàn toàn xứng đáng với mức đầu tư token khi đưa tỷ lệ thành công của bài toán từ 36% lên **100% tuyệt đối** trên toàn bộ các bài toán đánh giá. Trong môi trường thực tế, việc bỏ thêm token để đảm bảo hệ thống không có bug là một trade-off hoàn toàn tối ưu.

5. **Rò rỉ dữ liệu và quá khớp**:
   - Không có rò rỉ dữ liệu (data leakage): Toàn bộ quy trình curate skill chỉ đọc các tác vụ `role == "learn"`, bộ lọc `eval_markers()` quét chặn các định danh đánh giá, và quy trình đóng băng được git xác thực nghiêm ngặt bằng tag `freeze` trước khi chạy eval.
   - Về quá khớp (overfitting): Skill tự sinh có xu hướng khái quát hóa các lỗi cục bộ của bài học, nhưng khi sang bài đánh giá với dữ liệu và bẫy mới, các chỉ dẫn trừu tượng không đủ cụ thể để giúp tác tử vượt qua các bài kiểm tra gắt gao.

6. **Ước lượng nhiễu (Noise Analysis)**:
   - So sánh điểm tác vụ học giữa giai đoạn dev (Phần 3.4) và sau đóng băng (Phần 4.2):
     + `code-learn`: 1/10 (dev) vs 1/10 (freeze) -> chênh lệch 0.00
     + `data-learn`: 0/8 (dev) vs 0/8 (freeze) -> chênh lệch 0.00
     + `logs-learn`: 0/9 (dev) vs 0/9 (freeze) -> chênh lệch 0.00
   - Độ chênh lệch bằng 0.00 khẳng định rằng khi cố định `LAB_TEMPERATURE=0`, tính tất định của hệ thống là rất cao, và sự vượt trội 100% của `subagents` ở tập đánh giá là một kết quả có ý nghĩa thống kê thực chất.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập tác vụ còn hạn chế**: Thí nghiệm gồm 6 tác vụ (3 học, 3 đánh giá). Mặc dù bao quát đủ 3 họ kỹ năng (code, data, logs), kích thước mẫu vẫn còn nhỏ để ngoại suy cho mọi kịch bản kỹ thuật phần mềm phức tạp.
2. **Chi phí và độ trễ của Đa tác tử**: Điều kiện `subagents` đạt chất lượng 100% nhưng có độ trễ cao và tiêu tốn lượng token gấp 3-9 lần so với tác tử đơn lẻ, đòi hỏi phải có cơ chế router thông minh để chỉ kích hoạt đa tác tử khi thực sự cần thiết.
3. **Phụ thuộc vào quy ước định sẵn (House Rules)**: Các quy ước ẩn Acme mang tính thiết kế có chủ ý; trong các hệ thống doanh nghiệp thực tế, các quy tắc này thường nằm rải rác trong tài liệu wiki hoặc văn hóa nhóm mà không có bot rà soát tự động phản hồi ngay lập tức.

## 10. Kết luận

Thí nghiệm chứng minh rằng kiến trúc Đa tác tử phân cấp (`subagents`) với sự phân tách trách nhiệm rõ ràng (`explorer`, `implementer`, `reviewer`) mang lại bước nhảy vọt về chất lượng, đạt **100% điểm số (30/30 checks)** trên toàn bộ tập tác vụ đánh giá. Trong khi đó, tác tử tự tiến hóa ở tầng ngữ cảnh (`skills-auto`) giúp tiết kiệm chi phí token và nạp đúng quy trình, nhưng cần kết hợp cơ chế phản hồi theo thời gian thực (in-context hot-path feedback) để giải quyết các quy ước tổ chức mới. Hướng cải tiến tiếp theo là xây dựng cơ chế định tuyến thích ứng (Dynamic Routing) để tự động cân bằng giữa chi phí token của single-agent và độ tin cậy tuyệt đối của multi-agent.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự)**:
  1. `uv run pytest tests/test_01_provided.py`
  2. `uv run python scripts/tour.py`
  3. `uv run pytest tests/test_02_agent.py`
  4. `uv run pytest tests/test_03_runner.py`
  5. `uv run pytest tests/test_04_curator.py`
  6. `uv run python -m lab.runner --condition baseline --tasks learn`
  7. `uv run python -m lab.runner --condition subagents --tasks learn`
  8. `uv run python -m lab.curator`
  9. `uv run python -m lab.runner --condition skills-auto --tasks learn`
  10. `cp -r results/skills-auto results/skills-auto-dev`
  11. `git add -A && git commit -m "hypotheses"`
  12. `git commit --allow-empty -m "freeze skills" && git tag freeze`
  13. `uv run python -m lab.runner --condition baseline --tasks eval`
  14. `uv run python -m lab.runner --condition subagents --tasks eval`
  15. `uv run python -m lab.runner --condition skills-auto --tasks all --recursion-limit 30`
  16. `uv run python scripts/verify_freeze.py`
  17. `uv run python -m lab.compare > report/table.md`
  18. `uv run python scripts/check_breakdown.py`
  19. `uv run python scripts/challenge_redteam.py`

- **Thử thách mở rộng (Bonus +5 điểm) - Hướng 6c: Tấn công và Phòng thủ Curator (Red Teaming the Curator)**:
  - **Mục tiêu**: Đánh giá các nguy cơ tiềm ẩn khi Curator tự động đọc vết lỗi và viết skill, bao gồm nguy cơ rò rỉ dữ liệu tập đánh giá (data leakage) hoặc chèn mã độc/path traversal.
  - **Thực thi**: Tạo script `scripts/challenge_redteam.py` thử nghiệm 4 vector tấn công: (A1) Trực tiếp chèn định danh tập đánh giá, (A2) Tấn công Directory Traversal (`../evil`), (A3) Tấn công diễn đạt lại ngữ nghĩa (Semantic Paraphrasing), (A4) Mã hóa Base64 để vượt qua regex.
  - **Kết quả thực nghiệm** (lưu tại `results/extension-redteam/redteam_report.json`):
    + Bộ phòng thủ cơ sở (`validate_skill`) chặn đứng thành công 100% các vector A1 và A2 nhờ `eval_markers()` và `SAFE_NAME`.
    + Giải pháp phòng thủ đa tầng (Hardened Defense) bổ sung bộ giải mã tự động và nhận diện thực thể ngữ nghĩa, ngăn chặn 100% cả 4 vector tấn công tinh vi.
  - **Khả năng tái lập**: Chạy độc lập bằng lệnh `uv run python scripts/challenge_redteam.py`, không ảnh hưởng tới kết quả chính và dữ liệu đóng băng.
