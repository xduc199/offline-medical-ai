# Benchmark hiệu năng AI y tế ngoại tuyến — 2026-10-29

## Kết quả thực thi

**Benchmark endpoint chưa chạy được.** API tại `http://127.0.0.1:8765` không có listener; kiểm tra `GET /api/health` không kết nối được. Theo yêu cầu, không khởi chạy API và không gửi request hỏi đáp.

- Request khởi động dự kiến: 2; đã gửi: **0/2**.
- Request đo chính thức dự kiến: 24 (B01–B08, mỗi câu 3 lượt); đã gửi: **0/24**.
- Không có response để tính latency, độ dài câu trả lời, trạng thái ẩn, hoặc tỷ lệ thành công.
- Không ghi dữ liệu thô benchmark và không sửa các capture hiện có.

## Cấu hình được xác minh

| Thành phần | Trạng thái tại thời điểm kiểm tra |
|---|---|
| Nhánh Git | `fix/pilot-answer-quality` |
| API | `127.0.0.1:8765` không chạy; không có listener và `/api/health` không kết nối được |
| Model cấu hình trong mã | `qwen2.5:7b-instruct-q4_K_M` (giá trị mặc định; `BEC_OLLAMA_MODEL` không được đặt) |
| Model Ollama đã cài | `qwen2.5:7b-instruct-q4_K_M`, Q4_K_M, 7.6B tham số |
| Trạng thái model Ollama | Model có trong `/api/tags`; `ollama ps` không có model đang chạy |
| Ollama URL | `http://127.0.0.1:11434` (mặc định; `OLLAMA_URL` không được đặt), endpoint tag phản hồi |
| Cổng pilot | 8765 (mặc định; `BEC_PILOT_PORT` không được đặt) |
| `BEC_OLLAMA_NUM_GPU` | Không được đặt; mã không ép `num_gpu`, để Ollama tự chọn backend |
| CPU | Intel Core i5-12500H, 12 lõi / 16 luồng |
| RAM vật lý | 15.7 GB theo Windows |
| GPU | Windows nhận diện NVIDIA GeForce RTX 3060 Laptop GPU và Intel Iris Xe; `nvidia-smi` không có trong PATH |
| GPU đang được Ollama dùng | Chưa xác định: không có model đang chạy để kiểm tra. Giá trị AdapterRAM do Windows báo không được coi là VRAM runtime |
| Vector index mặc định | `vector_db/who_icrc_bec_bge_m3.json` không tồn tại; không có biến môi trường override. Theo mã hiện tại, ứng dụng sẽ dùng keyword retrieval và topic filtering khi khởi chạy với cấu hình này |

Giá trị model, URL và cổng ở trên là cấu hình mặc định của mã vì các biến môi trường tương ứng không được đặt; chúng không phải bằng chứng rằng một tiến trình API đang dùng các giá trị đó.

## Endpoint và bộ câu hỏi

Mã endpoint nhận `POST /api/ask` với JSON `{"question": "..."}`. Tám câu hỏi được chọn nguyên văn từ `reports/answer_quality_candidates_b05_b07_followup_20261029.json`:

| Mã | Câu hỏi |
|---|---|
| B01 | Theo tài liệu, tổng quan về xử trí khó thở là gì? |
| B02 | Tóm tắt các bước đánh giá người bệnh chấn thương. |
| B03 | Theo tài liệu, những dấu hiệu và nguyên nhân nào liên quan đến sốc? |
| B04 | Tài liệu hướng dẫn gì về rắn cắn, từ đánh giá đến xử trí? |
| B05 | Tổng hợp cách xử trí co giật ở người lớn và trẻ em theo tài liệu. |
| B06 | Tài liệu trình bày những bước đánh giá ban đầu người bệnh cấp cứu nào? |
| B07 | Tóm tắt các nội dung chính về bỏng trong tài liệu. |
| B08 | Theo tài liệu, cần đánh giá và xử trí người bệnh bị chảy máu như thế nào? |

Không dùng dữ liệu người bệnh thật. Không gọi `tests.capture_answer_quality_candidates`: script đó lưu toàn bộ câu trả lời và nguồn, đồng thời mặc định ghi đè `reports/answer_quality_candidates.json`.

## Bảng các lượt dự kiến

Các lượt dưới đây **không được gửi**; dấu gạch ngang là số liệu chưa đo, không phải 0 giây.

