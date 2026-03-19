# Hướng dẫn thiết lập Đăng nhập Google (OAuth 2.0) cho ITBot

Để tính năng đăng nhập Google trên ITBot hoạt động thật sự trong môi trường local, bạn cần làm theo các bước sau để lấy Client ID và Client Secret từ Google.

## Bước 1: Tạo dự án trên Google Cloud
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Đăng nhập bằng tài khoản Google của bạn.
3. Ở góc trên cùng bên trái (cạnh logo Google Cloud), bấm vào **Select a project** (Chọn dự án) > **New Project** (Dự án mới).
4. Đặt tên dự án (ví dụ: `ITBot-Login`) và bấm **Create** (Tạo).

## Bước 2: Cấu hình màn hình đồng ý (OAuth consent screen)
1. Thư mục bên trái, chọn **APIs & Services** (API và Dịch vụ) > **OAuth consent screen** (Màn hình đồng ý OAuth).
2. Chọn loại người dùng là **External** (Bên ngoài) và bấm **Create**.
3. Điền thông tin cơ bản:
   - *App name:* ITBot
   - *User support email:* (Email của bạn)
   - *Developer contact information:* (Email của bạn)
4. Bấm **Save and Continue** cho đến phần kết thúc (Kéo xuống dưới, bỏ qua phần Scopes và Test users cho ứng dụng nội bộ nhỏ).
5. Trở lại trang OAuth consent screen, đảm bảo tráng thái là "Testing" hoặc bạn có thể "Publish App" nếu không muốn bị giới hạn user.

## Bước 3: Tạo Credentials (Thông tin xác thực)
1. Chọn tab **Credentials** (Thông tin xác thực) ở menu trái.
2. Bấm nút **+ CREATE CREDENTIALS** (TẠO THÔNG TIN XÁC THỰC) ở trên cùng > Chọn **OAuth client ID**.
3. Cấu hình Client ID:
   - *Application type (Loại ứng dụng):* Chọn **Web application** (Ứng dụng web).
   - *Name:* ITBot Web Client
   - *Authorized JavaScript origins (Nguồn JavaScript được ủy quyền):* Bấm `+ ADD URI` và điền: `http://localhost:8501`
   - *Authorized redirect URIs (URI chuyển hướng được ủy quyền):* Bấm `+ ADD URI` và điền: `http://localhost:8501/` *(Lưu ý: phải có dấu `/` ở cuối tuỳ thuộc quy tắc Streamlit auth nhưng thường là trùng gốc)*
4. Bấm **Create** (Tạo).

## Bước 4: Sao chép ID và Secret vào dự án
Sau khi tạo xong, Google sẽ hiển thị một bảng popup chứa:
- **Client ID** 
- **Client Secret**

Bạn hãy copy 2 chuỗi này, mở file `.env` trong VSCode của dự án và dán vào:

```env
GOOGLE_CLIENT_ID=dán_client_id_của_bạn_vào_đây
GOOGLE_CLIENT_SECRET=dán_client_secret_của_bạn_vào_đây
REDIRECT_URI=http://localhost:8501
```

## Bước 5: Khởi động lại ứng dụng
Gõ lệnh để tắt ứng dụng cũ (nhấn `Ctrl + C` trên terminal), sau đó chạy lại:
```bash
streamlit run app.py
```

Bây giờ nút đăng nhập Google trong ITBot đã hoạt động chính thức! Các phiên trò chuyện sẽ được tự động lưu vào database theo địa chỉ Gmail của từng người.
