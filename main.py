import io
import sys
import time

import folium
import overpy

from time import time, sleep
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from folium import plugins
from KDtree import KDimensionalTree
from interactive_map import Ui_MainWindow
from geopy import distance


class MapThread(QThread):
    """
    Thread that finds closest point on a map
    """

    def __init__(self, main):
        super(MapThread, self).__init__()
        self.main = main

    def run(self):
        longitude = self.main.ui.longitude_spinbox.value()
        latitude = self.main.ui.latitude_spinbox.value()
        search_radius = self.main.ui.radius_spinbox.value()
        request = f"""[out:json];
                             (node["amenity"={self.main.category}]
                             (around:{search_radius}, {latitude}, {longitude});
                             );
                             out center;"""

        api = overpy.Overpass()
        try:
            start = time()
            self.main.search_result = api.query(request)
            end = time()
            print("Request time -", end - start)
        except overpy.exception.OverpassTooManyRequests:
            return
        points = []
        benchmark = [latitude, longitude]
        start = time()
        for node in self.main.search_result.nodes:
            points.append([float(node.lat), float(node.lon)])
        if len(points) > 1:
            kd = KDimensionalTree()
            tree = kd.build(points)
            closest_point = kd.find_closest(tree, benchmark)
            self.show_result(benchmark, closest_point, search_radius)
            self.main.ui.distance_label.setText("Distance to closest point: " +
                                                str(int(distance.distance(tuple(benchmark),
                                                                          tuple(closest_point)).m))
                                                + "m.")
        elif len(points) == 1:
            self.show_result(benchmark, points[0], search_radius)
            self.main.ui.distance_label.setText("Distance to closest point: " +
                                                str(int(distance.distance(tuple(benchmark),
                                                                          tuple(points[0])).m))
                                                + "m.")
        else:
            self.show_result(benchmark, None, search_radius)
            self.main.ui.distance_label.setText("No points found.")
        end = time()
        print("Map refresh time -\n", end - start)

    def show_result(self, benchmark, closest_point, search_radius):
        """
        Method builds a k-d tree by given list of points

        :param benchmark: Benchmark point [x,y]
        :param closest_point: Closest to benchmark point [x,y]
        :param search_radius: Radius of search zone
        :type search_radius: int
        :return: Built k-d tree
        :rtype: dict
        """
        icons = {'cafe': 'cutlery',
                 'parking': 'car',
                 'bank': 'money',
                 'hospital': 'heartbeat',
                 'fuel': 'battery-three-quarters'}
        self.main.ui.new_map = folium.Map(
            location=benchmark, tiles="OpenStreetMap", zoom_start=13
        )
        folium.Marker(location=benchmark, icon=folium.Icon(color='green',
                                                           icon='male',
                                                           prefix='fa')).add_to(self.main.ui.new_map)
        if closest_point:
            closest_node = None
            for node in self.main.search_result.nodes:
                if float(node.lat) == closest_point[0] \
                        and float(node.lon) == closest_point[1]:
                    closest_node = node
            point_name = ""
            if 'name' in closest_node.tags.keys():
                point_name = closest_node.tags['name']
            folium.Marker(location=closest_point, popup='Closest Point' +
                                                        '\nLatitude:' + str(closest_point[0]) +
                                                        '\nLongitude:' + str(closest_point[1]) +
                                                        '\n' + point_name,
                          icon=folium.Icon(color='red',
                                           icon=icons[self.main.category],
                                           prefix='fa')).add_to(self.main.ui.new_map)
            folium.plugins.AntPath([benchmark, closest_point]).add_to(self.main.ui.new_map)
        folium.Circle(location=benchmark, radius=search_radius).add_to(self.main.ui.new_map)
        self.main.data = io.BytesIO()
        self.main.ui.new_map.save(self.main.data, close_file=False)


class InteractiveMap(QtWidgets.QMainWindow):
    """
    A PyQt5 main window class
    """

    def __init__(self):
        super(InteractiveMap, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.category = "fuel"
        self.data = None
        self.search_result = None
        self.map_thread = None
        self.ui.radius_slider.valueChanged.connect(self.change_radius)
        self.ui.find_button.clicked.connect(self.find_nearest)
        self.ui.find_bank.clicked.connect(self.set_category)
        self.ui.find_fuel.clicked.connect(self.set_category)
        self.ui.find_cafe.clicked.connect(self.set_category)
        self.ui.find_parking.clicked.connect(self.set_category)
        self.ui.find_hospital.clicked.connect(self.set_category)

    def set_category(self):
        """
        Sets the selected category
        """
        if self.ui.find_hospital.isChecked():
            self.category = "hospital"
        elif self.ui.find_bank.isChecked():
            self.category = "bank"
        elif self.ui.find_fuel.isChecked():
            self.category = "fuel"
        elif self.ui.find_parking.isChecked():
            self.category = "parking"
        elif self.ui.find_cafe.isChecked():
            self.category = "cafe"

    def change_radius(self, value):
        """
        Slider and spinbox binding
        """
        self.ui.radius_spinbox.setValue(value)

    def find_nearest(self):
        """
        Starts a QThread
        """
        self.ui.find_button.setEnabled(False)
        self.map_thread = MapThread(main=self)
        self.map_thread.start()
        self.ui.radius_slider.setValue(self.ui.radius_spinbox.value())
        self.map_thread.finished.connect(self.update_map)

    def update_map(self):
        """
        Updates HTML map
        """
        decoded = self.data.getvalue().decode()
        self.ui.widget.setHtml(decoded)
        cooldown = Thread(target=self.enable_button)
        cooldown.start()

    def enable_button(self):
        """
        Enables button after 10 seconds of waiting
        """
        sleep(10)
        self.ui.find_button.setEnabled(True)


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = InteractiveMap()
    window.show()
    sys.exit(App.exec())
