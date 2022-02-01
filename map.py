import folium
import pandas
import re
import sys
import io
from PyQt5 import QtWidgets, QtWebEngineWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    folium_map = folium.Map(
        location=[55.751624, 37.626386], zoom_start=12, zoom_control=False, control_scale=True, tiles='Stamen Terrain',
        scrollWheelZoom=False,
        dragging=False)
    places = pandas.read_excel('datasets/cinema.xlsx')
    numbers = [re.findall(r'\d+', text) for text in places['geoData']]
    coordinates = []
    for i in numbers:
        new_list = [i[2] + '.' + i[3], i[0] + '.' + i[1]]
        coordinates.append(new_list)
    names = places['CommonName']
    for coordinates, names in zip(coordinates, names):
        folium.Marker(location=[coordinates[0], coordinates[1]], popup=names,
                      icon=folium.Icon(color='blue')).add_to(folium_map)
    data = io.BytesIO()
    folium_map.save(data, close_file=False)
    window = QtWebEngineWidgets.QWebEngineView()
    window.setHtml(data.getvalue().decode())
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())

