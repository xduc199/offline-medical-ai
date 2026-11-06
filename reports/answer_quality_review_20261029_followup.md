# Báo cáo follow-up chất lượng câu trả lời — 2026-10-29

## Mục tiêu và phạm vi

Điều tra lỗi citation của các câu trả lời ABCDE, sửa kiểm tra cấu trúc Markdown và prompt repair, đánh giá bộ lọc tiếng Anh, kiểm tra đường truy xuất liên quan, và ghi nhận một lượt sinh thật sau sửa. Đây là đánh giá kỹ thuật của ứng dụng tra cứu tài liệu WHO/ICRC *Basic Emergency Care* (2018), không phải đánh giá lâm sàng.

Mã được đánh giá trên nhánh `fix/pilot-answer-quality`, HEAD `f0d83ae`. Worktree đã có thay đổi tracked và báo cáo/log untracked trước follow-up này; chúng được giữ nguyên. Báo cáo cũ không bị ghi đè. Kết quả kiểm thử trong báo cáo phản ánh worktree sau các chỉnh sửa được liệt kê dưới đây, không phải riêng commit HEAD.

## Cấu hình

| Thành phần | Trạng thái đã xác minh |
|---|---|
| Python | 3.12.10 |
| Model | `qwen2.5:7b-instruct-q4_K_M`, Ollama cục bộ tại `127.0.0.1:11434` |
| API pilot | `127.0.0.1:8765`; `/api/health` trả `ok=true` |
| Retrieval | Keyword; semantic index chưa nạp |
| Tài liệu | 1 nguồn WHO/ICRC, 1.496 chunks trong corpus đang nạp |
| Dữ liệu người bệnh | Không dùng |

## Phân tích nguyên nhân và thay đổi

| Vấn đề | Bằng chứng / nguyên nhân đã xác nhận | Thay đổi |
|---|---|---|
| `(S1)` bị báo thiếu citation | Validator chấp nhận dạng chuẩn `[S1]`; dấu ngoặc tròn không được nhận là citation hợp lệ nên lỗi chung dễ gây nhầm nguyên nhân. | Giữ một cú pháp chuẩn `[S1]`, nhận diện `(S1)` để báo `invalid_citation_format`; prompt nêu rõ không dùng ngoặc tròn. |
| Gạch đầu dòng lồng nhau bị báo sai hoặc lọt claim | Bộ kiểm tra cũ coi mọi dòng bullet là claim riêng và kiểm tra citation ngay trên dòng đó; nhãn/container như `- Khám ban đầu (ABCDE):` không nhất thiết là khẳng định. Việc gom nội dung theo đoạn cũng có thể để citation cuối đoạn che một câu trước đó. | Phân tích heading, đoạn văn, câu, soft-wrap và danh sách lồng nhau; bỏ qua heading/nhãn container không phải claim; kiểm từng câu/item thực tế; citation trước claim bị báo đặt sai vị trí. |
| Prompt repair không chỉ rõ lỗi | Prompt cũ không truyền đầy đủ câu bị từ chối và lý do validator, khiến model có thể lặp lỗi. | Prompt repair nhận draft bị từ chối, issue code/chi tiết, nguồn hợp lệ và quy tắc loại bỏ claim không được nguồn hỗ trợ. Tối đa một repair (hai vòng sinh). |
| Cảnh báo tiếng Anh báo động giả | Quy tắc trước đó không có ngoại lệ hẹp cho thuật ngữ ngắn sau phần giải thích tiếng Việt. | Cho phép danh sách thuật ngữ ngắn đã chọn trong ngoặc sau gloss tiếng Việt; câu/đoạn tiếng Anh chưa dịch vẫn bị từ chối. |
| Câu hỏi ABCDE chỉ nhận được đoạn một phần | Keyword retrieval thông thường trả các trang 48–49 với nội dung một phần; danh sách định nghĩa đủ năm tên có trong corpus ở PDF p. 221. | Thêm truy xuất từ khóa hẹp cho câu hỏi yêu cầu ABCDE đầy đủ. Câu trả lời xác định chỉ nêu tên năm thành phần và cảnh báo nguồn không mô tả đủ thao tác; không gọi model để suy diễn. |
| Lỗi Ollama/API có thể chứa chi tiết exception | Exception vận chuyển hoặc lỗi nội bộ có thể đưa chuỗi chi tiết vào warning/response. | Che chi tiết lỗi Ollama, nhận diện timeout bọc trong `URLError`, chuẩn hóa JSON Ollama sai, kiểm tra body API là JSON object và trả lỗi 500 chung; log chỉ ghi loại exception. |

Validator kiểm tra cú pháp, phạm vi ID nguồn và cấu trúc trích dẫn; nó **không chứng minh entailment/ngữ nghĩa cho mọi claim**. Một citation hợp lệ không đồng nghĩa nguồn hỗ trợ nội dung. Một số guard cụ thể (ví dụ kiểm tra coverage ABCDE, chủ đề và tình huống postpartum) không thay thế đánh giá bằng chứng toàn diện.

## Dữ liệu và kết quả

### Kiểm thử tự động

Lệnh `python -m unittest discover -s tests -p 'test_*.py'` chạy **132 test, tất cả đạt**. Các test bao gồm cú pháp/ID citation, nhiều câu, Markdown heading và list lồng nhau, citation sai vị trí, bounded repair, untranslated English, câu hỏi ABCDE, triage API, JSON không phải object, lỗi API không lộ exception, timeout Ollama và JSON phản hồi sai.

Đã chạy `py_compile` cho các module/test liên quan và `git diff --check`; cả hai đạt. Kiểm thử API bằng server trong tiến trình dùng các dependency giả là integration test, không phải kiểm thử model thật.

