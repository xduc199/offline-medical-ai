# Báo cáo follow-up hiệu năng — 2026-10-29

## Phạm vi và cấu hình

Đo một request có inference thật và ba smoke request không gọi model. Không chạy benchmark 24 lượt lặp. API cục bộ trả `ok=true` tại `127.0.0.1:8765` trước khi gửi câu hỏi. Model Ollama là `qwen2.5:7b-instruct-q4_K_M`; retrieval keyword, semantic index chưa nạp; corpus nạp một nguồn WHO/ICRC với 1.496 chunks.

Nhánh `fix/pilot-answer-quality`, HEAD `f0d83ae`; worktree đã dirty trước đó và được giữ nguyên. Các số bên dưới là phép đo trên máy hiện tại, không phải số liệu của commit sạch độc lập.

## Các request API

| Trường hợp | HTTP | Tổng latency | Số vòng sinh model | Kết quả |
|---|---:|---:|---:|---|
| B07 — tóm tắt bỏng, có nguồn | 200 | **35.878 s** | 2 (draft + một repair) | Validator vẫn thấy `uncited_claim` và cảnh báo translation; câu trả lời bị ẩn. |
| B02 — ABCDE, bằng chứng chi tiết một phần | 200 | Không đo riêng | 0 | Nhánh keyword đặc biệt trả danh sách năm tên từ PDF p. 221 và nêu giới hạn nguồn. |
| Không có bằng chứng cho câu hỏi liều thuốc/appendicitis | 200 | **0.390 s** | 0 | Không nguồn, `out_of_scope`, không gọi model. |
| Tình huống khó thở khẩn cấp | 200 | **0.381 s** | 0 | Chuyển thẳng sang `possible_emergency`; không retrieval/model. |

35.878 giây là latency end-to-end của request B07 gồm xử lý API, hai vòng sinh và validation; ứng dụng không xuất timing riêng cho retrieval, từng lần Ollama hoặc validation. Không có thống kê P50/P95 đáng tin từ một request. B02 không được bấm giờ riêng. Các request không gọi model không đại diện cho thời gian inference.

Mỗi lần gọi `/api/chat` đặt timeout 240 giây. Không ghi nhận timeout trong lượt B07. Log tạm xác nhận hai kết quả sinh; báo cáo không lưu draft hoặc ngữ cảnh nguồn.

## Benchmark retrieval độc lập

Lệnh `python -m tests.evaluate_retrieval --method keyword --top-k 5` trên `tests/broad_questions_vi.json`:

| Số câu | Số câu có nhãn trang | Recall@5 | MRR | HitRate@5 | Latency truy xuất trung bình |
|---:|---:|---:|---:|---:|---:|
| 8 | 7 | 1.000 | 0.929 | 1.000 | 0.002 s |

Đây là benchmark keyword retrieval trực tiếp theo trang được gán nhãn; không đo endpoint ABCDE special route, generation, độ hỗ trợ ngữ nghĩa hoặc an toàn lâm sàng.

## Tài nguyên máy quan sát được

- Ollama dùng model 5.2 GB theo `ollama ps`, context 4096, runner `llamacpp`, bộ xử lý báo `18%/82% CPU/GPU` (tỷ lệ xử lý, không phải phép đo utilization hoặc VRAM).
- Windows nhận diện NVIDIA GeForce RTX 3060 Laptop GPU; `nvidia-smi` không có sẵn nên không thu được VRAM đã cấp, VRAM cực đại hoặc mức sử dụng GPU độc lập.
- Không đo được RAM tiến trình, nhiệt độ, token đầu vào/đầu ra hoặc thời gian từng vòng sinh. API hiện không cung cấp các số liệu đó.
- Cấu hình mã để Ollama tự chọn backend; không thay model, GPU flag hay context length trong lượt benchmark này.
- Sau các phép đo, pilot do lượt kiểm tra khởi chạy đã được dừng; cổng 8765 hiện đóng.

## So sánh và giới hạn

Báo cáo cũ `performance_benchmark_20261029.md` ghi **0/24** request vì API khi ấy chưa chạy; không có baseline latency thực tế trong báo cáo đó. Mô tả lịch sử trong yêu cầu nêu khoảng 9–10 giây cho một lần gọi trực tiếp và khoảng 70 giây cho request hoàn chỉnh, nhưng đó là số tham khảo từ cấu hình/lượt khác, không phải benchmark đối chứng có cùng câu hỏi, số lần gọi, cache và tải máy. Vì vậy không kết luận máy nhanh hơn hoặc chậm hơn từ phép so sánh này.

Một request B07 duy nhất cần hai vòng sinh và vẫn bị từ chối, nên latency không thể được đánh đổi lấy việc nới validator. Chưa có đủ mẫu để ước lượng phân phối thời gian, hiệu năng GPU hay chất lượng model.

## Đề xuất đo tiếp

1. Chỉ sau khi có tập đánh giá được chốt, đo từng pha retrieval, mỗi vòng inference, validation và tổng request bằng instrumentation có kiểm soát.
2. Thu token/thời gian từ metadata Ollama nếu endpoint cung cấp đáng tin cậy; thu VRAM bằng công cụ NVIDIA phù hợp trước và sau request.
3. Báo rõ cache hit/miss và không trộn cache hit với inference mới.
4. Giữ nguyên model và tham số khi so sánh cấu hình; đánh giá chất lượng song song để không tối ưu latency bằng cách hạ tiêu chí nguồn.

Báo cáo này là file mới; báo cáo cũ và các artifact có sẵn không bị ghi đè. Không đổi nhánh, commit, push hoặc tạo PR.
