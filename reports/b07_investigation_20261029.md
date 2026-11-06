# Điều tra B07: bỏng vẫn bị ẩn — 2026-10-29

## Tóm tắt

B07 cũ bị ẩn vì hai loại lỗi cùng tồn tại: đầu ra có ký tự Hán chưa được dịch, và lần sửa lặp lại nội dung lỗi rồi thêm một ghi chú không citation. Lượt B07 ban đầu còn bị validator báo `uncited_claim` cho câu dẫn trung tính ở dòng 1; đây là false positive của parser. Việc bỏ false positive này không đủ để chấp nhận bản trả lời: cảnh báo bản địa hóa vẫn hợp lệ, và có ít nhất một claim về “chấn thương do cháy nổ” không được đoạn đã trích hỗ trợ như đã viết.

Sau khi sửa parser, prompt, localizer và diagnostics, đã chạy đúng **một** request B07 mới. API trả HTTP 200 sau **5.699 giây**, nhưng trả thông báo lỗi chung từ nhánh Ollama trước khi nhận đầu ra model. Vì thế lần mới không kiểm tra được citation/localization, không sinh được generation diagnostic record, và không chứng minh B07 đã khắc phục. Không gửi lại request model.

## Trạng thái và bằng chứng được đọc

- Nhánh `fix/pilot-answer-quality`, HEAD `f0d83ae`; worktree đã có thay đổi tracked và artifact untracked trước khi bắt đầu. Giữ nguyên toàn bộ, không đổi nhánh hoặc thao tác Git phá hủy.
- Đã đọc `reports/answer_quality_review_20261029_followup.md`, `reports/performance_benchmark_20261029_followup.md` và diff trong validator, pilot, cùng các test liên quan.
- Log B07 cũ còn tại `C:\Users\Admin\AppData\Local\Temp\bec_generation_review_98d85ae299de461d99f4ea641c44c1bd.jsonl`. Log chứa hai output thô, ID/trang nguồn và lỗi; **không chứa câu hỏi, prompt hay văn bản nguồn**.
- `reports/answer_quality_candidates_b05_b07_followup_20261029.json` có record B07 với câu hỏi `Tóm tắt các nội dung chính về bỏng trong tài liệu.`, S1 p. 52, S2 p. 71. Hai đoạn lưu ở capture có đúng page/start/end và văn bản trùng từng ký tự với chunks hiện nạp (`52:2700–2734`, `71:4064–4094`). Đây là cách khôi phục nguồn từ artifact/corpus; trace B07 tự nó chỉ xác nhận ID và trang, nên không thể chứng minh byte-for-byte nội dung prompt lúc chạy.
- `reports/generation_diagnostics_api_20261029.jsonl` là request khác: nguồn p. 48–49, không phải B07. Không dùng log đó làm bằng chứng cho B07.

### Hai lần sinh trong log B07 cũ

| Trường | Lần 1 | Lần 2 |
|---|---|---|
| Run ID | `1793265199595322600` | `1793265199595322600` |
| Nguồn | S1 p. 52, S2 p. 71 | S1 p. 52, S2 p. 71 |
| Citation validator | `uncited_claim`; chi tiết: đoạn văn dòng 1 chưa có mã | `uncited_claim`; chi tiết: dòng 1 và dòng 23 chưa có mã |
| Bản địa hóa | `translation`; ký tự phát hiện: `破`, `风` | `translation`; cùng ký tự vẫn còn |
| CJK trong system/source | Không có | Không có |
| CJK trong user prompt | Không có | Có `破`, `风` |
| Quyết định | yêu cầu một lần sửa | vẫn lỗi; từ chối hiển thị |

Lần 1 mở đầu bằng `Các nội dung chính về bỏng trong tài liệu bao gồm:`; phần danh sách theo sau có citation. Lỗi ở dòng 1 vì câu dẫn này không nằm trong danh sách intro trung tính cũ. Trong nội dung có cụm `Tiêm phòng破风 and giảm đau cho bỏng [S2]`. Lần 2 lặp lại đoạn đó, rồi thêm ghi chú: `Lưu ý: Đoạn văn "tiêm phòng破风" đã được giữ nguyên vì đây là tên thuốc hoặc thuật ngữ y khoa chưa rõ bản dịch, và đoạn văn có ký tự không phải tiếng Việt đã được loại bỏ.` Ghi chú còn chứa chính ký tự bị cho là đã loại bỏ.

