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

def normalize_county_name(name):
    """統一處理縣市名稱，將「台」統一轉換為「臺」，並處理縣市轉換"""
    if not name:
        return name
    
    # 處理台/臺的轉換
    name = name.replace('台', '臺')
    
    # 處理特殊的縣市轉換（因行政區劃調整）
    county_city_mapping = {
        '桃園縣': '桃園市',
        '臺北縣': '新北市',
        '台北縣': '新北市'
    }
    
    return county_city_mapping.get(name, name)

def get_dominant_language(lang_data, exclude_mandarin=False):
    """獲取使用比例最高的語言，可選擇是否排除華語"""
    if not lang_data:
        return None
    
    # 創建要比較的語言數據
    data_to_compare = {}
    for lang, value in lang_data.items():
        if exclude_mandarin and lang == "華語":
            continue
        data_to_compare[lang] = value
    
    if not data_to_compare:
        return None
        
    return max(data_to_compare.items(), key=lambda x: x[1])

def create_popup_content(area_name, lang_data, exclude_mandarin=False):
    """創建彈窗內容，可以選擇是否排除華語數據"""
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
        if exclude_mandarin and lang == "華語":
            continue
            
        # 根據語言類型設定進度條顏色
        color_map = {
            '華語': '#FF6B6B',
            '閩南語': '#4ECB71',
            '客家話': '#6B8EFF',
            '原住民語': '#FFD93D'
        }
        bar_color = color_map.get(lang, '#4188e0')
            
        content += f'''
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                    <span style="font-weight: bold; color: {bar_color}">{lang}</span>
                    <span>{percentage}%</span>
                </div>
                <div style="background-color: #f0f0f0; border-radius: 4px; height: 20px; overflow: hidden;">
                    <div style="width: {percentage}%; height: 100%; background-color: {bar_color};"></div>
                </div>
            </div>
        '''
    content += '</div></div>'
    return content

def create_style_function(exclude_mandarin=False):
    """創建樣式函數，可以設置是否排除華語"""
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
            dominant = get_dominant_language(lang_data, exclude_mandarin)
            if dominant:
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
    
    return style_function

def highlight_function(feature):
    """定義滑鼠懸停時的樣式"""
    return {
        'fillColor': "#43484A",
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.7
    }

