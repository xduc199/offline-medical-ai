# Bộ phân loại yêu cầu — nền tảng prototype

## Phạm vi

`query_triage.py` cung cấp phân loại yêu cầu dựa trên quy tắc từ khóa để hỗ trợ thiết kế luồng hỏi đáp. Đây không phải mô hình y tế đã được kiểm định, không xác nhận tình trạng cấp cứu và không chẩn đoán.

Các lớp gồm:
- `greeting`: lời chào / cảm ơn.
- `document_lookup`: có vẻ là câu hỏi trong phạm vi tra cứu tài liệu hiện có.
- `out_of_scope`: nội dung y tế hoặc câu hỏi chưa được xác định là nằm trong tài liệu hiện có.
- `possible_emergency`: phát hiện cụm từ có thể biểu thị tình huống nguy hiểm.
- `personal_medical_advice`: câu hỏi về thuốc hoặc tình trạng cá nhân cần người có chuyên môn đánh giá.
- `ambiguous`: đầu vào trống hoặc quá mơ hồ.

## Giới hạn và yêu cầu trước khi tích hợp

1. Quy tắc từ khóa có thể bỏ sót tình huống nguy hiểm, đặc biệt khi người dùng diễn đạt gián tiếp, dùng tiếng lóng, viết sai chính tả hoặc mô tả triệu chứng không nằm trong danh sách.
2. Có thể báo động giả vì cùng một cụm từ có thể xuất hiện trong câu hỏi học thuật hoặc câu phủ định.
3. Kết quả `possible_emergency` chỉ là cảnh báo thận trọng, không phải phân loại mức độ cấp cứu.
4. Kết quả `document_lookup` không có nghĩa là tài liệu thực sự hỗ trợ câu hỏi. Luồng truy xuất vẫn phải tìm được bằng chứng trước khi trả lời.
5. Không sử dụng kết quả âm tính để trấn an người dùng hoặc kết luận rằng không có nguy cơ.
6. Trước khi phát hành rộng hơn, cần bổ sung bộ dữ liệu đánh giá đa dạng do người có chuyên môn rà soát, kiểm thử tích hợp với API, rà soát ngôn ngữ tiếng Việt và quy trình giám sát/ứng phó lỗi.

## Chạy test

Từ thư mục gốc dự án:

```powershell
python -m unittest tests.test_query_triage -v
```

## Gợi ý cho bước kế tiếp

Tích hợp triage vào `/api/ask` theo thứ tự:
1. Kiểm tra đầu vào.
2. Phát hiện và hiển thị cảnh báo nguy hiểm có tính thận trọng.
3. Không tạo lời khuyên chẩn đoán/điều trị cá nhân.
4. Với câu hỏi tra cứu, thực hiện retrieval và chỉ gọi LLM khi có nguồn phù hợp.
5. Trả câu trả lời có nguồn và thể hiện rõ hạn chế.
6. Viết kiểm thử API cho từng nhánh và giữ chế độ chạy cục bộ.

Không mở ứng dụng này thành dịch vụ công khai hoặc dùng cho quyết định chăm sóc bệnh nhân chỉ dựa trên bộ lọc từ khóa này.
