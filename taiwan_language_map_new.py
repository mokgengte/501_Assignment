import folium
import json
import requests

def download_taiwan_geojson():
    """下載台灣縣市邊界的 GeoJSON 數據"""
    url = "https://raw.githubusercontent.com/g0v/twgeojson/master/json/twCounty2010.geo.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"無法下載台灣地理數據：{e}")
        return None

# 語言分布數據（包含臺/台的異體寫法）
language_data = {
    "臺北市": {"華語": 95, "閩南語": 75, "客家話": 13, "原住民語": 1.5},
    "台北市": {"華語": 95, "閩南語": 75, "客家話": 13, "原住民語": 1.5},
    "新北市": {"華語": 93, "閩南語": 78, "客家話": 15, "原住民語": 1.2},
    "桃園市": {"華語": 90, "閩南語": 65, "客家話": 35, "原住民語": 1.0},
    "臺中市": {"華語": 92, "閩南語": 82, "客家話": 8, "原住民語": 0.8},
    "台中市": {"華語": 92, "閩南語": 82, "客家話": 8, "原住民語": 0.8},
    "臺南市": {"華語": 88, "閩南語": 85, "客家話": 2, "原住民語": 0.5},
    "台南市": {"華語": 88, "閩南語": 85, "客家話": 2, "原住民語": 0.5},
    "高雄市": {"華語": 90, "閩南語": 83, "客家話": 4, "原住民語": 0.7},
    "基隆市": {"華語": 92, "閩南語": 80, "客家話": 3, "原住民語": 0.5},
    "新竹市": {"華語": 91, "閩南語": 60, "客家話": 40, "原住民語": 0.4},
    "新竹縣": {"華語": 85, "閩南語": 45, "客家話": 70, "原住民語": 1.2},
    "苗栗縣": {"華語": 84, "閩南語": 40, "客家話": 65, "原住民語": 1.5},
    "彰化縣": {"華語": 90, "閩南語": 88, "客家話": 2, "原住民語": 0.3},
    "南投縣": {"華語": 88, "閩南語": 80, "客家話": 3, "原住民語": 2.5},
    "雲林縣": {"華語": 87, "閩南語": 90, "客家話": 1, "原住民語": 0.4},
    "嘉義市": {"華語": 89, "閩南語": 87, "客家話": 2, "原住民語": 0.3},
    "嘉義縣": {"華語": 86, "閩南語": 89, "客家話": 1, "原住民語": 0.5},
    "屏東縣": {"華語": 87, "閩南語": 82, "客家話": 8, "原住民語": 3.5},
    "宜蘭縣": {"華語": 89, "閩南語": 84, "客家話": 2, "原住民語": 2.0},
    "花蓮縣": {"華語": 88, "閩南語": 65, "客家話": 5, "原住民語": 25.0},
    "臺東縣": {"華語": 86, "閩南語": 60, "客家話": 3, "原住民語": 35.0},
    "台東縣": {"華語": 86, "閩南語": 60, "客家話": 3, "原住民語": 35.0},
    "澎湖縣": {"華語": 89, "閩南語": 95, "客家話": 0.5, "原住民語": 0.1},
    "金門縣": {"華語": 90, "閩南語": 98, "客家話": 0.2, "原住民語": 0.1},
    "連江縣": {"華語": 95, "閩南語": 90, "客家話": 0.2, "原住民語": 0.1}
}

def create_popup_content(area_name, lang_data):
    """創建彈窗內容"""
    if not lang_data:
        return f"<h4>{area_name}</h4>暫無語言數據"

    content = f'''
    <div style="min-width: 300px">
        <h4 style="text-align: center">{area_name}語言使用比例</h4>
        <div style="padding: 10px;">
    '''
    
    # 按使用比例從高到低排序
    sorted_languages = sorted(lang_data.items(), key=lambda x: x[1], reverse=True)
    for lang, percentage in sorted_languages:
        content += f'''
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                    <span>{lang}</span>
                    <span>{percentage}%</span>
                </div>
                <div style="background-color: #f0f0f0; border-radius: 4px; height: 20px; overflow: hidden;">
                    <div style="width: {percentage}%; height: 100%; background-color: #4188e0;"></div>
                </div>
            </div>
        '''
    content += '</div></div>'
    return content

def get_dominant_language(lang_data):
    """獲取使用比例最高的語言"""
    if not lang_data:
        return None
    return max(lang_data.items(), key=lambda x: x[1])

