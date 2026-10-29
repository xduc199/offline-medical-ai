# 🩺 Trợ lý AI y tế ngoại tuyến

> **Nghiên cứu, xây dựng hệ thống trợ lý AI ngoại tuyến hỗ trợ tra cứu kiến thức cấp cứu cơ bản và sơ cứu khi không có kết nối Internet.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/LLM-Ollama-111111?logo=ollama&logoColor=white" alt="Ollama" />
  <img src="https://img.shields.io/badge/Ch%E1%BA%BF%20%C4%91%E1%BB%99-Offline%20Local-16803C" alt="Chạy cục bộ" />
  <img src="https://img.shields.io/badge/Tr%E1%BA%A1ng%20th%C3%A1i-Prototype%20n%E1%BB%99i%20b%E1%BB%99-orange" alt="Prototype nội bộ" />
</p>

<p align="center">
  <b>🌐 Không cần gọi dịch vụ AI trên đám mây · 📚 Có hiển thị đoạn nguồn · 🔎 Dùng được để thử nghiệm tra cứu tài liệu</b>
</p>

---

## 📌 Mục lục

- [🎯 Giới thiệu](#-giới-thiệu)
- [🧭 Trạng thái hiện tại](#-trạng-thái-hiện-tại)
- [🧠 Hệ thống hoạt động như thế nào?](#-hệ-thống-hoạt-động-như-thế-nào)
- [🗂️ Cấu trúc dự án](#️-cấu-trúc-dự-án)
- [💻 Yêu cầu môi trường](#-yêu-cầu-môi-trường)
- [🚀 Cài đặt và chạy](#-cài-đặt-và-chạy)
- [💬 Cách sử dụng ứng dụng](#-cách-sử-dụng-ứng-dụng)
- [🧪 Chạy bộ câu hỏi kiểm thử](#-chạy-bộ-câu-hỏi-kiểm-thử)
- [⚙️ Cấu hình](#️-cấu-hình)
- [🩹 Xử lý lỗi thường gặp](#-xử-lý-lỗi-thường-gặp)
- [🛡️ An toàn, quyền riêng tư và phạm vi sử dụng](#️-an-toàn-quyền-riêng-tư-và-phạm-vi-sử-dụng)
- [🧱 Hạn chế hiện tại](#-hạn-chế-hiện-tại)
- [🛣️ Hướng phát triển](#️-hướng-phát-triển)
- [📚 Nguồn tài liệu](#-nguồn-tài-liệu)
- [🤝 Đóng góp và phản hồi](#-đóng-góp-và-phản-hồi)

---

## 🎯 Giới thiệu

**offline-medical-ai** là dự án nghiên cứu xây dựng một trợ lý AI chạy trên máy tính cá nhân, hướng tới hỗ trợ tiếp cận kiến thức y tế cơ sở và sơ cứu trong môi trường không có Internet.

Phiên bản hiện có tập trung vào một nhiệm vụ hẹp và có thể kiểm tra được: **tra cứu, trích xuất và diễn đạt lại thông tin từ tài liệu huấn luyện cấp cứu cơ bản WHO/ICRC Basic Emergency Care (2018)**. Ứng dụng sử dụng một mô hình ngôn ngữ chạy cục bộ thông qua Ollama và hiển thị các đoạn nguồn được truy xuất để người dùng đối chiếu.

### Mục tiêu nghiên cứu

- 📴 Khảo sát khả năng chạy mô hình ngôn ngữ lớn (LLM — Large Language Model) hoàn toàn trên máy cá nhân.
- 📚 Xây dựng bước xử lý tài liệu: văn bản trích xuất, làm sạch và chia thành các đoạn có thông tin trang/dòng.
- 🔎 Thử nghiệm truy xuất thông tin (retrieval) từ kho tài liệu trước khi tạo câu trả lời.
- 🧾 Hiển thị đoạn nguồn để hỗ trợ kiểm tra tính phù hợp của câu trả lời.
- 🧪 Tạo bộ câu hỏi để đánh giá thủ công khả năng tìm đúng nguồn, mức đầy đủ và các lỗi cần xử lý.

> **Lưu ý quan trọng:** phiên bản hiện tại là bản thử nghiệm tra cứu tài liệu (prototype), không phải hệ thống chẩn đoán, phân loại mức độ cấp cứu hoặc đưa ra quyết định điều trị cho một ca bệnh cụ thể.

## 🧭 Trạng thái hiện tại

| Hạng mục | Trạng thái đã xác minh trong mã nguồn |
|---|---|
| Giao diện web đơn giản | ✅ Có, được nhúng trực tiếp trong `app/internal_pilot.py` |
| Máy chủ HTTP cục bộ | ✅ Có, sử dụng thư viện chuẩn của Python |
| Chạy mô hình qua Ollama | ✅ Có tích hợp API cục bộ |
| Kho văn bản WHO/ICRC BEC 2018 đã làm sạch | ✅ Có tệp được ứng dụng đọc khi khởi động |
| Truy xuất theo từ khóa và mở rộng một số cụm tiếng Việt sang tiếng Anh | ✅ Có |
| Hiển thị đoạn nguồn và vị trí tham chiếu | ✅ Có |
| Dịch các đoạn nguồn đã tìm thấy khi người dùng bấm nút | ✅ Có, bản dịch tự động cần đối chiếu |
| Bộ câu hỏi thử nghiệm và chương trình gọi thử API | ✅ Có |
| Tìm kiếm ngữ nghĩa bằng embedding/vector database | ❌ Chưa được triển khai trong ứng dụng hiện tại |
| Bộ phân loại câu hỏi y tế/phi y tế, phân loại cấp cứu | ❌ Chưa được triển khai như một lớp độc lập |
| Hệ thống hỗ trợ quyết định lâm sàng đã được thẩm định | ❌ Không có |
| Chứng nhận an toàn y tế | ❌ Không có |

Trạng thái này mô tả mã nguồn hiện có, không phải lời khẳng định về độ chính xác hay mức an toàn lâm sàng.

## 🧠 Hệ thống hoạt động như thế nào?

Ở phiên bản hiện tại, luồng chính diễn ra như sau:

```text
Người dùng nhập câu hỏi tiếng Việt
                │
                ▼
Chuẩn hóa từ và mở rộng một số cụm tiếng Việt → tiếng Anh
                │
                ▼
Tìm, chấm điểm và chọn tối đa 2 đoạn trong văn bản đã làm sạch
                │
       ┌────────┴─────────┐
       │                  │
Không đủ phù hợp     Có đoạn phù hợp
       │                  │
       ▼                  ▼
Thông báo chưa tìm   Trả lời theo mẫu đặc biệt
được nguồn phù hợp   hoặc gọi Ollama cục bộ
                          │
                          ▼
             Kiểm tra một số lỗi đầu ra,
             mã trích dẫn và cách diễn đạt
                          │
                          ▼
             Hiển thị câu trả lời và đoạn nguồn
                          │
                          ▼
       Người dùng đối chiếu nguyên văn tài liệu
```

### Các thành phần chính

1. **Kho tài liệu:** tệp văn bản đã làm sạch của WHO/ICRC Basic Emergency Care (2018).
2. **Bộ truy xuất từ khóa:** chuẩn hóa chữ, tách từ, dùng trọng số và một bảng mở rộng nhỏ cho một số cách hỏi tiếng Việt. Đây **không phải** bộ tìm kiếm ngữ nghĩa.
3. **Ollama:** cung cấp API cục bộ cho mô hình `qwen2.5:7b-instruct-q4_K_M` theo cấu hình mặc định.
4. **Lớp kiểm tra đầu ra:** kiểm tra một số dấu hiệu hình thức như mã trích dẫn không hợp lệ, văn bản lặp hoặc còn nhiều tiếng Anh. Các kiểm tra này không thể chứng minh nội dung đúng về y khoa.
5. **Giao diện web:** nhận câu hỏi, hiển thị câu trả lời, đoạn nguồn và cung cấp nút dịch đoạn nguồn.
6. **Bộ kiểm thử thủ công:** gửi các câu hỏi mẫu đến API đang chạy, in thời gian phản hồi và nguồn được truy xuất để người đánh giá xem lại.

## 🗂️ Cấu trúc dự án

Các tệp quan trọng đối với việc chạy bản thử nghiệm:

```text
offline-medical-ai/
├── README.md
├── .gitignore
├── app/
│   ├── internal_pilot.py
│   ├── README_internal_pilot.md
│   └── evaluation_questions.json
├── knowledge_base/
│   ├── 01_raw/
│   │   └── WHO/
│   │       └── WHO_ICRC_Basic_Emergency_Care_2018.pdf
│   ├── 02_extracted/
│   │   └── các bản văn bản trích xuất từ PDF
│   ├── 03_cleaned/
│   │   └── WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt
│   └── 05_evaluation/
├── tests/
│   ├── broad_questions_vi.json
│   └── run_broad_questions.py
└── reports/
    └── các báo cáo rà soát và xử lý dữ liệu
```

> Thư mục `knowledge_base/03_cleaned/` hiện có nhiều tệp trung gian của quá trình xử lý văn bản. Ứng dụng chỉ đọc tệp `WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt` nêu trên; các tệp có hậu tố `before_...` không phải tất cả đều cần để khởi chạy. Có thể cần tổ chức lại chúng khi chuẩn hóa kho dữ liệu.

## 💻 Yêu cầu môi trường

| Thành phần | Yêu cầu |
|---|---|
| Hệ điều hành | Windows có PowerShell; có thể chạy trên hệ điều hành khác nếu cài đủ môi trường tương thích |
| Python | **3.12 trở lên** theo hướng dẫn bản thử nghiệm |
| Ollama | Cài đặt và dịch vụ cục bộ đang chạy |
| Mô hình | `qwen2.5:7b-instruct-q4_K_M` theo mặc định |
| Tài liệu đầu vào | Tệp `knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt` phải tồn tại |
| Kết nối Internet | Không cần trong lúc sử dụng sau khi đã cài Python, Ollama, tải mô hình và chuẩn bị dữ liệu |

**Lưu ý về tài nguyên:** mô hình 7B có thể cần dung lượng bộ nhớ và dung lượng lưu trữ đáng kể. Nhu cầu thực tế tùy cấu hình máy, cách lượng tử hóa, số luồng và tải đang chạy. README này không tuyên bố một cấu hình phần cứng tối thiểu đã được đo kiểm.

## 🚀 Cài đặt và chạy

### Bước 1 — Lấy mã nguồn

Mở PowerShell tại nơi bạn muốn lưu dự án, sau đó chạy:

```powershell
git clone https://github.com/xduc199/offline-medical-ai.git
cd offline-medical-ai
```

Nếu bạn đã có dự án trên máy, chuyển đến thư mục dự án đó thay vì clone thêm một bản.

### Bước 2 — Kiểm tra Python

```powershell
python --version
```

Phiên bản cần đáp ứng Python 3.12 trở lên. Nếu lệnh `python` không được nhận diện, cài Python và bảo đảm trình cài đặt đã thêm Python vào `PATH`, sau đó mở lại terminal.

Ứng dụng hiện dùng thư viện chuẩn của Python; không có tệp `requirements.txt` trong cấu trúc đang được tài liệu hóa, vì vậy **không cần chạy `pip install -r requirements.txt` cho bản hiện tại**.

### Bước 3 — Cài Ollama và tải mô hình

Cài Ollama theo hướng dẫn chính thức của dự án Ollama. Sau khi cài đặt, mở PowerShell và tải mô hình mặc định:

```powershell
ollama pull qwen2.5:7b-instruct-q4_K_M
```

Kiểm tra mô hình đã có trên máy:

```powershell
ollama list
```

Trong danh sách cần thấy đúng tên:

```text
qwen2.5:7b-instruct-q4_K_M
```

Nếu Ollama chưa chạy, mở ứng dụng Ollama trước. Có thể kiểm tra API cục bộ bằng:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Nếu mô hình đã có, không cần tải lại. Việc tải mô hình lần đầu cần Internet; khi đã được lưu đầy đủ trên máy, bản thử nghiệm có thể gửi yêu cầu đến Ollama cục bộ.

### Bước 4 — Kiểm tra tệp dữ liệu bắt buộc

Tại thư mục gốc dự án, chạy:

```powershell
Test-Path .\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt
```

Kết quả cần là:

```text
True
```

Nếu kết quả là `False`, ứng dụng sẽ không khởi động được vì không tìm thấy tệp nguồn mà mã nguồn đang tham chiếu. Kiểm tra bạn đang đứng ở đúng thư mục gốc và tệp dữ liệu đã được chuẩn bị đúng vị trí.

### Bước 5 — Khởi chạy ứng dụng

Ở thư mục gốc `offline-medical-ai`, chạy:

```powershell
python .\app\internal_pilot.py
```

Terminal sẽ hiển thị địa chỉ máy chủ, mô hình và số đoạn nguồn đã nạp. Khi máy chủ khởi động thành công, giữ cửa sổ terminal này mở.

### Bước 6 — Mở giao diện

Mở trình duyệt và truy cập:

**http://127.0.0.1:8765**

Bạn sẽ thấy giao diện “WHO/ICRC — Cấp cứu cơ bản | Bản thử nghiệm nội bộ”. Nếu không vào được trang, hãy kiểm tra terminal còn chạy hay đã báo lỗi.

### Bước 7 — Dừng ứng dụng

Quay lại cửa sổ PowerShell đang chạy máy chủ và nhấn:

```text
Ctrl + C
```

Máy chủ sẽ dừng.

## 💬 Cách sử dụng ứng dụng

### 1. Đặt câu hỏi về tài liệu

Nhập câu hỏi cụ thể về nội dung tài liệu. Ví dụ:

- “Tài liệu liệt kê những dấu hiệu nào của sốc?”
- “Tài liệu nêu các dấu hiệu nào của hạ đường huyết?”
- “Theo tài liệu, tài liệu mô tả những bước nào về rắn cắn?”

Những câu hỏi này là ví dụ để kiểm tra khả năng tìm nội dung tài liệu, **không phải hướng dẫn xử trí một trường hợp thực tế**.

### 2. Gửi câu hỏi

Nhấn **Tìm trong tài liệu và hỏi mô hình**. Có thể nhấn `Ctrl + Enter` khi con trỏ đang ở vùng nhập câu hỏi.

Ứng dụng tìm các đoạn phù hợp trong tài liệu trước. Nếu mức phù hợp không đạt ngưỡng được đặt trong mã nguồn, ứng dụng sẽ thông báo chưa tìm thấy nguồn đủ liên quan và không gọi mô hình để tạo câu trả lời.

### 3. Đọc câu trả lời cùng cảnh báo

Câu trả lời có thể kèm cảnh báo nếu ứng dụng phát hiện dấu hiệu đầu ra không đạt một số kiểm tra hình thức. Hãy xem câu trả lời như kết quả thử nghiệm, không phải kết luận y khoa.

### 4. Mở đoạn nguồn để đối chiếu

Trong phần **Các đoạn nguồn gốc (tiếng Anh)**, mở từng mục để xem nội dung đã truy xuất. Tham chiếu thể hiện trang PDF (nếu nhận diện được) và dòng trong tệp văn bản đã làm sạch.

Hãy so sánh từng ý trong câu trả lời với đoạn nguồn. Việc có mã `[S1]`, `[S2]` không đảm bảo nguồn thực sự chứng minh toàn bộ ý được trình bày.

### 5. Dịch đoạn nguồn khi cần

Nhấn **Dịch các đoạn nguồn sang tiếng Việt** để yêu cầu mô hình dịch các đoạn đang hiển thị. Đây là bản dịch tự động của đoạn được truy xuất, không phải bản dịch toàn bộ tài liệu; có thể có lỗi thuật ngữ, thiếu ý hoặc sai điều kiện. Luôn đối chiếu nguyên văn tiếng Anh.

## 🧪 Chạy bộ câu hỏi kiểm thử

Dự án có một script phục vụ rà soát thủ công trên ứng dụng đang chạy.

### Chạy toàn bộ bộ câu hỏi

Mở **một cửa sổ PowerShell thứ hai** tại thư mục gốc, giữ cửa sổ đầu tiên chạy ứng dụng và thực hiện:

```powershell
python .\tests\run_broad_questions.py
```

### Chạy nhanh 3 câu đầu tiên

```powershell
python .\tests\run_broad_questions.py --limit 3
```

### Chỉ định địa chỉ API

```powershell
python .\tests\run_broad_questions.py --url http://127.0.0.1:8765 --limit 3
```

Script sẽ:
- Gọi endpoint kiểm tra trạng thái `/api/health`.
- Gửi các câu hỏi từ `tests/broad_questions_vi.json` đến endpoint `/api/ask`.
- In thời gian phản hồi, câu trả lời, nguồn được truy xuất và cảnh báo (nếu có).
- So sánh trang nguồn mục tiêu trong bộ câu hỏi với các trang của nguồn truy xuất khi dữ liệu kiểm thử có chỉ định.

**Cách đọc kết quả:** `PASS`/ `MISS` kiểm tra sự xuất hiện của trang mục tiêu trong nguồn truy xuất, không phải điểm chính xác y khoa. Chương trình chưa tự động chấm độ đúng, mức đầy đủ, độ an toàn hay mức phù hợp lâm sàng. Cần có người đánh giá đối chiếu từng trường hợp.

Ngoài bộ câu hỏi rộng, `app/evaluation_questions.json` có một số tình huống dùng cho đánh giá nội dung mục tiêu và rà soát thủ công; đây không phải bài kiểm thử tự động hoàn chỉnh.

## ⚙️ Cấu hình

Các biến môi trường được mã nguồn hiện tại hỗ trợ:

| Biến | Giá trị mặc định | Ý nghĩa |
|---|---|---|
| `BEC_PILOT_PORT` | `8765` | Cổng HTTP của ứng dụng |
| `BEC_OLLAMA_MODEL` | `qwen2.5:7b-instruct-q4_K_M` | Tên mô hình đã tải trong Ollama |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Địa chỉ API Ollama cục bộ |

Ví dụ PowerShell khi muốn dùng cổng khác:

```powershell
$env:BEC_PILOT_PORT = "8766"
python .\app\internal_pilot.py
```

Sau đó mở `http://127.0.0.1:8766`.

Ví dụ cấu hình rõ tên mô hình và địa chỉ Ollama:

```powershell
$env:BEC_PILOT_PORT = "8765"
$env:BEC_OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"
$env:OLLAMA_URL = "http://127.0.0.1:11434"
python .\app\internal_pilot.py
```

Các biến môi trường cần được đặt trong cùng cửa sổ PowerShell trước khi chạy chương trình. Mã nguồn hiện cấu hình máy chủ web chỉ lắng nghe tại `127.0.0.1`; không đổi cấu hình thành địa chỉ công khai để mở cho mạng khác.

### Các endpoint cục bộ hiện có

| Đường dẫn | Phương thức | Mục đích |
|---|---|---|
| `/` | `GET` | Hiển thị giao diện web |
| `/api/health` | `GET` | Kiểm tra trạng thái demo, mô hình và dữ liệu |
| `/api/ask` | `POST` | Truy xuất đoạn nguồn và tạo câu trả lời |
| `/api/translate` | `POST` | Dịch tối đa các đoạn nguồn đang được hỗ trợ bởi mã nguồn |

### Nền tảng phân loại yêu cầu (đang phát triển)

Nhánh `feat/hybrid-retrieval-safety-foundation` bổ sung `app/query_triage.py`, một bộ phân loại yêu cầu theo quy tắc từ khóa có thể giải thích. Thành phần này phân biệt lời chào, câu hỏi tra cứu tài liệu, câu hỏi cá nhân cần nhân viên y tế tư vấn, câu hỏi ngoài phạm vi, câu hỏi mơ hồ và các cụm từ *có thể* biểu thị tình huống nguy hiểm.

Đây **không phải** mô hình phân loại cấp cứu đã được kiểm định. Từ khóa có thể gây báo động giả hoặc bỏ sót; không phát hiện được từ khóa không có nghĩa là người dùng an toàn. Trên nhánh phát triển, thành phần đã được gọi trước truy xuất trong `/api/ask`. Các nhánh lời chào, từ khóa có thể nguy hiểm và câu hỏi tư vấn cá nhân được chặn trước khi truy xuất/gọi mô hình; câu hỏi ngoài phạm vi vẫn cần được xác nhận bằng nguồn và gắn cảnh báo. Những quy tắc này chưa được thẩm định y khoa, có thể bỏ sót hoặc báo động giả.

Chạy kiểm thử quy tắc:

```powershell
python -m unittest tests.test_query_triage -v
python -m unittest tests.test_ask_endpoint_triage -v
```

Ví dụ kiểm tra trạng thái:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/health
```

Ví dụ gửi câu hỏi trực tiếp:

```powershell
$body = @{ question = "Tài liệu liệt kê những dấu hiệu nào của sốc?" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8765/api/ask -Method Post -ContentType "application/json; charset=utf-8" -Body $body
```

## 🩹 Xử lý lỗi thường gặp

| Hiện tượng | Nguyên nhân thường gặp | Cách kiểm tra / xử lý |
|---|---|---|
| `python` không được nhận diện | Python chưa cài hoặc chưa có trong `PATH` | Chạy `python --version`, cài Python 3.12+ và mở terminal mới |
| Không tìm thấy tệp văn bản nguồn | Đang chạy ngoài thư mục dự án hoặc thiếu tệp dữ liệu | Chạy `Test-Path .\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt` ở thư mục gốc |
| Không kết nối được Ollama | Ollama chưa chạy hoặc API không ở địa chỉ cấu hình | Kiểm tra `ollama list` và `Invoke-RestMethod http://127.0.0.1:11434/api/tags` |
| Không tìm thấy mô hình | Tên mô hình trong cấu hình chưa được tải | Chạy `ollama pull qwen2.5:7b-instruct-q4_K_M` hoặc đặt `BEC_OLLAMA_MODEL` trùng một mô hình có trong `ollama list` |
| Ollama báo không tìm thấy model | Tên trong `BEC_OLLAMA_MODEL` không khớp tên đã cài | So sánh chính xác tên mô hình trong `ollama list` |
| Trang web không mở được | Máy chủ chưa khởi chạy, đã dừng hoặc cổng đang bị chiếm | Kiểm tra cửa sổ chạy Python và thông báo lỗi; thử `BEC_PILOT_PORT=8766` bằng cú pháp PowerShell ở trên |
| Câu trả lời báo chưa tìm được nguồn | Bộ tìm từ khóa chưa tìm được đoạn đủ phù hợp | Thử diễn đạt lại bằng thuật ngữ xuất hiện trong tài liệu; không xem việc không tìm thấy là bằng chứng tài liệu không có thông tin |
| Câu trả lời trống hoặc có cảnh báo | Mô hình có thể sinh nội dung không đạt kiểm tra hoặc yêu cầu hết thời gian | Đọc đoạn nguồn tiếng Anh; thử lại câu hỏi cụ thể hơn và rà soát model/service |
| Bản dịch không xuất hiện | Dịch thất bại hoặc bộ kiểm tra chất lượng phát hiện dấu hiệu lỗi | Đọc nguồn tiếng Anh; không coi bộ lọc hình thức là xác nhận chất lượng bản dịch |
| Cổng bị sử dụng | Có chương trình khác đang lắng nghe tại cổng 8765 | Đặt `$env:BEC_PILOT_PORT = "8766"` rồi chạy lại |

### Quy trình chẩn đoán nhanh

Chạy theo đúng thứ tự sau để xác định lỗi nằm ở đâu:

```powershell
python --version
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags
Test-Path .\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt
python .\app\internal_pilot.py
```

Nếu vẫn lỗi, ghi lại thông báo đầy đủ từ terminal và các lệnh vừa chạy. Không xóa môi trường, thư mục mô hình hoặc kho dữ liệu để thử sửa lỗi khi chưa xác định nguyên nhân.

## 🛡️ An toàn, quyền riêng tư và phạm vi sử dụng

### ⚠️ Chỉ dùng thử nghiệm nội bộ

Ứng dụng đang ở **Mức 0 — tra cứu tài liệu** trong cách phân loại vận hành nội bộ của dự án. Đây không phải chứng nhận an toàn hoặc phân loại pháp lý.

- Không dùng để chẩn đoán, phân loại cấp cứu, kê đơn, quyết định điều trị hoặc thay thế nhân viên y tế.
- Không dùng câu trả lời tự động làm căn cứ duy nhất cho bất kỳ quyết định chăm sóc người bệnh nào.
- Bản dịch và nội dung sinh tự động có thể bỏ sót phủ định, điều kiện, liều lượng, đơn vị hoặc ngoại lệ.
- Khi gặp tình huống thực tế, làm theo quy trình tại cơ sở và liên hệ nhân viên y tế có chuyên môn.
- Mọi nội dung có ý nghĩa chuyên môn phải được đối chiếu với nguyên văn và được người có chuyên môn đánh giá.

### 🔐 Dữ liệu và quyền riêng tư

Theo mã nguồn hiện tại:
- Máy chủ web chỉ lắng nghe trên địa chỉ loopback `127.0.0.1`.
- Yêu cầu mô hình được gửi đến API Ollama cục bộ, không được thiết kế để gọi dịch vụ AI trên đám mây.
- Ứng dụng không lưu lịch sử trò chuyện theo thiết kế hiện tại và đã tắt ghi log mặc định của máy chủ HTTP.

Tuy vậy, điều này không phải cam kết bảo mật toàn diện: hệ điều hành, Ollama hoặc công cụ khác trên máy vẫn có thể có cơ chế ghi nhận riêng. **Không nhập tên, số hồ sơ, địa chỉ, ảnh, thông tin định danh hay dữ liệu nhạy cảm của người bệnh.** Chỉ chạy trên máy tin cậy.

## 🧱 Hạn chế hiện tại

1. **Truy xuất theo từ khóa:** có thể bỏ lỡ cách diễn đạt tương đương, câu hỏi nhiều ý, nội dung bảng hoặc đoạn nằm ngoài hai kết quả được chọn.
2. **Nguồn còn hẹp:** bản demo tập trung vào một tài liệu WHO/ICRC BEC 2018 đã làm sạch; chưa có quy trình quản trị nhiều nguồn có phiên bản, mức ưu tiên và ngày rà soát.
3. **Câu trả lời phụ thuộc LLM:** mô hình có thể bỏ sót hoặc diễn đạt sai dù đã nhận đoạn nguồn. Mã trích dẫn không tự chứng minh câu trả lời đúng.
4. **Bản dịch chưa được thẩm định:** bộ lọc chỉ phát hiện một số dấu hiệu hình thức, không thay thế thẩm định thuật ngữ y khoa.
5. **Chưa có bộ phân loại ý định và an toàn độc lập:** chưa có lớp riêng để phân biệt câu hỏi thông thường, câu hỏi y tế, tình huống nguy cấp, câu hỏi ngoài phạm vi và câu hỏi mơ hồ.
6. **Đánh giá còn thủ công:** script đo thời gian và hiển thị nguồn, nhưng không cung cấp điểm độ chính xác, độ bao phủ, độ an toàn hay kết quả đánh giá lâm sàng tự động.
7. **Chưa có triển khai thực tế:** không có tài khoản, phân quyền, giám sát vận hành, quản trị tài liệu hoàn chỉnh hoặc xác nhận độc lập để sử dụng lâm sàng.

## 🛣️ Hướng phát triển

Các mục dưới đây là **đề xuất nghiên cứu**, không phải chức năng đã hoàn thành:

- [ ] Chuẩn hóa cấu trúc kho dữ liệu, loại bỏ bản trung gian trùng lặp khỏi luồng sử dụng chính và lập danh mục nguồn.
- [ ] Thiết kế truy xuất kết hợp từ khóa và ngữ nghĩa, đo lường chất lượng lấy đoạn trước khi chọn phương án.
- [ ] Bổ sung phân loại câu hỏi: trong phạm vi / ngoài phạm vi / mơ hồ / tình huống có nguy cơ cao.
- [ ] Xây dựng lớp an toàn dựa trên quy tắc kiểm tra được, ưu tiên nhận diện dấu hiệu cảnh báo và khuyến nghị liên hệ trợ giúp phù hợp; không giao toàn bộ quyết định an toàn cho LLM.
- [ ] Tăng khả năng truy nguyên: lưu phiên bản nguồn, trang, vị trí đoạn, thời điểm rà soát và liên kết giữa từng ý trả lời với bằng chứng.
- [ ] Xây dựng bộ đánh giá có đáp án tham chiếu, chấm độ đúng nguồn, độ đầy đủ, mức bịa thông tin, độ an toàn, độ trễ và nhu cầu tài nguyên.
- [ ] Nhờ người có chuyên môn y tế rà soát độc lập bộ câu hỏi và đầu ra trước khi mở rộng phạm vi.
- [ ] Đo kiểm nhiều mô hình và các phương án lượng tử hóa trên thiết bị mục tiêu trước khi đề xuất cấu hình triển khai.

Nên triển khai theo từng giai đoạn: **độ tin cậy của dữ liệu → chất lượng truy xuất → an toàn đầu ra → đánh giá độc lập → mới cân nhắc mở rộng chức năng**.

## 📚 Nguồn tài liệu

Tài liệu được dùng trong bản thử nghiệm hiện tại:

- **WHO/ICRC Basic Emergency Care: Approach to the Acutely Ill and Injured (2018)** — tài liệu huấn luyện cấp cứu cơ bản được lưu trong cây dữ liệu của dự án tại `knowledge_base/01_raw/WHO/WHO_ICRC_Basic_Emergency_Care_2018.pdf`.
- Tệp văn bản trích xuất và làm sạch dùng khi khởi chạy nằm ở `knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt`.

Tài liệu gốc được tạo bởi bên thứ ba. Trước khi công khai repository hoặc phân phối bản PDF/văn bản trích xuất, cần kiểm tra giấy phép và điều kiện tái phân phối áp dụng cho các tệp đó. Việc đặt một tệp trong repository không tự tạo ra quyền phân phối tệp ấy.

## 🤝 Đóng góp và phản hồi

Đối với báo lỗi hoặc đề xuất cải tiến, hãy cung cấp:

1. Hệ điều hành, phiên bản Python, phiên bản Ollama và tên mô hình.
2. Các lệnh đã chạy và thông báo lỗi đầy đủ.
3. Câu hỏi thử nghiệm, mã nguồn được truy xuất và cảnh báo tương ứng — chỉ sử dụng nội dung mẫu, không gửi dữ liệu người bệnh.
4. Hành vi mong đợi so với kết quả thực tế.

Mọi thay đổi liên quan đến hướng dẫn y tế, quy tắc an toàn hoặc nội dung nguồn phải được ghi rõ lý do, nguồn đối chiếu và người rà soát. Không xem việc một thay đổi chạy được về mặt kỹ thuật là bằng chứng rằng nó an toàn về mặt chuyên môn.

---

<p align="center">
  <b>🧪 Dự án nghiên cứu đang phát triển — ưu tiên khả năng truy nguyên, kiểm chứng và an toàn.</b>
</p>
