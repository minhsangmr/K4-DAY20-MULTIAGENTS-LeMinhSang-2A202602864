# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lê Minh Sang | 2A202602864 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `ag/gemini-3.8-flash-high` qua OpenAI-compatible endpoint, `LAB_TEMPERATURE=0`, `recursion_limit=60`.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, macOS (Darwin x86_64), chạy trực tiếp với `uv` (Python 3.13 / virtualenv).
- Số lần chạy tác vụ đã dùng / ngân sách: 18 / 25 lần chạy.
- Commit của tag `freeze`: (sẽ điền sau khi tạo tag)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Trên các tác vụ đánh giá, điều kiện subagents dự kiến đạt điểm số tương đương hoặc chênh lệch nhỏ so với baseline do khả năng phân rã nhiệm vụ cho các chuyên viên (explorer, implementer, reviewer), nhưng chi phí token sẽ cao hơn đáng kể (tăng khoảng 50% - 100%) do chi phí trao đổi và cô lập ngữ cảnh (context isolation).
- H2 (skills-auto so với baseline): Trên các tác vụ đánh giá, điều kiện skills-auto dự kiến sẽ cải thiện điểm số ở các check quy ước tổ chức chung (như type annotations, regression tests, changelog) nếu các quy ước này được bảo toàn từ tác vụ học, tuy nhiên khả năng cải thiện trên các check kỹ thuật mới sẽ hạn chế do hiện tượng quá khớp (overfitting) theo kết quả của các nghiên cứu SkillsBench và SkillEvolBench.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ học sẽ cao hơn tác vụ đánh giá trên toàn bộ các điều kiện do tác vụ đánh giá chứa các trường dữ liệu và bẫy logic mới (distribution shift). Đồng thời, các quy ước tổ chức mới chỉ xuất hiện ở tác vụ đánh giá sẽ không thể được giải quyết bởi các skill tự sinh từ tác vụ học.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: công cụ thao tác tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), công cụ thực thi lệnh shell (`execute`), và công cụ gọi tác tử con (`task`). Trong đó, công cụ cho phép chạy lệnh là `execute`.
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
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): Khi giao việc ở `data-learn`, tác tử chính truyền mô tả bài toán nhưng do subagent không kế thừa ngữ cảnh hội thoại đầy đủ và không biết các quy ước ẩn, subagent tập trung vào xử lý số liệu nhưng chưa bao quát được toàn bộ format JSON theo chuẩn Acme.
- Ảnh hưởng đến token và thời gian: Số lượng token ở `code-learn` tăng gần gấp đôi (từ 139,907 ở baseline lên 266,210 ở subagents) và ở `data-learn` tiêu tốn 242,119 tokens, cho thấy chi phí overhead của multi-agent là rất đáng kể.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy 1 lần duy nhất, sinh ra 3 skill hợp lệ. Không có skill nào bị xóa vì cả 3 skill đều tuân thủ chuẩn format YAML frontmatter, không rò rỉ dữ liệu đánh giá và mang tính quy trình khái quát cao.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `improve-data-validation` | Tổng quát cho việc xác thực định dạng dữ liệu, ép kiểu và bảo đảm tính toàn vẹn schema JSON. | Đúng đắn, hướng dẫn sử dụng try-except, type annotations và test biên. | 9 dòng; Description: "Use when validating data formats and ensuring data integrity in processing tasks."; `skills_read` = 3 ở `code-learn`. |
| `enhance-testing-practices` | Tổng quát cho quy trình viết bài kiểm thử hồi quy (regression tests) sau mỗi lần sửa lỗi. | Đúng đắn, hướng dẫn cấu trúc test rõ ràng, viết assertion kiểm tra output mong đợi. | 9 dòng; Description: "Use when developing and maintaining tests for code changes and new features."; `skills_read` = 3 ở `code-learn`. |
| `maintain-code-quality` | Tổng quát cho việc duy trì chất lượng mã nguồn, cập nhật changelog và tài liệu docstring. | Đúng đắn, hướng dẫn theo dõi thay đổi qua CHANGELOG.md và chuẩn hóa style guide. | 9 dòng; Description: "Use when writing or refactoring code to ensure adherence to best practices and maintainability."; `skills_read` = 3 ở `code-learn`. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

(Sẽ cập nhật sau khi hoàn thành các lần chạy đánh giá chính thức)

## 8. Phân tích

(Sẽ cập nhật chi tiết sau khi có bảng số liệu đối chiếu)

## 9. Hạn chế và tính hợp lệ

1. Kích thước tập dữ liệu nhỏ (3 tác vụ học, 3 tác vụ đánh giá): Mỗi họ tác vụ chỉ có 1 tác vụ học và 1 tác vụ đánh giá, khiến kết quả dễ bị ảnh hưởng bởi đặc thù của từng bài toán cụ thể thay vì phản ánh xu hướng thống kê lớn.
2. Nhiễu ngẫu nhiên của mô hình ngôn ngữ lớn (LLM stochasticity): Cùng một mô hình và cùng một câu lệnh có thể cho ra kết quả khác nhau giữa các lần chạy do bản chất sinh xác suất và nhiệt độ suy luận.
3. Sự phụ thuộc vào thiết kế quy ước nhân tạo ("House Rules"): Các quy ước của tổ chức Acme mang tính chủ đích do người ra đề thiết kế để tạo khoảng trống cho skill phát huy tác dụng; trong các môi trường công nghiệp thực tế, các quy tắc này thường phức tạp và phân tán hơn nhiều.

## 10. Kết luận

(Sẽ hoàn thiện sau khi tổng hợp toàn bộ kết quả)

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
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