`post_localization_output` bằng `raw_model_output` ở cả hai lần. Trace cho thấy bộ localizer không sửa cụm chữ Hán; cảnh báo Unicode phát hiện đúng vấn đề. Lần 2 có chữ Hán trong user prompt nhưng không có trong system prompt hay source text. Theo code, retry chèn draft bị từ chối vào user prompt; điều này xác nhận ký tự lỗi được đưa lại vào prompt và có thể bị model bắt chước. Đây là cơ chế có bằng chứng, dù không thể khẳng định nó là nguyên nhân duy nhất khiến model lặp lỗi.

**Prompt sửa nguyên văn không được lưu trong log cũ.** Từ code tại luồng retry có thể xác nhận prompt gồm: yêu cầu viết lại bằng tiếng Việt, không sinh Han/Nhật/Hàn, citation từng ý bằng ID hợp lệ, chuyển sang bullet phẳng khi có `uncited_claim`, dịch tiếng Anh, nêu giới hạn nguồn, kèm draft bị từ chối và các chi tiết lỗi. Vì raw user prompt không được lưu, báo cáo không khẳng định đây là bản prompt đã gửi byte-for-byte. CJK counts xác nhận draft chứa ký tự Hán đã xuất hiện trong prompt lần hai.

## Đối chiếu claim với nguồn đã truy xuất

Các trạng thái dưới đây đánh giá nội dung B07 cũ so với hai đoạn đã khớp bằng ID/trang/start/end như trên. “Được hỗ trợ” chỉ nói đoạn có nội dung tương ứng; không phải thẩm định y khoa.

| Khẳng định/ý chính trong draft | ID | Đánh giá theo đoạn nguồn |
|---|---|---|
| “Các nội dung chính … bao gồm” | — | Lời dẫn, không phải hướng dẫn y khoa; không cần citation riêng khi từng ý liệt kê có citation. |
| Tắc nghẽn/khó thở do máu, dịch tiết, nôn, dị vật hoặc sưng đường thở | S1 | **Được hỗ trợ một phần**: đoạn liệt kê máu, dịch tiết, nôn, dị vật và sưng như dấu hiệu/nguyên nhân tắc nghẽn; draft diễn đạt lại thành quan hệ nguyên nhân của “khó thở”. |
| Chấn thương đầu/cổ có thể gây tắc đường thở bởi các yếu tố trên | S1 | **Được hỗ trợ**: đoạn ghi trực tiếp chấn thương đầu/cổ có thể gây tắc do máu, dịch tiết, nôn, dị vật hoặc sưng; đây không nhất thiết là nội dung riêng về bỏng. |
| Chấn thương do cháy nổ gây sưng đường thở | S1 | **Không được hỗ trợ như đã viết**: nguồn nói tổn thương do hít phải khói/nhiệt từ bỏng có thể gây sưng, không nói “chấn thương do cháy nổ”. |
| Bỏng nặng trên 15% cơ thể cần chuyển nhanh | S2 | **Được hỗ trợ**: nguồn nêu “serious burns to >15% of body”. |
| Bỏng ở tay, mặt, vùng bẹn, khớp hoặc bỏng vòng cần chuyển nhanh | S2 | **Được hỗ trợ**: khớp với danh sách nguồn. |
| Tổn thương hít phải, bỏng kèm chấn thương khác cần chuyển nhanh | S2 | **Được hỗ trợ**: khớp với danh sách nguồn. |
| Bỏng ở “người nhỏ” hoặc người già | S2 | **Được hỗ trợ một phần**: nguồn nói “very young or elderly”; “người nhỏ” không chuyển tải rõ “trẻ rất nhỏ”. |
| Bệnh mạn tính trước bỏng, như đái tháo đường | S2 | **Được hỗ trợ một phần**: nguồn nói “significant pre-burn illness (such as diabetes)”, không khẳng định mọi bệnh mạn tính. |
| Bù dịch và dự đoán mất dịch tiếp diễn | S2 | **Được hỗ trợ**: nêu trực tiếp trong nguồn. |
| Tiêm vaccine uốn ván và giảm đau | S2 | **Được hỗ trợ về nội dung nguồn**, nhưng bản dịch thực tế `破风 and` không đạt yêu cầu tiếng Việt. |
| Tháo trang sức và kê cao chi bỏng nếu có thể | S2 | **Được hỗ trợ**: nêu trực tiếp trong nguồn. |
| Bỏng có nguy cơ nhiễm trùng cao; làm sạch và băng vết thương cẩn thận | S2 | **Được hỗ trợ**: nêu trực tiếp trong nguồn. |
| Ghi chú tự giải thích cụm Hán là tên thuốc/thuật ngữ và nói ký tự ngoài tiếng Việt đã bị loại bỏ | — | **Không được hỗ trợ**; đây là giải thích do model tự thêm, không có trong nguồn và phần “đã loại bỏ” trái với output đang hiển thị. Ghi chú cũng thiếu citation. |