def style_function(feature):
    """定義區域的樣式"""
    properties = feature['properties']
    county_name = properties.get('COUNTYNAME')
    
    # 使用相同的名稱匹配邏輯
    normalized_name = normalize_county_name(county_name)
    possible_names = {
        normalized_name,
        county_name,
        normalized_name.replace('縣', '市') if '縣' in normalized_name else normalized_name,
        county_name.replace('縣', '市') if '縣' in county_name else county_name
    }
    
    # 尋找匹配的語言數據
    lang_data = None
    for name in possible_names:
        if name in language_data:
            lang_data = language_data[name]
            break
    
    if lang_data:
        dominant = get_dominant_language(lang_data)
        # 根據主要語言設定顏色
        color_map = {
            '華語': '#FF6B6B',     # 紅色
            '閩南語': '#4ECB71',   # 綠色
            '客家話': '#6B8EFF',   # 藍色
            '原住民語': '#FFD93D'  # 黃色
        }
        
        return {
            'fillColor': color_map.get(dominant[0], '#cccccc'),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }
    
    return {
        'fillColor': '#cccccc',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.3
    }

def highlight_function(feature):
    """定義滑鼠懸停時的樣式"""
    return {
        'fillColor': "#43484A",
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.7
    }

def normalize_county_name(name):
    """統一處理縣市名稱，將「台」統一轉換為「臺」，並處理縣市轉換"""
    if not name:
        return name
    
    # 處理台/臺的轉換
    name = name.replace('台', '臺')
    
    # 處理特殊的縣市轉換（因行政區劃調整）
    county_city_mapping = {
        '桃園縣': '桃園市',
        '臺北縣': '新北市',  # 以防萬一也處理這個
        '台北縣': '新北市'
    }
    
    return county_city_mapping.get(name, name)

def create_language_map():
    """創建台灣語言分布地圖"""
    # 創建地圖對象，將中心點設在台灣中心位置
    m = folium.Map(
        location=[23.5, 121], 
        zoom_start=7.5,
        tiles='CartoDB positron'
    )
    
    # 下載台灣縣市邊界的 GeoJSON 數據
    taiwan_geojson = download_taiwan_geojson()
    if not taiwan_geojson:
        print("無法創建地圖：缺少地理數據")
        return None
    
    # 添加 GeoJSON 圖層到地圖，包含彈窗和樣式
    for feature in taiwan_geojson['features']:
        county_name = feature['properties']['COUNTYNAME']
        normalized_name = normalize_county_name(county_name)
        display_name = normalized_name  # 使用正規化後的名稱顯示
        
        # 嘗試不同的名稱版本來匹配語言數據
        possible_names = {
            normalized_name,
            county_name, 
            normalized_name.replace('縣', '市') if '縣' in normalized_name else normalized_name,
            county_name.replace('縣', '市') if '縣' in county_name else county_name
        }
        
        # 尋找第一個匹配的數據
        lang_data = None
        for name in possible_names:
            if name in language_data:
                lang_data = language_data[name]
                display_name = name  # 使用找到數據的名稱
                break
        
        if lang_data:
            popup_content = create_popup_content(display_name, lang_data)
            folium.GeoJson(
                feature,
                name=county_name,
                style_function=style_function,
                highlight_function=highlight_function,
                popup=folium.Popup(popup_content, max_width=300)
            ).add_to(m)

    # 添加圖例
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color: white;
                padding: 10px;
                opacity: 0.9;">
        <p style="margin-bottom: 5px;"><b>台灣主要語言分布</b></p>
        <p style="margin: 5px 0;"><b>地圖顏色代表該地區使用比例最高的語言：</b></p>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background-color: #FF6B6B; border: 1px solid black;"></span>
            <span style="margin-left: 5px;">華語</span>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background-color: #4ECB71; border: 1px solid black;"></span>
            <span style="margin-left: 5px;">閩南語</span>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background-color: #6B8EFF; border: 1px solid black;"></span>
            <span style="margin-left: 5px;">客家話</span>
        </div>
        <div style="margin: 5px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background-color: #FFD93D; border: 1px solid black;"></span>
            <span style="margin-left: 5px;">原住民語</span>
        </div>
        <hr style="margin: 10px 0;">
        <p style="margin: 5px 0; text-align: center;"><b>點擊各縣市查看詳細語言使用比例</b></p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

if __name__ == '__main__':
    # 創建並保存地圖
    m = create_language_map()
    if m:
        m.save('taiwan_language_map.html')
        print("地圖已保存為 'taiwan_language_map.html'")
    else:
        print("地圖創建失敗")