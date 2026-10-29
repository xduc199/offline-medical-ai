# Bản thử nghiệm nội bộ WHO/ICRC BEC

Đây là bản mẫu chạy cục bộ để nhân sự đánh giá khả năng tra cứu nội dung trong tài liệu WHO/ICRC Basic Emergency Care 2018 đã làm sạch. **Không phải công cụ hỗ trợ quyết định lâm sàng**; không dùng cho chăm sóc người bệnh, chẩn đoán, phân loại cấp cứu, kê đơn hoặc xử trí tình huống thực tế.

## Phân cấp an toàn

- **Mức 0 — Tra cứu tài liệu (mức hiện tại):** tìm đoạn nguồn và trả lời câu hỏi về chính nội dung đó. Không nhận định chẩn đoán, không phân loại cấp cứu và không khuyến nghị xử trí cho một người bệnh cụ thể.
- **Mức 1 — Giáo dục có kiểm soát:** giải thích khái niệm chung từ nguồn, có trích dẫn và rà soát của chuyên gia trước khi phát hành.
- **Mức 2 — Hỗ trợ chuyên môn có giám sát:** chỉ xem xét sau khi có bộ kiểm định đại diện, xác nhận lâm sàng độc lập, kiểm soát thay đổi và quy trình giám sát người dùng đủ chuyên môn.
- **Mức 3 — Đề xuất chẩn đoán/xử trí cho ca bệnh:** chưa được triển khai. Cần đánh giá lợi ích-nguy cơ, xác nhận độc lập trên dữ liệu phù hợp, quản trị và xem xét quy định áp dụng trước khi cân nhắc.

Các mức này là phân loại vận hành nội bộ cho prototype, không phải chứng nhận an toàn hay phân loại pháp lý.

## Khởi chạy

Yêu cầu: Python 3.12 trở lên, Ollama đang chạy cục bộ và đã cài model `qwen2.5:7b-instruct-q4_K_M`.

Cài model nếu máy chưa có:

```powershell
ollama pull qwen2.5:7b-instruct-q4_K_M
```

Mở PowerShell tại thư mục gốc dự án:

```powershell
python .\app\internal_pilot.py
```

Mở <http://127.0.0.1:8765>. Dừng máy chủ bằng `Ctrl+C`.

## Bật log chẩn đoán khi debug

Mặc định ứng dụng không ghi prompt, câu hỏi hoặc bản nháp của mô hình. Để bật log cho một phiên debug có kiểm soát, đặt `BEC_PILOT_DIAGNOSTICS_PATH` trước khi khởi chạy:

```powershell
$env:BEC_PILOT_DIAGNOSTICS_PATH = Join-Path $env:TEMP "bec-generation-debug.jsonl"
python .\app\internal_pilot.py
```

Tệp được ghi theo chế độ nối thêm. Mỗi bản ghi chứa prompt hệ thống, prompt người dùng (gồm câu hỏi, ngữ cảnh nguồn và khi retry có bản nháp bị từ chối), đoạn nguồn, đầu ra thô, kết quả kiểm tra và ID/trang nguồn. Nếu Ollama lỗi trước khi trả đầu ra, bản ghi có stage, loại lỗi và nhóm lỗi an toàn nhưng không chứa nội dung exception thô. Chỉ dùng đường dẫn cục bộ được bảo vệ, không dùng dữ liệu nhận dạng hoặc thông tin nhạy cảm của người bệnh, và không đặt log trong thư mục được phát hành công khai. Chọn tên tệp riêng nếu cần giữ log cũ. Sau phiên debug, dừng máy chủ rồi tắt biến môi trường bằng `Remove-Item Env:BEC_PILOT_DIAGNOSTICS_PATH`. Nếu không ghi được log, ứng dụng phát cảnh báo cho người phát triển nhưng vẫn tiếp tục xử lý request.

## Thử bộ câu hỏi rộng

Khi máy chủ đang chạy, mở PowerShell ở thư mục gốc dự án và chạy:

```powershell
python .\tests\run_broad_questions.py
```

Bộ câu hỏi nằm trong `tests/broad_questions_vi.json`. Mỗi lượt in câu trả lời, nguồn được truy xuất, cảnh báo và thời gian phản hồi để người đánh giá rà soát. Chạy nhanh một vài câu bằng `--limit`, ví dụ `python .\tests\run_broad_questions.py --limit 3`. Đây là công cụ rà soát thủ công, không tự đánh giá độ an toàn lâm sàng.

Có thể cấu hình trước khi khởi chạy:

```powershell
$env:BEC_PILOT_PORT = "8765"
$env:BEC_OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"
$env:OLLAMA_URL = "http://127.0.0.1:11434"
python .\app\internal_pilot.py
```

Máy chủ chỉ lắng nghe trên máy cục bộ (`127.0.0.1`), gửi câu hỏi đến Ollama cục bộ, không lưu lịch sử trò chuyện và không ghi nội dung câu hỏi vào log. Không nhập thông tin nhận dạng hoặc dữ liệu nhạy cảm của người bệnh.

## Cách hoạt động và giới hạn

- Tìm đoạn bằng từ khóa và một bảng mở rộng nhỏ từ một số cụm tiếng Việt sang tiếng Anh. Đây không phải tìm kiếm ngữ nghĩa; có thể bỏ sót đoạn phù hợp.
- Hiển thị đoạn nguồn tìm được, trang PDF nếu có nhãn trang, và số dòng trong bản cleaned.
- Tự dịch các đoạn nguồn được truy xuất sang tiếng Việt và hiển thị cạnh nguyên văn tiếng Anh. Bản dịch chỉ bao phủ các đoạn truy xuất, không phải bản dịch toàn bộ tài liệu.
- Không gọi model khi kết quả tìm kiếm dưới ngưỡng phù hợp cơ bản.
- Model chạy ở chế độ hướng dẫn hội thoại, được yêu cầu chỉ dùng đoạn trích, nêu đủ các chi tiết/điều kiện liên quan, trả lời hoàn toàn bằng tiếng Việt và dẫn mã nguồn. Ứng dụng ẩn câu trả lời hoặc bản dịch nếu phát hiện thiếu mã nguồn, còn thuật ngữ tiếng Anh phổ biến, lặp bất thường hoặc một số cụm dịch sai đã biết.
- Bộ lọc chất lượng chỉ phát hiện một số lỗi hình thức; không thể chứng minh bản dịch đầy đủ hay chính xác về chuyên môn. Mọi nội dung tự động vẫn cần người có chuyên môn đối chiếu từng ý với nguyên văn nguồn.
- Mã trích dẫn chỉ cho biết đoạn nào đã được đưa vào model; không chứng minh câu trả lời được đoạn đó hỗ trợ. Người rà soát phải đối chiếu từng ý với đoạn nguồn hiển thị.
- Chưa có đăng nhập, phân quyền, lịch sử bền vững, nhật ký kiểm toán, tải tài liệu, bộ đánh giá RAG hoặc quy trình lâm sàng. Chỉ dùng trên máy đáng tin cậy, với người có chuyên môn giám sát.

> Khi có tình huống cấp cứu thực tế, hãy làm theo quy trình tại cơ sở và liên hệ nhân viên y tế đủ chuyên môn.

Ứng dụng đọc `knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt` khi khởi động và không sửa nội dung nguồn.


Toi uu phan hoi: chi muc tu khoa duoc dung mot lan khi khoi dong. Cac doan nguon chi duoc dich khi bam nut, de thao tac dich khong lam cham cau tra loi tra cuu.