Validator không nhận văn bản nguồn làm đầu vào để kiểm tra entailment. Test mới dùng câu “chấn thương do cháy nổ…” với `[S1]` để ghi rõ: hàm kiểm cú pháp sẽ chấp nhận citation đó về mặt cấu trúc. Điều này không được coi là claim đã được xác minh; hệ thống hiện chưa có semantic checker tổng quát đáng tin cậy.

## Phân loại nguyên nhân

| Lỗi | Bằng chứng | Phân loại | Nguyên nhân đã xác nhận? | Hướng xử lý |
|---|---|---|---|---|
| Citation syntax | Draft dùng `[S1]`, `[S2]`; trace không báo ID sai, citation sai dạng hay ID ngoài tập nguồn. | Không phải lỗi ở request này | Có, qua log | Không thay cú pháp chuẩn `[S1]`. |
| Markdown/parser | Dòng 1 là câu dẫn, không phải claim y khoa; bị phân tích như đoạn văn thiếu citation. | False positive parser | Có, test tái hiện | Bổ sung nhận diện hẹp cho “Các nội dung chính … trong tài liệu bao gồm:”; bullet thiếu citation vẫn bị chặn. |
| Thiếu citation | Dòng 23 của lần hai là ghi chú giải thích mới, không có citation. | Thiếu citation thật | Có, log + test | Giữ từ chối; prompt cấm ghi chú về dịch thuật/quy trình. |
| Claim không được nguồn hỗ trợ | “Chấn thương do cháy nổ…” không khớp câu nguồn về inhalational injury due to burns. | Lỗi bằng chứng/ngữ nghĩa | Có qua đối chiếu thủ công; validator không phát hiện | Prompt yêu cầu chỉ phát biểu điều kiện đúng như đoạn nguồn; hiện vẫn cần người rà soát vì không có semantic checker tổng quát. |
| Bản địa hóa | `破风` và `and` còn trong câu; ký tự Hán tồn tại cả trước/sau localizer và kích hoạt cảnh báo. | Lỗi đầu ra model + bản địa hóa thất bại | Có, log | Đưa gloss nguồn `tetanus vaccination`/`pain relief`; localizer chỉ thay cụm tiếng Anh khớp nguồn. Không xóa cảnh báo Han. |
| Prompt repair | Prompt template có nhắc lỗi/draft và cấm chữ Hán, nhưng draft lỗi được chèn lại nguyên văn; lần hai còn thêm meta note. Prompt serialized không có trong log cũ. | Lỗi thiết kế prompt và tuân thủ model | Cơ chế echo xác nhận; tác động duy nhất chưa chứng minh | Lược ký tự ngoài bộ chữ khỏi draft nhúng, thay bằng placeholder; cấm lời dẫn/chú thích/meta. Giới hạn một repair. |
| Retrieval | S1 p. 52 là đoạn airway/trauma lẫn một số nhắc đến burn; S2 p. 71 là đoạn burn trực tiếp và hỗ trợ phần lớn danh sách. | Liên quan một phần, có nguy cơ nhiễu ngữ cảnh; không phải thiếu hoàn toàn nguồn | Có qua source comparison | Giữ cảnh báo và yêu cầu model chỉ dùng mệnh đề burn-specific có trong passage. Chưa triển khai semantic/context filter mới. |
| API/Ollama ở lần B07 cũ | Hai model outputs đã có trong log; API trả câu từ chối sau validator. | Không phải lỗi transport ở lượt cũ | Có | Không nới validator. |
| API/Ollama ở lượt B07 mới | HTTP 200, 5.699 s, trả warning chung “Ollama cục bộ không tạo được câu trả lời”; app đi qua nhánh bắt `RuntimeError`. Không có output/validator record. Tags hoạt động, `ollama ps` sau request rỗng; log Ollama có probe GPU lúc khởi động nhưng không có lỗi request tương ứng. | Lỗi trước khi có output model; lỗi Ollama/runtime được xác nhận, nguyên nhân nội tại chưa rõ | Một phần | Thêm diagnostics opt-in cho stage/type/category mà không ghi exception thô. Không chạy lại model theo giới hạn một lần. |