def create_language_layers(m, taiwan_geojson, exclude_mandarin=False):
    """創建地圖圖層，根據是否排除華語來顯示數據"""
    layer = folium.FeatureGroup(name='語言分布' + ('（排除華語）' if exclude_mandarin else ''))
    
    style_func = create_style_function(exclude_mandarin)
    
    for feature in taiwan_geojson['features']:
        county_name = feature['properties']['COUNTYNAME']
        normalized_name = normalize_county_name(county_name)
        display_name = normalized_name
        
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
                display_name = name
                break
        
        if lang_data:
            popup_content = create_popup_content(display_name, lang_data, exclude_mandarin)
            folium.GeoJson(
                feature,
                name=county_name,
                style_function=style_func,
                highlight_function=highlight_function,
                popup=folium.Popup(popup_content, max_width=300)
            ).add_to(layer)
    
    return layer

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
    
    # 默認只添加包含華語的圖層
    normal_layer = create_language_layers(m, taiwan_geojson, False)
    normal_layer.add_to(m)
    
    # 添加自定義的單選按鈕控制
    toggle_html = '''
    <div id="language-toggle" style="position: fixed; 
                top: 10px; right: 10px; 
                z-index: 1000;
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                font-family: Arial, sans-serif;">
        <div style="font-weight: bold; margin-bottom: 12px; color: #333; font-size: 14px;">
            語言顯示模式
        </div>
        <label style="display: block; margin-bottom: 10px; cursor: pointer; font-size: 13px;">
            <input type="radio" name="language_mode" value="normal" checked 
                   style="margin-right: 8px; transform: scale(1.2);">
            <span style="color: #333;">包含華語</span>
        </label>
        <label style="display: block; cursor: pointer; font-size: 13px;">
            <input type="radio" name="language_mode" value="exclude" 
                   style="margin-right: 8px; transform: scale(1.2);">
            <span style="color: #333;">排除華語</span>
        </label>
    </div>
    
    <script>
        // 等待地圖完全載入
        document.addEventListener('DOMContentLoaded', function() {
            // 獲取地圖實例
            var mapObj = window[Object.keys(window).find(key => key.startsWith('map_'))];
            
            // 預先創建兩種模式的GeoJSON數據
            var normalData = ''' + json.dumps(taiwan_geojson) + ''';
            var excludeData = ''' + json.dumps(taiwan_geojson) + ''';
            var languageData = ''' + json.dumps(language_data) + ''';
            
            // 當前顯示的圖層
            var currentLayers = [];
            
            // 縣市名稱標準化函數
            function normalizeCountyName(name) {
                if (!name) return name;
                name = name.replace(/台/g, '臺');
                var mapping = {
                    '桃園縣': '桃園市',
                    '臺北縣': '新北市',
                    '台北縣': '新北市'
                };
                return mapping[name] || name;
            }
            
            // 獲取主要語言
            function getDominantLanguage(langData, excludeMandarin) {
                if (!langData) return null;
                var dataToCompare = {};
                for (var lang in langData) {
                    if (excludeMandarin && lang === "華語") continue;
                    dataToCompare[lang] = langData[lang];
                }
                if (Object.keys(dataToCompare).length === 0) return null;
                
                var maxLang = null;
                var maxValue = -1;
                for (var lang in dataToCompare) {
                    if (dataToCompare[lang] > maxValue) {
                        maxValue = dataToCompare[lang];
                        maxLang = lang;
                    }
                }
                return maxLang ? [maxLang, maxValue] : null;
            }
            
            // 創建彈窗內容
            function createPopupContent(areaName, langData, excludeMandarin) {
                if (!langData) return "<h4>" + areaName + "</h4>暫無語言數據";
                
                var content = '<div style="min-width: 300px"><h4 style="text-align: center">' + 
                             areaName + '語言使用比例</h4><div style="padding: 10px;">';
                
                var sortedLangs = Object.keys(langData).map(function(lang) {
                    return [lang, langData[lang]];
                }).sort(function(a, b) { return b[1] - a[1]; });
                
                var colorMap = {
                    '華語': '#FF6B6B',
                    '閩南語': '#4ECB71', 
                    '客家話': '#6B8EFF',
                    '原住民語': '#FFD93D'
                };
                
                for (var i = 0; i < sortedLangs.length; i++) {
                    var lang = sortedLangs[i][0];
                    var percentage = sortedLangs[i][1];
                    if (excludeMandarin && lang === "華語") continue;
                    
                    var barColor = colorMap[lang] || '#4188e0';
                    content += '<div style="margin: 10px 0;">' +
                              '<div style="display: flex; justify-content: space-between; margin-bottom: 2px;">' +
                              '<span style="font-weight: bold; color: ' + barColor + '">' + lang + '</span>' +
                              '<span>' + percentage + '%</span></div>' +
                              '<div style="background-color: #f0f0f0; border-radius: 4px; height: 20px; overflow: hidden;">' +
                              '<div style="width: ' + percentage + '%; height: 100%; background-color: ' + barColor + ';"></div>' +
                              '</div></div>';
                }
                content += '</div></div>';
                return content;
            }
            
            // 獲取樣式
            function getStyle(feature, excludeMandarin) {
                var countyName = feature.properties.COUNTYNAME;
                var normalizedName = normalizeCountyName(countyName);
                
                var possibleNames = [
                    normalizedName,
                    countyName,
                    normalizedName.replace('縣', '市'),
                    countyName.replace('縣', '市')
                ];
                
                var langData = null;
                for (var i = 0; i < possibleNames.length; i++) {
                    if (languageData[possibleNames[i]]) {
                        langData = languageData[possibleNames[i]];
                        break;
                    }
                }
                
                if (langData) {
                    var dominant = getDominantLanguage(langData, excludeMandarin);
                    if (dominant) {
                        var colorMap = {
                            '華語': '#FF6B6B',
                            '閩南語': '#4ECB71',
                            '客家話': '#6B8EFF', 
                            '原住民語': '#FFD93D'
                        };
                        return {
                            fillColor: colorMap[dominant[0]] || '#cccccc',
                            color: 'black',
                            weight: 1,
                            fillOpacity: 0.7
                        };
                    }
                }
                
                return {
                    fillColor: '#cccccc',
                    color: 'black', 
                    weight: 1,
                    fillOpacity: 0.3
                };
            }
            
            // 清除當前圖層
            function clearCurrentLayers() {
                currentLayers.forEach(function(layer) {
                    mapObj.removeLayer(layer);
                });
                currentLayers = [];
            }
            
            // 添加圖層
            function addLanguageLayers(excludeMandarin) {
                clearCurrentLayers();
                
                normalData.features.forEach(function(feature) {
                    var countyName = feature.properties.COUNTYNAME;
                    var normalizedName = normalizeCountyName(countyName);
                    
                    var possibleNames = [
                        normalizedName,
                        countyName,
                        normalizedName.replace('縣', '市'),
                        countyName.replace('縣', '市')
                    ];
                    
                    var langData = null;
                    var displayName = normalizedName;
                    for (var i = 0; i < possibleNames.length; i++) {
                        if (languageData[possibleNames[i]]) {
                            langData = languageData[possibleNames[i]];
                            displayName = possibleNames[i];
                            break;
                        }
                    }
                    
                    if (langData) {
                        var style = getStyle(feature, excludeMandarin);
                        var popupContent = createPopupContent(displayName, langData, excludeMandarin);
                        
                        var layer = L.geoJson(feature, {
                            style: style,
                            onEachFeature: function(feature, layer) {
                                layer.bindPopup(popupContent, {maxWidth: 300});
                                layer.on('mouseover', function() {
                                    this.setStyle({
                                        fillColor: "#43484A",
                                        color: 'black',
                                        weight: 2,
                                        fillOpacity: 0.7
                                    });
                                });
                                layer.on('mouseout', function() {
                                    this.setStyle(style);
                                });
                            }
                        }).addTo(mapObj);
                        
                        currentLayers.push(layer);
                    }
                });
            }
            
            // 初始化顯示正常模式
            addLanguageLayers(false);
            
            // 監聽單選按鈕變化
            document.querySelectorAll('input[name="language_mode"]').forEach(function(radio) {
                radio.addEventListener('change', function() {
                    var excludeMandarin = this.value === 'exclude';
                    addLanguageLayers(excludeMandarin);
                });
            });
        });
    </script>
    '''
    
    m.get_root().html.add_child(folium.Element(toggle_html))
    
    # 添加圖例
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color: white;
                padding: 10px;
                opacity: 0.9;">
        <p style="margin-bottom: 5px;"><b>台灣語言分布地圖</b></p>
        <p style="margin: 5px 0;"><b>顏色代表主要使用語言：</b></p>
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
        <p style="margin: 5px 0;"><b>使用說明：</b></p>
        <div style="font-size: 12px; margin-top: 5px; color: #666;">
            1. 右上角可切換是否包含華語<br>
            2. 點擊區域查看詳細語言比例<br>
            3. 進度條顏色對應語言類型
        </div>
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