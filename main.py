import geopandas as gpd
import matplotlib.pyplot as plt
df = gpd.read_file('../Shape File/studyarea.shp')
print(df.shape)
print(df.head())
df.plot()
plt.show()