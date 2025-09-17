# AccuWeather

Component tích hợp thông tin thời tiết và chất lượng không khí Việt Nam cho Home Assistant, sử dụng nguồn dữ liệu từ AccuWeather.

## Tính năng

- Hiển thị thông tin thời tiết hiện tại: nhiệt độ, độ ẩm, điều kiện thời tiết, tốc độ gió, điểm sương, chỉ số UV...
- Dự báo thời tiết theo ngày (5 ngày tới)
- Dự báo thời tiết theo giờ (48 giờ tới)
- Hiển thị thông tin chất lượng không khí: AQI, PM2.5, PM10, O3, SO2, NO2, CO
- Hỗ trợ đầy đủ 63 tỉnh thành và hầu hết quận/huyện tại Việt Nam
- Phân loại theo 8 vùng miền địa lý của Việt Nam
- Tùy chọn cấu hình thời gian cập nhật dữ liệu (5-180 phút)
- Hỗ trợ đa ngôn ngữ cho giao diện cấu hình

## Cài đặt

### Cài đặt qua HACS (khuyến nghị)

#### Phương pháp 1: Nút "Thêm vào HACS" (đơn giản nhất)

[![Thêm vào HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=smarthomeblack&repository=accuweather&category=integration)

1. Nhấp vào nút "Thêm vào HACS" ở trên (hoạt động khi bạn đã đăng nhập vào Home Assistant).
2. Xác nhận thêm kho lưu trữ vào HACS.
3. Tìm và cài đặt "accuweather" từ menu HACS > Tích hợp.
4. Khởi động lại Home Assistant.
5. Thêm tích hợp: Cài đặt > Thiết bị & Dịch vụ > Thêm tích hợp > accuweather.
6. Chọn tỉnh/thành phố và quận/huyện mà bạn muốn hiển thị thông tin thời tiết.
7. Tùy chọn cấu hình thời gian cập nhật (mặc định là 10 phút).


### Cài đặt thủ công

1. Tải xuống [bản phát hành mới nhất](https://github.com/smarthomeblack/accuweather/releases) hoặc sao chép nội dung repository.
2. Sao chép thư mục `custom_components/accuweather` vào thư mục `custom_components` trong cài đặt Home Assistant của bạn.
3. Khởi động lại Home Assistant.
4. Thêm tích hợp: Cài đặt > Thiết bị & Dịch vụ > Thêm tích hợp > accuweather.
5. Chọn tỉnh/thành phố và quận/huyện mà bạn muốn hiển thị thông tin thời tiết.
6. Tùy chọn cấu hình thời gian cập nhật (mặc định là 10 phút).

## Cấu hình

Bạn có thể thay đổi cấu hình của tích hợp bất cứ lúc nào:

1. Đi tới Cài đặt > Thiết bị & Dịch vụ
2. Tìm tích hợp Weather Vn và nhấn vào Tùy chọn
3. Cấu hình:
   - Chọn tỉnh/thành phố
   - Cài đặt thời gian cập nhật (từ 5 đến 60 phút)
   - Chọn quận/huyện

## Sử dụng

Sau khi cài đặt, các entity sau sẽ được tạo ra:

- Entity `weather.ten_quan_huyen`: Thông tin thời tiết hiện tại và dự báo
- Entity `sensor.ten_quan_huyen_air_quality`: Chỉ số chất lượng không khí tổng hợp
- Các entity cảm biến chất lượng không khí riêng lẻ: pm2.5, pm10, o3, no2, co, so2,...

Bạn có thể thêm thẻ Weather và các cảm biến vào dashboard để hiển thị thông tin.

## Các tỉnh/thành phố hỗ trợ

Tích hợp hỗ trợ tất cả 63 tỉnh thành của Việt Nam, được phân loại theo 8 vùng miền:

- Đông Bắc Bộ: Hà Giang, Cao Bằng, Bắc Kạn, Tuyên Quang, Thái Nguyên,...
- Tây Bắc Bộ: Lào Cai, Điện Biên, Lai Châu, Sơn La, Yên Bái,...
- Đồng bằng Sông Hồng: Hà Nội, Hải Phòng, Hải Dương, Hưng Yên,...
- Bắc Trung Bộ: Thanh Hóa, Nghệ An, Hà Tĩnh, Quảng Bình,...
- Nam Trung Bộ: Đà Nẵng, Quảng Nam, Quảng Ngãi, Bình Định,...
- Tây Nguyên: Kon Tum, Gia Lai, Đắk Lắk, Đắk Nông, Lâm Đồng
- Đông Nam Bộ: TP. Hồ Chí Minh, Bà Rịa - Vũng Tàu, Bình Dương,...
- Đồng bằng Sông Cửu Long: Cần Thơ, Long An, Tiền Giang, Bến Tre,...

## Quận/huyện hỗ trợ

Tích hợp hỗ trợ hầu hết các quận/huyện của 63 tỉnh thành, bao gồm cả các khu vực đặc biệt như biển, vùng núi và các đảo.

## Chú ý

- Dữ liệu được cập nhật tự động theo thời gian cấu hình (mặc định là 10 phút)
- Độ chính xác của dữ liệu phụ thuộc vào nguồn cung cấp (accuweather)
- Một số khu vực có thể không có đủ dữ liệu chi tiết


## Phát triển trong tương lai

- Thêm hỗ trợ cho các khu vực du lịch đặc biệt
- Tích hợp dữ liệu cảnh báo thiên tai
- Cải thiện giao diện và hiển thị dữ liệu
- Tùy chọn hiển thị đơn vị đo (metric/imperial)

## Đóng góp

Mọi đóng góp đều được hoan nghênh. Vui lòng tạo issues hoặc pull requests trên [GitHub](https://github.com/smarthomeblack/accuweather).