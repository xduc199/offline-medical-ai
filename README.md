# Trợ lý AI y tế ngoại tuyến

> **Nghiên cứu và xây dựng trợ lý AI chạy cục bộ, hỗ trợ tra cứu kiến thức cấp cứu cơ bản từ tài liệu WHO/ICRC khi không có Internet.**

<p align="center"><b>Truy xuất có nguồn · Chạy trên máy cá nhân · Có công cụ đánh giá</b></p>

**Mục lục:** [Giới thiệu](#giới-thiệu) · [Cài đặt](#cài-đặt) · [Sử dụng](#sử-dụng) · [Đánh giá](#đánh-giá) · [An toàn và giới hạn](#an-toàn-và-giới-hạn)

---

## Giới thiệu

**offline-medical-ai** là dự án nghiên cứu một trợ lý hỏi đáp dựa trên tài liệu (document-grounded QA — tạo câu trả lời dựa trên nguồn được truy xuất), hướng tới môi trường không có kết nối Internet.

Bản thử nghiệm tập trung vào tài liệu **WHO/ICRC *Basic Emergency Care: Approach to the Acutely Ill and Injured* (2018)**. Ứng dụng truy xuất đoạn văn bản liên quan, có thể chuyển nội dung sang mô hình ngôn ngữ chạy cục bộ qua Ollama và hiển thị nguồn để người dùng đối chiếu.

### Mục tiêu

- Khảo sát khả năng chạy mô hình ngôn ngữ lớn (LLM — Large Language Model) trên máy cá nhân.
- Xử lý tài liệu thành văn bản có thể tìm kiếm, giữ thông tin tham chiếu trang/dòng.
- Thử nghiệm truy xuất theo từ khóa và, trong phiên bản có chỉ mục phù hợp, truy xuất kết hợp ngữ nghĩa.
- Hiển thị bằng chứng truy xuất và rà soát một số lỗi đầu ra.
- Xây dựng bộ câu hỏi và chỉ số để đánh giá bước truy xuất.

> **Phạm vi:** đây là prototype phục vụ nghiên cứu và thử nghiệm kỹ thuật, không phải sản phẩm y tế đã được thẩm định.

## Trạng thái chức năng

| Thành phần | Trạng thái được mô tả trong dự án |
|---|---|
| Giao diện web và HTTP API cục bộ | Đã có trong `app/internal_pilot.py` |
| Kết nối Ollama cục bộ | Đã tích hợp; cần cài và tải model trên máy |
| Truy xuất từ khóa và hiển thị nguồn | Đã có |
| Quy tắc phân loại yêu cầu | Có prototype dựa trên từ khóa; chưa phải bộ phân loại y tế đã kiểm định |
| Truy xuất embedding + RRF | Có đường xử lý tùy chọn; cần chỉ mục hợp lệ để sử dụng |
| Benchmark Recall@k/MRR | Có script đánh giá truy xuất |
| Đánh giá độ đúng và an toàn lâm sàng độc lập | Chưa được xác lập |

Các trạng thái trên là mô tả kỹ thuật của mã nguồn, không phải bằng chứng về độ chính xác y khoa. Kết quả thực tế cần kiểm tra trên đúng commit và môi trường triển khai.

## Kiến trúc tổng quát

```text
Câu hỏi tiếng Việt
       │
       ▼
Chuẩn hóa / phân loại theo quy tắc
       │
       ▼
Truy xuất đoạn nguồn từ kho tài liệu
       │
       ├── Không đủ nguồn phù hợp ──► Thông báo chưa đủ bằng chứng
       │
       ▼
Xây dựng ngữ cảnh + gọi Ollama cục bộ
       │
       ▼
Kiểm tra một số lỗi hình thức / tham chiếu
       │
       ▼
Câu trả lời + đoạn nguồn để đối chiếu
```

Tùy cấu hình, bước truy xuất có thể dùng từ khóa hoặc hợp nhất thứ hạng từ khóa và vector bằng **Reciprocal Rank Fusion (RRF — hợp nhất thứ hạng)**. Điểm tương đồng và mã trích dẫn không tự chứng minh nội dung là đúng.

## Cấu trúc dự án

Một số đường dẫn chính:

```text
offline-medical-ai/
├── app/
│   ├── internal_pilot.py
│   ├── README_internal_pilot.md
│   ├── evaluation_questions.json
│   └── ...
├── knowledge_base/
│   ├── 01_raw/       # Tài liệu đầu vào
│   ├── 02_extracted/ # Văn bản trích xuất
│   ├── 03_cleaned/   # Văn bản đã làm sạch
│   └── 05_evaluation/
├── tests/            # Bộ câu hỏi, benchmark và kiểm thử
├── reports/          # Báo cáo đánh giá / rà soát
└── README.md
```

Ứng dụng cần tệp văn bản đã làm sạch tại:

`knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt`

Các thư mục và tệp phụ có thể thay đổi theo phiên bản. Nếu đường dẫn không tồn tại trong bản clone của bạn, hãy kiểm tra cây thư mục và cấu hình được mã nguồn hiện tại sử dụng.

## Yêu cầu

- Windows + PowerShell là môi trường hướng dẫn chính; hệ điều hành khác cần điều chỉnh lệnh tương ứng.
- Python 3.12 trở lên theo cấu hình hướng dẫn hiện tại.
- [Ollama](https://ollama.com/) đã cài đặt và chạy trên máy.
- Model mặc định: `qwen2.5:7b-instruct-q4_K_M`.
- Tệp dữ liệu đã làm sạch nêu trên có mặt trong cây dự án.

Model 7B cần tài nguyên bộ nhớ và lưu trữ đáng kể. Hiệu năng phụ thuộc phần cứng, lượng tử hóa, thiết lập runtime và độ dài ngữ cảnh; cấu hình tối thiểu chưa được xác lập trong README này.

## Cài đặt

### 1. Clone repository

```powershell
git clone https://github.com/xduc199/offline-medical-ai.git
cd offline-medical-ai
```

Nếu dự án đã có trên máy, chuyển đến thư mục dự án hiện tại thay vì clone thêm một bản.

### 2. Kiểm tra Python

```powershell
python --version
```

Đảm bảo phiên bản đáp ứng yêu cầu. Nếu không nhận diện được lệnh `python`, cài Python và kiểm tra biến môi trường `PATH`.

### 3. Cài Ollama và tải model

Cài Ollama theo hướng dẫn chính thức, sau đó chạy:

```powershell
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama list
```

Kiểm tra API Ollama cục bộ:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Lần tải model đầu tiên cần Internet. Sau khi model và dữ liệu đã có trên máy, luồng xử lý có thể chạy cục bộ; không tải model mới trong lúc sử dụng thông thường.

### 4. Kiểm tra dữ liệu nguồn

Tại thư mục gốc:

```powershell
Test-Path .\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt
```

Kết quả mong đợi là `True`. Nếu là `False`, kiểm tra thư mục hiện hành, tệp dữ liệu và đường dẫn mà mã nguồn sử dụng.

### 5. Khởi chạy server

```powershell
python .\app\internal_pilot.py
```

Giữ cửa sổ terminal mở sau khi server khởi động. Mở trình duyệt tại:

**http://127.0.0.1:8765**

Dừng ứng dụng bằng `Ctrl + C` trong cửa sổ đang chạy server.

> Nếu ứng dụng báo thiếu tệp hoặc lỗi khởi động, hãy dùng thông báo thực tế từ terminal để chẩn đoán; không tự tạo tệp dữ liệu giả để vượt qua lỗi.

## Sử dụng

1. Mở giao diện tại `http://127.0.0.1:8765`.
2. Nhập câu hỏi cụ thể về nội dung tài liệu.
3. Gửi câu hỏi và chờ kết quả từ ứng dụng.
4. Đọc các đoạn nguồn được truy xuất, đối chiếu nội dung trả lời với nguyên văn.
5. Khi dùng chức năng dịch nguồn, xem bản dịch là hỗ trợ tham khảo và kiểm tra lại thuật ngữ.

Ví dụ câu hỏi dùng để thử nghiệm tra cứu:

- “Tài liệu mô tả những dấu hiệu nào của sốc?”
- “Tài liệu có đề cập những dấu hiệu nào của hạ đường huyết?”
- “Theo tài liệu, nội dung về rắn cắn được trình bày ở đâu?”

Đây là câu hỏi thử hệ thống, không phải hướng dẫn xử trí một trường hợp thực tế.

### API cục bộ

| Endpoint | Phương thức | Mục đích |
|---|---|---|
| `/` | `GET` | Giao diện web |
| `/api/health` | `GET` | Trạng thái ứng dụng, model và chỉ mục |
| `/api/ask` | `POST` | Truy xuất nguồn và xử lý câu hỏi |
| `/api/translate` | `POST` | Dịch các đoạn nguồn theo chức năng hỗ trợ |

Kiểm tra trạng thái:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/health
```

Gửi câu hỏi thử:

```powershell
$body = @{ question = "Tài liệu mô tả những dấu hiệu nào của sốc?" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8765/api/ask -Method Post -ContentType "application/json; charset=utf-8" -Body $body
```

Các endpoint và trường JSON có thể thay đổi giữa các phiên bản; kiểm tra `app/internal_pilot.py` nếu phản hồi khác ví dụ.

## Cấu hình

Các biến môi trường được tài liệu hóa cho bản thử nghiệm:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `BEC_PILOT_PORT` | `8765` | Cổng HTTP của ứng dụng |
| `BEC_OLLAMA_MODEL` | `qwen2.5:7b-instruct-q4_K_M` | Tên model trong Ollama |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | API Ollama |

Ví dụ đổi cổng:

```powershell
$env:BEC_PILOT_PORT = "8766"
python .\app\internal_pilot.py
```

Sau đó mở `http://127.0.0.1:8766`. Biến môi trường cần đặt trong cùng cửa sổ PowerShell trước khi khởi động.

### Truy xuất ngữ nghĩa tùy chọn

Phiên bản có hỗ trợ đường truy xuất embedding có thể kết hợp kết quả vector và từ khóa bằng RRF, nếu chỉ mục hợp lệ đã được tạo. Model embedding và model sinh câu trả lời là hai vai trò khác nhau.

Thiết lập được mô tả trong mã nguồn hiện tại:

```powershell
ollama pull bge-m3
python -m app.build_vector_index --model bge-m3 --batch-size 16
```

Sau khi build, kiểm tra:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/health
```

Nếu trường `semantic_index_loaded` là `true` và `retrieval_mode` là `hybrid_rrf`, ứng dụng báo đã nạp chỉ mục kết hợp. Nếu không, cần xem phản hồi health và log để xác định nguyên nhân. Lệnh, tên trường và đường dẫn chỉ mục cần được đối chiếu với đúng phiên bản mã nguồn.

Tài liệu tham khảo kỹ thuật:
- [Ollama](https://ollama.com/)
- [Ollama Embeddings](https://github.com/ollama/ollama/blob/main/docs/capabilities/embeddings.mdx)
- [BGE-M3 trên Ollama](https://ollama.com/library/bge-m3)

## Đánh giá

### Chạy bộ câu hỏi

Giữ cửa sổ thứ nhất chạy ứng dụng; mở PowerShell thứ hai ở thư mục gốc:

```powershell
python .\tests\run_broad_questions.py
```

Chạy giới hạn ba câu:

```powershell
python .\tests\run_broad_questions.py --limit 3
```

Chỉ định URL:

```powershell
python .\tests\run_broad_questions.py --url http://127.0.0.1:8765 --limit 3
```

Script này phục vụ rà soát nguồn và thời gian phản hồi. Kết quả tìm thấy trang đích không đồng nghĩa với câu trả lời đúng, đầy đủ hoặc an toàn về y khoa.

### Benchmark truy xuất

Nếu các script tương ứng tồn tại trong phiên bản đang dùng, có thể chạy đối chứng từ khóa:

```powershell
python -m tests.evaluate_retrieval --method keyword --top-k 5
```

Với chỉ mục ngữ nghĩa đã sẵn sàng:

```powershell
python -m tests.evaluate_retrieval --method all --require-semantic --top-k 5 --output reports/retrieval_metrics.json
```

Các chỉ số thường được dùng:
- **Recall@k:** tỷ lệ câu hỏi có ít nhất một kết quả liên quan trong top k.
- **MRR (Mean Reciprocal Rank):** đánh giá vị trí của kết quả liên quan đầu tiên.
- **HitRate@k:** tỷ lệ câu hỏi có kết quả mục tiêu xuất hiện trong top k.

Kết quả chỉ có ý nghĩa khi nhãn tham chiếu đủ tốt. Các chỉ số truy xuất không đo trực tiếp độ chính xác của câu trả lời hoặc an toàn lâm sàng.

### Kiểm thử tự động

```powershell
python -m unittest discover -s tests -p "test*.py" -v
```

Chỉ xem CI là đạt khi kiểm tra trạng thái thực tế trong tab **Actions** của GitHub; việc có workflow không đảm bảo mọi lần chạy đều thành công.

## Xử lý lỗi thường gặp

| Vấn đề | Kiểm tra |
|---|---|
| `python` không được nhận diện | Kiểm tra cài đặt Python và `PATH` |
| Thiếu tệp dữ liệu | Kiểm tra thư mục gốc và đường dẫn tệp đã làm sạch |
| Không kết nối được Ollama | Mở Ollama, kiểm tra `ollama list` và API tags |
| Không tìm thấy model | Đối chiếu tên `BEC_OLLAMA_MODEL` với `ollama list` |
| Không mở được giao diện | Xem terminal, kiểm tra server còn chạy và cổng có bị chiếm |
| Không có nguồn phù hợp | Diễn đạt câu hỏi bằng thuật ngữ trong tài liệu; đừng suy ra rằng tài liệu không có thông tin |
| Bản dịch hoặc câu trả lời có cảnh báo | Đối chiếu nguồn gốc; bộ kiểm tra hình thức không bảo đảm nội dung chính xác |
| Chế độ ngữ nghĩa không hoạt động | Kiểm tra chỉ mục, model embedding, đường dẫn và phản hồi `/api/health` |

Chẩn đoán ban đầu:

```powershell
python --version
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags
Test-Path .\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt
```

Nếu vẫn lỗi, giữ nguyên dữ liệu, ghi lại thông báo lỗi đầy đủ và xác định nguyên nhân trước khi thay đổi môi trường.

## An toàn và giới hạn

### Chỉ dùng cho nghiên cứu

- Không dùng ứng dụng để chẩn đoán, phân loại cấp cứu, kê đơn hoặc quyết định điều trị.
- Không dùng câu trả lời làm căn cứ duy nhất cho quyết định chăm sóc người bệnh.
- Nội dung sinh tự động có thể sai hoặc thiếu, ngay cả khi có trích dẫn.
- Bản dịch tự động có thể làm sai thuật ngữ, phủ định, liều lượng, đơn vị hoặc điều kiện.
- Khi gặp tình huống thực tế, hãy liên hệ nhân viên y tế hoặc dịch vụ cấp cứu phù hợp và tuân thủ quy trình tại cơ sở.
- Cần chuyên gia y tế đánh giá độc lập trước khi cân nhắc sử dụng trong môi trường lâm sàng.

### Quyền riêng tư

Ứng dụng được thiết kế để giao tiếp với Ollama cục bộ và hướng tới sử dụng trên máy cá nhân. Tuy nhiên, điều này không thay thế việc rà soát toàn bộ hệ điều hành, phần mềm, cấu hình mạng và cơ chế ghi log.

**Không nhập thông tin định danh hoặc dữ liệu nhạy cảm của người bệnh.** Chỉ chạy trên máy tin cậy; không mở server ra mạng công cộng.

## Hạn chế hiện tại

1. Truy xuất có thể bỏ lỡ cách diễn đạt khác, nội dung bảng hoặc thông tin không nằm trong các đoạn được chọn.
2. Kho tri thức hiện tập trung vào một tài liệu chính; chưa phải một cơ sở tri thức y tế toàn diện.
3. LLM có thể suy diễn vượt nguồn hoặc diễn đạt sai.
4. Kiểm tra mã trích dẫn và các quy tắc đầu ra chỉ phát hiện một số lỗi hình thức, không chứng minh quan hệ giữa từng khẳng định và bằng chứng.
5. Bộ phân loại theo từ khóa có thể báo động giả hoặc bỏ sót.
6. Đánh giá cần nhãn tham chiếu được rà soát; benchmark truy xuất không phải đánh giá lâm sàng.
7. Chưa có cơ sở để tuyên bố hệ thống đã được xác nhận an toàn cho bệnh nhân hoặc sẵn sàng triển khai thực tế.

## Hướng phát triển

Các mục dưới đây là định hướng nghiên cứu, không phải cam kết về tính năng đã hoàn thành:

- [ ] Chuẩn hóa kho dữ liệu, nguồn, phiên bản và quy trình cập nhật.
- [ ] Mở rộng bộ câu hỏi tham chiếu và rà soát nhãn trang/đoạn.
- [ ] So sánh truy xuất từ khóa và hybrid bằng Recall@k, MRR, độ trễ và tài nguyên.
- [ ] Đánh giá mức bám sát nguồn, nội dung không có bằng chứng, độ đầy đủ và chất lượng bản dịch.
- [ ] Kiểm tra false positive/false negative của quy tắc phân loại yêu cầu.
- [ ] Xây dựng quy trình rà soát độc lập với người có chuyên môn y tế.
- [ ] Đo kiểm nhiều model và cấu hình trên phần cứng mục tiêu.
- [ ] Chỉ xem xét mở rộng phạm vi sau khi có kết quả đánh giá đáng tin cậy.

Thứ tự ưu tiên: **chất lượng dữ liệu → chất lượng truy xuất → độ tin cậy của câu trả lời → đánh giá an toàn độc lập → cân nhắc mở rộng**.

## Nguồn tài liệu

- WHO/ICRC, *Basic Emergency Care: Approach to the Acutely Ill and Injured* (2018), được dùng làm nguồn chính cho bản thử nghiệm.
- [Ollama](https://ollama.com/)
- [Ollama Embeddings](https://github.com/ollama/ollama/blob/main/docs/capabilities/embeddings.mdx)
- [BGE-M3 trên Ollama](https://ollama.com/library/bge-m3)

Trước khi phân phối PDF hoặc văn bản trích xuất, hãy xác minh giấy phép và điều kiện tái phân phối của tài liệu nguồn.

## Báo lỗi và phản hồi

Khi báo lỗi, hãy cung cấp thông tin không nhạy cảm:

1. Hệ điều hành, phiên bản Python, Ollama và model.
2. Lệnh đã chạy cùng thông báo lỗi.
3. Câu hỏi thử nghiệm và mã nguồn được truy xuất (đã loại bỏ dữ liệu nhạy cảm).
4. Kết quả mong đợi so với thực tế.

Với thay đổi liên quan đến tri thức y tế hoặc an toàn, cần nêu nguồn đối chiếu và quy trình rà soát. Chạy được về mặt kỹ thuật không đồng nghĩa với an toàn về mặt chuyên môn.

---

<p align="center">
  <b> Dự án nghiên cứu đang phát triển — ưu tiên khả năng kiểm chứng, truy nguyên và an toàn.</b>
</p>
