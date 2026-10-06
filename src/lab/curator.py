"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    if out_dir is None:
        out_dir = ROOT / "skills" / "auto"
    out_dir = Path(out_dir)

    runs = []
    source_path = Path(results_dir) / source_condition
    if source_path.exists():
        for run_file in sorted(source_path.glob("*/run.json")):
            try:
                r = json.loads(run_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            # Tuyệt đối không dùng dữ liệu tác vụ đánh giá
            if r.get("role") != "learn":
                continue

            task_id = r.get("task", run_file.parent.name)
            trace_file = run_file.parent / "trace.md"
            trace = ""
            if trace_file.exists():
                try:
                    trace = trace_file.read_text(encoding="utf-8")[-6000:]
                except Exception:
                    trace = ""

            failed = []
            for c in r.get("checks", []):
                if not c.get("passed"):
                    failed.append({
                        "name": c.get("name", ""),
                        "detail": c.get("detail", ""),
                    })

            runs.append({
                "task": task_id,
                "failed": failed,
                "trace": trace,
            })

    # Nếu không có run nào có failed khác rỗng -> in cảnh báo và trả về [] (không gọi mô hình)
    if not any(bool(run["failed"]) for run in runs):
        print("Warning: no failed checks on learning tasks; skipping curator.")
        return []

    failures_blocks = []
    for r in runs:
        if not r["failed"]:
            continue
        flist = "\n".join(f"- Check: {f['name']}\n  Review bot feedback: {f['detail']}" for f in r["failed"])
        tblock = f"\nExecution trace (last part):\n{r['trace']}\n" if r["trace"] else ""
        failures_blocks.append(f"### Task: {r['task']}\nFailed checks:\n{flist}{tblock}")

    prompt = (
        f"You write SKILL documentation for an engineering agent working in a sandbox.\n"
        f"Below are the failed checks (check name and the review bot's feedback rule) and execution traces from baseline runs of learning tasks.\n"
        f"Identify the recurring procedural problems, organizational rules, and best practices (not task-specific hardcoded answers) "
        f"and write up to {max_skills} concise skills that will help avoid these failures on NEW tasks of the same family.\n\n"
        f"Rules:\n"
        f"- Generalize: Do not mention specific task IDs, specific input dataset filenames, or hardcoded answers. "
        f"Focus on procedures, conventions, and verification steps.\n"
        f"- Each skill must have YAML frontmatter with `name` (lowercase, letters/digits/dashes only, max 64 chars) "
        f"and `description` (one sentence: WHEN TO USE THIS SKILL, e.g. starting with 'Use when...').\n"
        f"- The body should be concise (at most 40 lines), actionable, imperative instructions and checklists.\n"
        f"- Output format must strictly match:\n"
        f"=== SKILL: <name> ===\n"
        f"---\n"
        f"name: <name>\n"
        f"description: <when to use>\n"
        f"---\n"
        f"<skill body>\n"
        f"=== END ===\n\n"
        + "\n\n".join(failures_blocks)
    )

    if model is None:
        from .model import make_model
        model = make_model()

    reply_msg = model.invoke(prompt)
    reply = getattr(reply_msg, "content", str(reply_msg))
    if isinstance(reply, list):
        reply = "".join(str(b.get("text", b)) if isinstance(b, dict) else str(b) for b in reply)

    written = []
    out_dir.mkdir(parents=True, exist_ok=True)
    blocks = parse_skill_blocks(reply)
    for name, text in blocks:
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            continue
        skill_folder = out_dir / name
        skill_folder.mkdir(parents=True, exist_ok=True)
        skill_file = skill_folder / "SKILL.md"
        skill_file.write_text(text, encoding="utf-8")
        written.append(skill_file)

    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
