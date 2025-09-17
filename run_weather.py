from get_local import get_location_keys
from get_hourly import get_hourly_forecast_by_key
from get_daily import get_daily_forecast_by_key
from get_air import get_air_quality_by_key
from get_weather import get_weather_by_key
from get_all_health import crawl_all_health_activities_by_key

def group_health_activities(items):
    groups = {
        'allergy_health': [],
        'outdoor': [],
        'travel': [],
        'home_garden': [],
        'pests': [],
        'allergy_other': [],
        'entertainment': [],
        'other': []
    }
    for item in items:
        slug = (item.get('slug') or '').lower()
        cat = item.get('lifestyleCategory')
        t = item.get('type')
        if cat == 1 or slug in ['asthma','flu','sinus','migraine','arthritis','common-cold'] or t in [21, 23, 25, 26, 27, 30, 18]:
            groups['allergy_health'].append(item)
        elif cat == 2 or slug in ['running','hiking','biking','golf','sun-sand','astronomy','fishing']:
            groups['outdoor'].append(item)
        elif cat == 3 or slug in ['driving','air-travel']:
            groups['travel'].append(item)
        elif cat == 4 or slug in ['lawn-mowing','composting']:
            groups['home_garden'].append(item)
        elif cat == 5 or 'pest' in slug or 'mosquito' in slug:
            groups['pests'].append(item)
        elif slug in ['dust-dander','pollen']:
            groups['allergy_other'].append(item)
        elif slug in ['outdoor-entertaining','entertainment']:
            groups['entertainment'].append(item)
        else:
            groups['other'].append(item)
    return groups

def main():
    keyword = input("Nhập tên địa điểm: ")
    results = get_location_keys(keyword)
    if results:
        print("Các địa điểm tìm được:")
        for key, name, long_name in results:
            print(f"Key: {key} | Tên: {name} | Đầy đủ: {long_name}")
        key = input("Nhập key địa điểm để lấy thời tiết: ")
        weather = get_weather_by_key(key)
        if weather:
            print(f"\n--- Thời tiết hiện tại ---")
            for k, v in weather.items():
                print(f"{k}: {v}")
            print(f"\n--- Dự báo theo giờ ---")
            hourly = get_hourly_forecast_by_key(key)
            for h in hourly:
                print(h)
            print(f"\n--- Dự báo hàng ngày ---")
            daily = get_daily_forecast_by_key(key)
            for d in daily:
                print(d)
            print(f"\n--- Chất lượng không khí ---")
            air_quality = get_air_quality_by_key(key)
            print(air_quality)
            # Phân nhóm health activities chi tiết từ dữ liệu crawl động
            groups = crawl_all_health_activities_by_key(key)
            all_items = []
            for items in groups.values():
                all_items.extend(items)
            cats = group_health_activities(all_items)
            print(f"\n--- Dị ứng/Sức khỏe ---")
            for a in cats['allergy_health']:
                print(a)
            print(f"\n--- Hoạt động ngoài trời ---")
            for o in cats['outdoor']:
                print(o)
            print(f"\n--- Đi lại/Đi làm/Du lịch ---")
            for t in cats['travel']:
                print(t)
            print(f"\n--- Nhà & vườn ---")
            for h in cats['home_garden']:
                print(h)
            print(f"\n--- Sâu bọ/Côn trùng/Muỗi ---")
            for p in cats['pests']:
                print(p)
            print(f"\n--- Dị ứng khác (bụi phấn, khói bụi) ---")
            for al in cats['allergy_other']:
                print(al)
            print(f"\n--- Giải trí ---")
            for e in cats['entertainment']:
                print(e)
            print(f"\n--- Nhóm khác ---")
            for x in cats['other']:
                print(x)
        else:
            print("Không lấy được dữ liệu thời tiết.")
    else:
        print("Không tìm thấy địa điểm.")

if __name__ == "__main__":
    main()