| Request | Mã câu hỏi | Lượt | Trạng thái | HTTP | Latency (s) | Độ dài câu trả lời |
|---|---:|---:|---|---:|---:|---:|
| B01-1 | B01 | 1 | Chưa gửi — API không chạy | — | — | — |
| B01-2 | B01 | 2 | Chưa gửi — API không chạy | — | — | — |
| B01-3 | B01 | 3 | Chưa gửi — API không chạy | — | — | — |
| B02-1 | B02 | 1 | Chưa gửi — API không chạy | — | — | — |
| B02-2 | B02 | 2 | Chưa gửi — API không chạy | — | — | — |
| B02-3 | B02 | 3 | Chưa gửi — API không chạy | — | — | — |
| B03-1 | B03 | 1 | Chưa gửi — API không chạy | — | — | — |
| B03-2 | B03 | 2 | Chưa gửi — API không chạy | — | — | — |
| B03-3 | B03 | 3 | Chưa gửi — API không chạy | — | — | — |
| B04-1 | B04 | 1 | Chưa gửi — API không chạy | — | — | — |
| B04-2 | B04 | 2 | Chưa gửi — API không chạy | — | — | — |
| B04-3 | B04 | 3 | Chưa gửi — API không chạy | — | — | — |
| B05-1 | B05 | 1 | Chưa gửi — API không chạy | — | — | — |
| B05-2 | B05 | 2 | Chưa gửi — API không chạy | — | — | — |
| B05-3 | B05 | 3 | Chưa gửi — API không chạy | — | — | — |
| B06-1 | B06 | 1 | Chưa gửi — API không chạy | — | — | — |
| B06-2 | B06 | 2 | Chưa gửi — API không chạy | — | — | — |
| B06-3 | B06 | 3 | Chưa gửi — API không chạy | — | — | — |
| B07-1 | B07 | 1 | Chưa gửi — API không chạy | — | — | — |
| B07-2 | B07 | 2 | Chưa gửi — API không chạy | — | — | — |
| B07-3 | B07 | 3 | Chưa gửi — API không chạy | — | — | — |
| B08-1 | B08 | 1 | Chưa gửi — API không chạy | — | — | — |
| B08-2 | B08 | 2 | Chưa gửi — API không chạy | — | — | — |
| B08-3 | B08 | 3 | Chưa gửi — API không chạy | — | — | — |

## Tổng hợp chỉ số

| Chỉ số | Kết quả |
|---|---|
| Số request đo được | 0/24 |
| Trung bình / P50 / P95 | N/A — không có mẫu |
| Min / Max | N/A — không có mẫu |
| Tỷ lệ thành công | N/A — không có request được gửi (không phải 0%) |
| Timeout / lỗi HTTP / câu trả lời bị ẩn | Không có quan sát; không thể suy ra tỷ lệ |
| So sánh tốc độ giữa B01–B08 | Không thể thực hiện |
| Request chậm bất thường | Không có dữ liệu để xác định |

P95 và các thống kê thời gian không có độ tin cậy nào ở lần kiểm tra này vì cỡ mẫu bằng 0.

## Cache và các giai đoạn thời gian

Mã có cache kết quả trong tiến trình: `_ANSWER_CACHE` giữ tối đa 128 kết quả, khóa theo câu hỏi và chỉ số các chunk đã truy xuất. API không trả thông tin cache hit. Nếu chạy đủ ba lượt giống nhau cho mỗi câu, hai lượt sau nhiều khả năng là cache hit, không phải inference mới. Không xóa hoặc thay đổi cache. Hai warm-up tương lai nên dùng câu khác B01–B08 để tránh làm ấm cache cho nhóm đo.

Mã nguồn cho thấy các giai đoạn có thể nằm trong tổng latency:

1. `retrieve`: keyword retrieval; nếu có vector index hợp lệ thì thêm embedding search, fusion và topic filtering. Với index mặc định hiện không có, đường chạy dự kiến là keyword retrieval và topic filtering.
2. `call_model_uncached`: prompt, gọi Ollama, localization và các validator; có thể có một lần retry nếu lần đầu không đạt.
3. `ollama_chat`: gọi `/api/chat`; có thể thử lại một lần sau một số lỗi HTTP 5xx.
4. Endpoint `/api/ask`: tổng thời gian từ nhận câu hỏi tới khi gửi JSON response.

Ứng dụng hiện không ghi thời gian riêng cho retrieval, topic filtering, mỗi lần inference hay validation/retry. Chỉ có thể lấy tổng thời gian HTTP từ ngoài endpoint; không có số liệu thực tế để quy chậm cho một thành phần. Không kết luận inference, retrieval hoặc retry là nút thắt dựa trên mã nguồn một mình.

## Giới hạn và bước tiếp theo

- Cần khởi chạy đúng một API theo README từ thư mục gốc dự án: `python .\app\internal_pilot.py`. Ollama đang phản hồi và model đã cài; lệnh này chưa được chạy trong lần benchmark này.
- Sau khi API có mặt, xác minh `/api/health` cho model và retrieval mode trước khi đo. Gửi 2 warm-up riêng, sau đó 24 request tuần tự; lưu status, elapsed, answer length, warning/ẩn và không lưu answer/source body.
- Báo rõ lượt cache hit có thể xảy ra. Không xóa cache; nếu cần inference-only latency, cần một thiết kế đo riêng được phê duyệt thay vì diễn giải cache hit thành tốc độ model.
- Để phân rã latency, cần instrumentation riêng cho retrieval, embedding, từng `ollama_chat`, validation/retry và tổng endpoint. Không có số đo hiện tại để đề xuất tối ưu thành phần nào.
- HTTP thành công, khi có, chỉ phản ánh request hoàn tất; không xác nhận câu trả lời đúng hoặc an toàn về y khoa.

## Git

Không sửa mã nguồn, không đổi nhánh, không commit, push hoặc tạo PR. Báo cáo này là file mới; các thay đổi đang có và báo cáo untracked khác được giữ nguyên.