Sau khi cập nhật API error handling, đã khởi động lại pilot từ mã hiện tại và xác minh `/api/health`, request ABCDE không gọi model và nhánh cấp cứu không truy xuất. Pilot do lượt kiểm tra khởi chạy đã được dừng; cổng 8765 hiện đóng.

### Kiểm thử endpoint và model thật

Đã gửi bốn tình huống smoke test tới API cục bộ, không dùng dữ liệu người bệnh:

| Tình huống | Kết quả quan sát |
|---|---|
| B07 — tóm tắt nội dung bỏng, có nguồn | HTTP 200; hai vòng sinh; câu trả lời bị ẩn sau repair vì `uncited_claim` và cảnh báo bản địa hóa vẫn còn. |
| B02 — hỏi các bước đánh giá chấn thương/ABCDE, nguồn chỉ hỗ trợ một phần | HTTP 200; truy xuất đặc biệt đưa PDF p. 221; trả lời định danh năm thành phần cùng cảnh báo rằng nguồn chưa mô tả đủ thao tác; không gọi model. |
| Hỏi liều kháng sinh/appendicitis không có bằng chứng trong corpus | HTTP 200; `out_of_scope`, không có nguồn, không gọi model. |
| Tình huống khó thở khẩn cấp | HTTP 200; nhánh `possible_emergency`, không retrieval và không gọi model. |

Trong chẩn đoán đã bật tạm thời cho lượt B07, có **2 bản ghi sinh** (draft đầu và repair). Cả hai có lỗi cấu trúc `uncited_claim` và cảnh báo translation; không ghi nhận lỗi ID nguồn không tồn tại hay dạng ngoặc tròn trong chính lượt này. Kết quả cuối cùng bị ẩn, nguồn được trả để người dùng đối chiếu. Nội dung draft không được đưa vào báo cáo. Log chẩn đoán đầy đủ nằm ngoài workspace tại `C:\Users\Admin\AppData\Local\Temp\bec_generation_review_98d85ae299de461d99f4ea641c44c1bd.jsonl`; lệnh dọn file bị chính sách công cụ chặn, nên file vẫn còn ở vị trí tạm này.

Đếm theo lượt sinh thật: **0/1 câu trả lời model được chấp nhận, 1/1 bị ẩn sau một repair**. Đây là mẫu một câu, không phải ước lượng tỷ lệ lỗi. Không có chuyên gia y tế chấm câu trả lời; số ca human review = 0. Không có đánh giá an toàn lâm sàng.

### Tập đánh giá truy xuất

`tests/broad_questions_vi.json` có 8 câu, trong đó 7 câu có trang tham chiếu được gán nhãn. Benchmark keyword top-k=5 đạt Recall@5 **1.000**, MRR **0.929**, HitRate@5 **1.000**, latency truy xuất trung bình **0.002 s**. Đây là độ khớp trang trên bộ nhãn hiện có; không đo chất lượng câu sinh, mức entailment hoặc an toàn. Benchmark trực tiếp không gọi nhánh endpoint ABCDE đặc biệt.

## Dữ liệu so sánh và giới hạn

- Không có baseline answer-quality được con người chấm trước sửa. Candidate/log cũ không tương đương với review chuyên gia; `answer_quality_review.json` hiện không có phiếu chấm. Vì vậy không tính mức cải thiện phần trăm.
- Có lần chạy ban đầu **115 test đạt** trước khi sửa; hiện **132 test đạt** sau khi bổ sung hồi quy. Số test tăng không phải bằng chứng an toàn y khoa.
- Báo cáo hiệu năng cũ ghi 0/24 request do API khi đó chưa chạy. Không thể so sánh latency benchmark cũ với lượt này.
- Kiểm tra citation là kiểm tra cấu trúc, không phải xác minh ngữ nghĩa đầy đủ. Không thể kết luận các claim trong draft B07 đúng hay sai về chuyên môn chỉ từ các mã lỗi cấu trúc.
- Một lượt model thật sau sửa vẫn thất bại; sửa parser/prompt không bảo đảm model đạt ở mọi lần chạy.

## Việc tiếp theo

1. Chạy đánh giá mù trên tập câu hỏi định trước với ít nhất hai người đọc có chuyên môn; chấm riêng độ đúng theo nguồn, mức đầy đủ, citation, tiếng Việt và tình huống cần từ chối.
2. Lưu nhãn chuyên gia và nội dung sinh theo quy trình bảo mật; không dùng tỷ lệ test tự động làm đại diện cho độ an toàn.
3. Xem lại các lần B07 thất bại bằng chẩn đoán tạm trong môi trường kiểm soát; chỉ thử model thêm sau khi xác định thay đổi cần đánh giá, tránh chạy lặp tốn thời gian.
4. Nếu cần khẳng định nguồn hỗ trợ claim, thiết kế đánh giá entailment có người gán nhãn và kiểm định riêng; không suy ra điều đó từ việc `[S1]` xuất hiện.

## Tệp mã được chỉnh trong follow-up

- `app/answer_validation.py`
- `app/internal_pilot.py`
- `app/README_internal_pilot.md`
- `tests/test_answer_validation.py`
- `tests/test_ask_endpoint_triage.py`
- `tests/test_grounded_answer_retry.py`

Các thay đổi sẵn có trong `app/topic_relevance.py`, `tests/test_topic_relevance.py` và `tests/test_hybrid_retrieval_integration.py` đã tồn tại trong worktree trước follow-up và được bảo toàn. Không đổi nhánh, commit, push hoặc tạo PR.