## Sửa đổi và test

- Validator bỏ qua đúng câu dẫn B07 này như phần mở đầu, nhưng vẫn báo `uncited_bullet` cho item thiếu citation và `uncited_claim` cho ghi chú dòng 23. Không thay kiểm tra ID hay chấp nhận citation chung.
- Repair prompt không còn nhúng nguyên văn ký tự Han/Nhật/Hàn từ draft bị từ chối; chúng được thay bằng placeholder. Prompt cấm lời dẫn/ghi chú, nhắc citation từng claim và glossary chính xác theo nguồn cho `tetanus vaccination` → `tiêm phòng uốn ván`, `pain relief` → `giảm đau`.
- Localizer chỉ áp glossary này khi cụm tiếng Anh có trong source text. Không tự “dịch” chuỗi Han. Nếu model tiếp tục sinh Han, cảnh báo vẫn chặn.
- Diagnostics opt-in hiện ghi prompt hệ thống/người dùng, source text, đầu ra và thông tin thất bại an toàn; exception thô không được ghi. README giải thích log chứa nội dung nhạy cảm và chỉ dùng đường dẫn được bảo vệ.
- Thêm test cho intro B07, ghi chú thiếu citation, citation đúng cú pháp nhưng không chứng minh hỗ trợ nguồn, redaction prompt retry, glossary bỏng và log lỗi Ollama không lộ chuỗi exception.

Đã chạy `python -m unittest discover -s tests -p 'test_*.py'`: **138 test đạt**. `py_compile` các module/test liên quan và `git diff --check` đạt (Git chỉ in cảnh báo chuẩn hóa LF/CRLF cho README). Không chạy semantic entailment tự động; không có chuyên gia y tế xác nhận các bản dịch hoặc claim.

## B07 chạy lại sau sửa

Preflight: `/api/health` đạt, model đúng đã cài và Ollama `/api/tags` phản hồi. Gửi một request duy nhất với câu hỏi B07 và source S1 p. 52/S2 p. 71.

| Chỉ số | Kết quả |
|---|---|
| HTTP | 200 |
| Tổng thời gian | 5.699 giây |
| Model output thành công | Không có output được ghi; số HTTP chat attempts nội bộ không xác định |
| Citation validation | Không chạy vì Ollama lỗi trước output |
| Localization | Không chạy vì Ollama lỗi trước output |
| Kết quả API | Thông báo lỗi Ollama chung; không phải quyết định từ chối của validator |
| Trace mới | Không được tạo: lúc request chạy, diagnostics chỉ ghi sau khi model trả output. Sau đó đã sửa code để lần debug sau ghi stage/type/category an toàn; không gửi lại model. |

Log Ollama khả dụng không đủ để quy lỗi cho GPU discovery, tải model hay loại runtime khác. Vì vậy nguyên nhân cụ thể của request mới **chưa xác định**. Không dùng nội dung từ request mới để kết luận prompt đã sửa thành công.

## Tệp được chỉnh trong lượt này

- `app/answer_validation.py`
- `app/internal_pilot.py`
- `app/README_internal_pilot.md`
- `tests/test_answer_validation.py`
- `tests/test_grounded_answer_retry.py`

Các thay đổi sẵn có ở `app/topic_relevance.py`, `tests/test_topic_relevance.py`, `tests/test_hybrid_retrieval_integration.py`, `tests/test_ask_endpoint_triage.py` và các báo cáo/log trước đó được giữ nguyên. Không commit, push, tạo PR, đổi nhánh hoặc xóa dữ liệu.

## Kết luận và giới hạn

False positive ở intro B07 đã được khắc phục có test; retry đã được sửa để không nhắc lại ký tự lỗi và có hướng dẫn dịch cụ thể hơn. Tuy nhiên **chưa thể tuyên bố toàn bộ B07 đã khắc phục**: lượt model mới lỗi trước khi sinh nên chưa kiểm tra được prompt mới với Ollama thật. Bản B07 cũ bị ẩn là quyết định đúng tổng thể vì có ký tự ngoài tiếng Việt, ghi chú không citation và claim “cháy nổ” không được passage hỗ trợ; riêng lỗi `uncited_claim` ở câu mở đầu là sai phân loại.

Hạn chế còn lại: chưa có kiểm chứng ngữ nghĩa tự động tổng quát, các đánh giá chưa được chuyên gia y tế chấm, và lỗi runtime Ollama ở request mới chưa có nguyên nhân nội tại. Không gửi thêm câu hỏi model trong lượt này.
