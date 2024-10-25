import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from matplotlib.path import Path

class ArgoDataProcessor:
    def __init__(self, filename):
        self.dataset = xr.open_dataset(filename)
        self.filtered_indices = None

    def find_profiles_near_line(self, lon0, lat0, bbox, distance=75):
        lon_km, lat_km = ll2km(self.dataset.LONGITUDE.values, self.dataset.LATITUDE.values, bbox)
        lon_r, lat_r = rotate_point_corr(lon_km, lat_km)

        I = np.where(lat_km.ravel() >= -60)
        J = np.where(lon_km.ravel() >= 0)
        i75 = np.where((lat_r >= -distance) & (lat_r <= distance))
        K = np.intersect1d(i75, I, J)

        bool_array = np.zeros_like(self.dataset.LONGITUDE.values, dtype=bool)
        bool_array[K] = True
        self.filtered_indices = bool_array

    def apply_filter(self):
        if self.filtered_indices is not None:
            self.dataset = self.dataset.isel(N_PROF=self.filtered_indices)

class BathymetryPlotter:
    def __init__(self, topo_filename):
        topo_data = np.load(topo_filename)
        self.lon_topo = topo_data['lon_topo']
        self.lat_topo = topo_data['lat_topo']
        self.bathy = topo_data['bathy']

    def plot_bathymetry_and_argo(self, argo_dataset):
        ranges = np.arange(0, 5400, 500)
        fig, ax = plt.subplots(figsize=(6, 7))
        plt.contour(self.lon_topo, self.lat_topo, self.bathy, ranges, colors='grey', linewidths=1)
        plt.contour(self.lon_topo, self.lat_topo, self.bathy, [0], colors='k', linewidths=1)
        plt.contour(self.lon_topo, self.lat_topo, self.bathy, [1000], colors='b', linewidths=1)

        plt.plot(argo_dataset.LONGITUDE.values, argo_dataset.LATITUDE.values, '.r')
        plt.plot(lon_line_A, lat_line_A, 'k')
        plt.plot(lon_line_1, lat_line_1, ':k')
        plt.plot(lon_line_0, lat_line_0, ':k')

        contour_path = Path(plt.gca().collections[2].get_paths()[1].vertices)
        contour_collection = plt.gca().collections[2]
        contour_paths = [path for path in contour_collection.get_paths()]

        points_within_contour = np.zeros(len(argo_dataset.LONGITUDE.values), dtype=bool)
        for path in contour_paths:
            contour_path = Path(path.vertices)
            points_within_contour |= contour_path.contains_points(np.column_stack((argo_dataset.LONGITUDE.values, argo_dataset.LATITUDE.values)))

        plt.plot(argo_dataset.LONGITUDE.values[points_within_contour], argo_dataset.LATITUDE.values[points_within_contour], 'og', markersize=3)
        plt.show()

        bool_array_2 = np.zeros_like(argo_dataset.LONGITUDE.values, dtype=bool)
        bool_array_2[points_within_contour] = True
        return bool_array_2
