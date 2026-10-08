# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Trần Gia Khánh |
| MSSV | 2A202602689 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/khanhtg205/K4-L3-DAY21-TranGiaKhanh-2A202602689-CI-CD-for-AI-Systems |
| Ngày nộp | 08/10/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Lần chạy thứ 3 đạt `f1_score` cao nhất (0.7149), vượt qua ngưỡng chất lượng tối thiểu 0.65 của bài lab để kích hoạt bước triển khai. Đáng chú ý, lần chạy 1 có `accuracy` cao hơn lần chạy 3 (0.8780 so với 0.8740), nhưng `f1_score` của lớp thiểu số lại thấp hơn. Điều này khẳng định accuracy không phản ánh trọn vẹn năng lực nhận diện lớp thu nhập cao. Ngoài ra, việc tăng số lượng cây kết hợp độ sâu cây giúp mô hình bao quát tốt các tương tác phi tuyến tính trong tập dữ liệu điều tra dân số.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Census Income có sự mất cân bằng lớp nghiêm trọng khi chỉ có khoảng 24,8% mẫu thuộc lớp thu nhập cao (>50K USD/năm). Một mô hình thô sơ luôn dự đoán nhãn 0 (thu nhập thấp) cho mọi trường hợp vẫn dễ dàng đạt `accuracy = 0.752`, nhưng mô hình đó hoàn toàn vô dụng trong thực tế vì bỏ sót toàn bộ khách hàng thu nhập cao (`f1_score = 0.000`).

Chỉ số `f1_score` của lớp dương là trung bình điều hòa giữa Precision (độ chuẩn xác) và Recall (độ bao phủ) trên nhóm người thu nhập cao. Khi đánh giá, không sử dụng `average="weighted"` hay `"macro"` vì trọng số từ lớp đa số sẽ kéo chỉ số tổng thể lên cao, làm mất đi tính nghiêm ngặt của chốt chặn Quality Gate.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Lỗi 403 Forbidden khi DVC push lên Google Cloud Storage | Service Account chưa được cấp quyền `Storage Object Admin` trực tiếp trên bucket `khanh_bucket`. | Cấp quyền `Storage Object Admin` cho email của Service Account trên Google Cloud Console IAM. |
| Service API bị crash khi load model unpickle trên VM | Phiên bản scikit-learn trên VM chạy Python 3.13 khác biệt cấu trúc nội bộ Cython so với model đã lưu. | Thêm ánh xạ tương thích module `_loss` trong `src/serve.py` và đồng bộ `scikit-learn==1.6.1`. |
| Lệnh `curl` trên PowerShell Windows báo lỗi cú pháp | PowerShell mặc định gán alias `curl` sang `Invoke-WebRequest` nên sai format header JSON. | Sử dụng tường minh chương trình `curl.exe` khi gửi request kiểm thử API. |

---

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2`) | 0.7354 | 0.8820 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu dữ liệu mới ở Bước 3 (nâng tổng kích thước tập huấn luyện lên 44.722 mẫu), cả `f1_score` (tăng từ 0.7149 lên 0.7354) và `accuracy` (tăng từ 0.8740 lên 0.8820) đều được cải thiện rõ rệt. Việc tăng gấp đôi lượng dữ liệu cùng phân phối đã giúp cây quyết định phân tách tốt hơn các vùng biên, giảm thiểu đáng kể lỗi phân loại sai trên tập holdout.
